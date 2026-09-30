"""Lesson progress is the working files. Pristine copies live beside them and are not the lessons."""

from __future__ import annotations

import ast
import io
import shutil
import tokenize
from pathlib import Path

from cleo.io.outputs.stream_output import StreamOutput

from koans.catalog import KOAN_MODULES

PACKAGE = Path(__file__).resolve().parent
STUDENT_WORK = "student_work.py"
TRANSFER = "about_transfer"


def lesson_stem(module_name: str) -> str:
    return module_name.rsplit(".", 1)[-1]


def has_unfilled_blank(source: str) -> bool:
    """True when the identifier `__` is still a fill-in value.

    `__ = blank` only publishes the sentinel. `__eq__` and other longer
    names are not blanks.
    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenizeError:
        return True
    for index, token in enumerate(tokens):
        if token.type != tokenize.NAME or token.string != "__":
            continue
        if _is_sentinel_binding(tokens, index):
            continue
        return True
    return False


def _is_sentinel_binding(tokens: list[tokenize.TokenInfo], index: int) -> bool:
    if index + 2 >= len(tokens):
        return False
    equals, name = tokens[index + 1], tokens[index + 2]
    return (
        equals.type == tokenize.OP
        and equals.string == "="
        and name.type == tokenize.NAME
        and name.string == "blank"
    )


def student_work_is_implemented(source: str) -> bool:
    """True when no function is still a pass or NotImplementedError stub."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if not functions:
        return False
    return all(not _is_stub(node) for node in functions)


def _is_stub(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    body = _without_docstring(function.body)
    if len(body) != 1:
        return len(body) == 0
    statement = body[0]
    if isinstance(statement, ast.Pass):
        return True
    if isinstance(statement, ast.Raise):
        return _raises_not_implemented(statement)
    return False


def _without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if not body:
        return body
    first = body[0]
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return body[1:]
    return body


def _raises_not_implemented(statement: ast.Raise) -> bool:
    exc = statement.exc
    if isinstance(exc, ast.Name):
        return exc.id == "NotImplementedError"
    if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
        return exc.func.id == "NotImplementedError"
    return False


def lesson_is_complete(path: Path, student_work: Path) -> bool:
    if not path.is_file():
        return False
    if has_unfilled_blank(path.read_text(encoding="utf-8")):
        return False
    if path.stem != TRANSFER:
        return True
    if not student_work.is_file():
        return False
    return student_work_is_implemented(student_work.read_text(encoding="utf-8"))


def lesson_rows(root: Path | None = None) -> list[tuple[str, bool]]:
    """Every topic, in path order. Completion does not stop the list."""
    package = root or PACKAGE
    student_work = package / STUDENT_WORK
    return [
        (stem, lesson_is_complete(package / f"{stem}.py", student_work))
        for stem in (lesson_stem(name) for name in KOAN_MODULES)
    ]


def write_lesson_list(output: StreamOutput, rows: list[tuple[str, bool]]) -> None:
    for name, done in rows:
        if done:
            output.write_line(f"<info>✓</info> {name}")
        else:
            output.write_line(f"<error>✗</error> {name}")


def restart_journey(root: Path | None = None) -> None:
    """Overwrite the working lessons and the student stub from the pristine copy."""
    package = root or PACKAGE
    source = package / "pristine"
    names = [f"{lesson_stem(name)}.py" for name in KOAN_MODULES]
    names.append(STUDENT_WORK)
    for name in names:
        origin = source / name
        if not origin.is_file():
            raise FileNotFoundError(f"Missing pristine copy: {origin}")
        shutil.copyfile(origin, package / name)
