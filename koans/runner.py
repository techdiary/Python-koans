"""Run koans in order and stop at the first failure or error."""

from __future__ import annotations

import ast
import importlib
import inspect
import os
import sys
import textwrap
import traceback
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NoReturn

from cleo.io.outputs.output import Type
from cleo.io.outputs.stream_output import StreamOutput
from cleo.ui.progress_indicator import ProgressIndicator

from koans.engine import DOES_NOT_NAME, FILL_IN_THE_BLANK, Koan, STATE_THE_MECHANISM

if TYPE_CHECKING:
    from typing import Never

ROOT = Path(__file__).resolve().parent.parent


def method_names(cls: type) -> list[str]:
    """Test methods in source order, not alphabetical order."""
    names: list[str] = []
    for name, value in cls.__dict__.items():
        if name.startswith("test") and callable(value):
            names.append(name)
    return names


def suite_from_classes(classes: list[type[Koan]]) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for cls in classes:
        for name in method_names(cls):
            suite.addTest(cls(name))
    return suite


def load_suite(module_names: list[str]) -> unittest.TestSuite:
    classes: list[type[Koan]] = []
    for module_name in module_names:
        module = importlib.import_module(module_name)
        found = [
            obj
            for _, obj in inspect.getmembers(module, inspect.isclass)
            if issubclass(obj, Koan) and obj.__module__ == module.__name__
        ]
        found.sort(key=lambda obj: inspect.getsourcelines(obj)[1])
        classes.extend(found)
    return suite_from_classes(classes)


def location_of(test: unittest.TestCase, err: tuple) -> str:
    records = traceback.extract_tb(err[2])
    test_file = os.path.abspath(inspect.getfile(type(test)))
    chosen = records[-1] if records else None
    for record in records:
        if os.path.abspath(record.filename) == test_file:
            chosen = record
    if chosen is None:
        return test.id()
    try:
        relative = os.path.relpath(chosen.filename, ROOT)
    except ValueError:
        relative = chosen.filename
    return f"{relative}:{chosen.lineno}"


def message_of(err: tuple) -> str:
    text = str(err[1]).strip()
    if text:
        return text
    return getattr(err[0], "__name__", "assertion failed")


StopKind = Literal["unfilled", "because", "prediction", "raised"]

SAVE_AND_RERUN = "Save the file, then run `python-koans start` again."
CHANGE_AND_RERUN = "Change that blank, save, and run `python-koans start` again."
FIX_AND_RERUN = "Fix the error, save, and run `python-koans start` again."


def _blank_argument(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id in {"__", "blank"}


def because_still_blank(test: unittest.TestCase) -> bool:
    """True when this test still calls because() with the blank sentinel."""
    method_name = getattr(test, "_testMethodName", "")
    method = getattr(test, method_name, None)
    if method is None:
        return False
    try:
        source = textwrap.dedent(inspect.getsource(method))
        tree = ast.parse(source)
    except (OSError, TypeError, SyntaxError):
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            called = func.attr
        elif isinstance(func, ast.Name):
            called = func.id
        else:
            continue
        if called != "because":
            continue
        if any(_blank_argument(arg) for arg in node.args):
            return True
        if any(
            keyword.arg in {None, "reason"} and _blank_argument(keyword.value)
            for keyword in node.keywords
        ):
            return True
    return False


def hint_on(test: unittest.TestCase) -> str | None:
    method_name = getattr(test, "_testMethodName", "")
    method = getattr(test, method_name, None)
    hint = getattr(method, "_koan_hint", None)
    if isinstance(hint, str) and hint.strip():
        return hint.strip()
    return None


def hint_in(message: str) -> str | None:
    marker = f"{DOES_NOT_NAME} Hint:"
    if not message.startswith(marker):
        return None
    text = message[len(marker):].strip()
    return text or None


def classify_stop(err: tuple) -> StopKind:
    message = message_of(err)
    if message == FILL_IN_THE_BLANK:
        return "unfilled"
    if message == STATE_THE_MECHANISM or message.startswith(DOES_NOT_NAME):
        return "because"
    exc_type = err[0]
    if isinstance(exc_type, type) and issubclass(exc_type, AssertionError):
        return "prediction"
    return "raised"


def _say(output: StreamOutput, text: str, *, raw: bool = False) -> None:
    output.write_line(text, type=Type.RAW if raw else Type.NORMAL)


def _where(output: StreamOutput, test: unittest.TestCase, err: tuple) -> None:
    name = getattr(test, "_testMethodName", test.id())
    _say(output, f"<info>{location_of(test, err)}</info>")
    _say(output, f"<info>{name}</info>")


def _hint_line(output: StreamOutput, hint: str | None) -> None:
    if hint:
        _say(output, f"Hint: {hint}", raw=True)


def _assert_never(kind: Never) -> NoReturn:
    raise AssertionError(kind)


def write_stop(output: StreamOutput, test: unittest.TestCase, err: tuple) -> None:
    """Say why the path stopped and what to edit. Do not print the answer or the stems."""
    kind = classify_stop(err)
    message = message_of(err)
    match kind:
        case "unfilled":
            _say(
                output,
                "<comment>This stop is the next koan, not a crash. "
                "An unfilled `__` was used as a value: fill in the blank.</comment>",
            )
            _where(output, test, err)
            _say(output, "Replace `__` with the value you predict.")
            if because_still_blank(test):
                _say(output, "Replace `because(__)` with one sentence naming the mechanism.")
            _hint_line(output, hint_on(test))
            _say(output, f"<b>{SAVE_AND_RERUN}</b>")
        case "because":
            _say(
                output,
                "<comment>The value may be right, but the sentence does not name the mechanism.</comment>",
            )
            _where(output, test, err)
            _hint_line(output, hint_on(test) or hint_in(message))
            _say(output, f"<b>{SAVE_AND_RERUN}</b>")
        case "prediction":
            _say(output, "<error>The prediction did not match.</error>")
            _where(output, test, err)
            _say(output, f"<b>{CHANGE_AND_RERUN}</b>")
        case "raised":
            exc_name = getattr(err[0], "__name__", "Exception")
            _say(output, f"<error>The test raised {exc_name}.</error>")
            _where(output, test, err)
            if message and message != exc_name:
                _say(output, message, raw=True)
            _say(output, f"<b>{FIX_AND_RERUN}</b>")
        case _ as unreachable:
            _assert_never(unreachable)
    output.write_line("")


def lesson_of(test: unittest.TestCase) -> str:
    return Path(inspect.getfile(type(test))).stem


def open_output(stream) -> StreamOutput:
    """Color follows the stream. A pipe or capture is plain text."""
    return StreamOutput(stream)


class StopResult(unittest.TestResult):
    def __init__(self, output: StreamOutput) -> None:
        super().__init__()
        self.failfast = True
        self.output = output
        self.first: tuple[unittest.TestCase, tuple] | None = None
        self._lesson: str | None = None

    def _step(self, test: unittest.TestCase, failed: bool, err: tuple | None) -> None:
        lesson = lesson_of(test)
        if lesson != self._lesson:
            self._lesson = lesson
            self.output.write_line(f"<c1>{lesson}</c1>")
        style = "error" if failed else "info"
        name = getattr(test, "_testMethodName", test.id())
        self.output.write_line(f"  <{style}>{name}</>")
        if not failed or err is None:
            return
        write_stop(self.output, test, err)

    def addSuccess(self, test: unittest.TestCase) -> None:
        super().addSuccess(test)
        self._step(test, failed=False, err=None)

    def addFailure(self, test: unittest.TestCase, err: tuple) -> None:
        super().addFailure(test, err)
        if self.first is None:
            self.first = (test, err)
        self._step(test, failed=True, err=err)

    def addError(self, test: unittest.TestCase, err: tuple) -> None:
        super().addError(test, err)
        if self.first is None:
            self.first = (test, err)
        self._step(test, failed=True, err=err)


def run_suite(suite: unittest.TestSuite, stream=None, output: StreamOutput | None = None) -> int:
    if stream is None:
        stream = sys.stdout
    if output is None:
        output = open_output(stream)
    total = suite.countTestCases()
    output.write_line(f"<b>{total} koans. The path stops at the first failure.</b>")
    output.write_line("")
    result = StopResult(output)
    suite.run(result)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    output.write_line(f"Passed {passed} of {total}.")
    if result.wasSuccessful():
        return 0
    return 1


def run_path(module_names: list[str], stream=None) -> int:
    if stream is None:
        stream = sys.stdout
    output = open_output(stream)
    indicator = ProgressIndicator(
        output,
        fmt=" {indicator} {message}" if output.is_decorated() else "{message}",
    )
    with indicator.auto("Loading lessons", "Lessons loaded."):
        suite = load_suite(module_names)
    return run_suite(suite, stream, output=output)
