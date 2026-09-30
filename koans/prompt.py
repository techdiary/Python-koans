"""Ask for each blank in the failing test and write the answers into the working lesson."""

from __future__ import annotations

import ast
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NoReturn, TextIO

from cleo.io.outputs.output import Type
from cleo.io.outputs.stream_output import StreamOutput

from koans.runner import ROOT, StopKind

if TYPE_CHECKING:
    from typing import Never

SlotKind = Literal["value", "because"]


@dataclass(frozen=True)
class _Slot:
    kind: SlotKind
    start: int
    end: int
    lineno: int


def _assert_never(kind: Never) -> NoReturn:
    raise AssertionError(kind)


def is_terminal(stdin: TextIO, stdout: TextIO) -> bool:
    """True only when both streams are a terminal. Pipes stay non-interactive."""
    return _isatty(stdin) and _isatty(stdout)


def _isatty(stream: TextIO) -> bool:
    try:
        return bool(stream.isatty())
    except (AttributeError, OSError, ValueError):
        return False


def offer_fill(
    path: Path,
    method_name: str,
    *,
    kind: StopKind,
    failing_lineno: int | None,
    hint: str | None,
    stdin: TextIO,
    output: StreamOutput,
) -> bool:
    """Print the method and prompt for each blank. Return True when the file changed.

    An empty answer leaves the file untouched. Pristine copies are never written.
    """
    _refuse_pristine(path)
    source = path.read_text(encoding="utf-8")
    shown = _method_text(source, method_name)
    slots = _slots(source, method_name, kind, failing_lineno)
    _show_method(output, path, shown, hint)
    if shown is None or not slots:
        return False
    answers = _ask_all(slots, stdin, output)
    if answers is None:
        return False
    updated = _apply(source, slots, answers)
    if updated == source:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def _refuse_pristine(path: Path) -> None:
    parts = path.parts + path.resolve().parts
    if "pristine" in parts:
        raise ValueError(f"refusing to edit pristine copy {path}")


def _show_method(
    output: StreamOutput,
    path: Path,
    shown: tuple[int, str] | None,
    hint: str | None,
) -> None:
    output.write_line("")
    if shown is None:
        output.write_line(f"<info>{_display(path)}</info>")
        output.write_line("<comment>This stop is the next koan, not a crash.</comment>")
        return
    lineno, text = shown
    output.write_line(f"<info>{_display(path)}:{lineno}</info>")
    output.write_line(text, type=Type.RAW)
    output.write_line("")
    output.write_line("<comment>This stop is the next koan, not a crash.</comment>")
    if hint:
        output.write_line(f"Hint: {hint}", type=Type.RAW)


def _display(path: Path) -> str:
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return str(path)


def _method_text(source: str, method_name: str) -> tuple[int, str] | None:
    function = _function(source, method_name)
    if function is None:
        return None
    lines = source.splitlines()
    end = function.end_lineno or function.lineno
    chunk = "\n".join(lines[function.lineno - 1 : end])
    return function.lineno, chunk


def _slots(
    source: str,
    method_name: str,
    kind: StopKind,
    failing_lineno: int | None,
) -> list[_Slot]:
    function = _function(source, method_name)
    if function is None:
        return []
    found = _unfilled_slots(source, function)
    match kind:
        case "unfilled" | "raised":
            extra: list[_Slot] = []
        case "because":
            extra = _filled_because_slots(source, function)
        case "prediction":
            extra = _prediction_slots(source, function, failing_lineno)
        case _ as unreachable:
            _assert_never(unreachable)
    for slot in extra:
        if any(_overlaps(slot, current) for current in found):
            continue
        found.append(slot)
    found.sort(key=lambda slot: slot.start)
    return found


def _function(source: str, method_name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            return node
    return None


def _unfilled_slots(source: str, function: ast.AST) -> list[_Slot]:
    found: list[_Slot] = []

    def walk(node: ast.AST) -> None:
        if isinstance(node, ast.Call) and _call_name(node) == "because":
            for arg in _because_args(node):
                if _is_blank(arg):
                    found.append(_slot(source, "because", arg))
                else:
                    walk(arg)
            return
        if _is_blank(node):
            found.append(_slot(source, "value", node))
            return
        for child in ast.iter_child_nodes(node):
            walk(child)

    for statement in getattr(function, "body", []):
        walk(statement)
    return found


def _filled_because_slots(source: str, function: ast.AST) -> list[_Slot]:
    found: list[_Slot] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or _call_name(node) != "because":
            continue
        for arg in _because_args(node):
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                found.append(_slot(source, "because", arg))
    return found


def _prediction_slots(
    source: str,
    function: ast.AST,
    failing_lineno: int | None,
) -> list[_Slot]:
    if failing_lineno is None:
        return []
    call = _assertion_on_line(function, failing_lineno)
    if call is None or not call.args:
        return []
    prediction = call.args[-1]
    if _is_blank(prediction):
        return []
    return [_slot(source, "value", prediction)]


def _assertion_on_line(function: ast.AST, lineno: int) -> ast.Call | None:
    found: list[ast.Call] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call) or not _is_assert(node):
            continue
        end = node.end_lineno or node.lineno
        if node.lineno <= lineno <= end:
            found.append(node)
    if not found:
        return None
    found.sort(key=lambda node: (node.end_lineno or node.lineno) - node.lineno)
    return found[0]


def _because_args(node: ast.Call) -> list[ast.expr]:
    args = list(node.args)
    for keyword in node.keywords:
        if keyword.arg in {None, "reason"}:
            args.append(keyword.value)
    return args


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def _is_assert(node: ast.Call) -> bool:
    return isinstance(node.func, ast.Attribute) and node.func.attr.startswith("assert")


def _is_blank(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "__" and isinstance(node.ctx, ast.Load)


def _slot(source: str, kind: SlotKind, node: ast.AST) -> _Slot:
    lineno = getattr(node, "lineno", 1)
    column = getattr(node, "col_offset", 0)
    end_line = getattr(node, "end_lineno", None) or lineno
    end_column = getattr(node, "end_col_offset", None)
    if end_column is None:
        end_column = column
    return _Slot(kind, _offset(source, lineno, column), _offset(source, end_line, end_column), lineno)


def _offset(source: str, lineno: int, column: int) -> int:
    lines = source.splitlines(keepends=True)
    return sum(len(lines[index]) for index in range(min(lineno - 1, len(lines)))) + column


def _overlaps(left: _Slot, right: _Slot) -> bool:
    return not (left.end <= right.start or right.end <= left.start)


def _ask_all(slots: list[_Slot], stdin: TextIO, output: StreamOutput) -> list[str] | None:
    answers: list[str] = []
    for slot in slots:
        answer = _ask_one(slot, stdin, output)
        if answer is None:
            return None
        answers.append(answer)
    return answers


def _ask_one(slot: _Slot, stdin: TextIO, output: StreamOutput) -> str | None:
    while True:
        output.write(_prompt_label(slot))
        output.write("> ")
        output.flush()
        text = _read_line(stdin)
        if text is None:
            output.write_line("")
            return None
        if slot.kind == "because":
            return text
        try:
            ast.parse(text, mode="eval")
        except SyntaxError:
            output.write_line("<error>That is not a Python expression.</error>")
            continue
        return text


def _prompt_label(slot: _Slot) -> str:
    match slot.kind:
        case "value":
            question = "Python expression"
        case "because":
            question = "One sentence naming the mechanism"
        case _ as unreachable:
            _assert_never(unreachable)
    return f"<info>Line {slot.lineno}: {question}:</info> "


def _read_line(stdin: TextIO) -> str | None:
    if stdin is sys.stdin:
        try:
            text = input()
        except EOFError:
            return None
    else:
        text = stdin.readline()
        if text == "":
            return None
        text = text.rstrip("\n")
    if text.strip() == "":
        return None
    return text.strip()


def _apply(source: str, slots: list[_Slot], answers: list[str]) -> str:
    pieces: list[tuple[int, int, str]] = []
    for slot, answer in zip(slots, answers, strict=True):
        match slot.kind:
            case "value":
                text = answer
            case "because":
                text = json.dumps(answer, ensure_ascii=False)
            case _ as unreachable:
                _assert_never(unreachable)
        pieces.append((slot.start, slot.end, text))
    for start, end, text in sorted(pieces, reverse=True):
        source = source[:start] + text + source[end:]
    return source
