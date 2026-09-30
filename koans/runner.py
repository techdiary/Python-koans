"""Run koans in order and stop at the first failure or error."""

from __future__ import annotations

import importlib
import inspect
import os
import sys
import traceback
import unittest
from pathlib import Path

from cleo.io.outputs.output import Type
from cleo.io.outputs.stream_output import StreamOutput
from cleo.ui.progress_indicator import ProgressIndicator

from koans.engine import Koan

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
        self.output.write_line(location_of(test, err), type=Type.RAW)
        self.output.write_line(message_of(err), type=Type.RAW)
        self.output.write_line("")

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
