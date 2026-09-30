"""Prove the blank, because(), and the runner. These tests do not fill the koans."""

from __future__ import annotations

import io
import os
import subprocess
import sys
import unittest
from pathlib import Path

from koans.engine import Koan, blank, expects
from koans.runner import run_suite, suite_from_classes

ROOT = Path(__file__).resolve().parent.parent


class HarnessTests(unittest.TestCase):
    def _assert_blank(self, operation) -> None:
        with self.assertRaises(AssertionError) as caught:
            operation()
        self.assertIn("fill in the blank", str(caught.exception).lower())

    def test_blank_sentinel_fails_comparisons_and_iteration(self):
        self._assert_blank(lambda: blank == 1)
        self._assert_blank(lambda: 1 == blank)
        self._assert_blank(lambda: blank != 1)
        self._assert_blank(lambda: blank < 1)
        self._assert_blank(lambda: blank <= 1)
        self._assert_blank(lambda: blank > 1)
        self._assert_blank(lambda: blank >= 1)
        self._assert_blank(lambda: list(blank))
        self._assert_blank(lambda: iter(blank))
        self._assert_blank(lambda: 1 in blank)

    def test_because_rejects_a_sentence_missing_stems_and_accepts_one_that_has_them(self):
        class Sample(Koan):
            @expects(
                "rebind",
                "same object",
                hint="Name the operation on the label.",
            )
            def test_body(self):
                pass

            @expects(any_of=(("alias", "shared"), ("rebind",)), hint="Name the operation.")
            def test_alt(self):
                pass

        good = Sample("test_body")
        good.because("Assignment will rebind the name to the same object")
        good.because("REBIND onto the SAME OBJECT")

        missing = Sample("test_body")
        with self.assertRaises(AssertionError) as caught:
            missing.because("the values match")
        message = str(caught.exception)
        self.assertIn("does not name the mechanism", message.lower())
        self.assertIn("hint:", message.lower())
        folded = message.casefold()
        self.assertNotIn("rebind", folded)
        self.assertNotIn("same object", folded)

        partial = Sample("test_body")
        with self.assertRaises(AssertionError) as caught_partial:
            partial.because("it will rebind")
        self.assertIn("does not name the mechanism", str(caught_partial.exception).lower())

        unfilled = Sample("test_body")
        with self.assertRaises(AssertionError) as caught_blank:
            unfilled.because(blank)
        self.assertIn("state the mechanism in one line", str(caught_blank.exception).lower())

        quoted = Sample("test_body")
        with self.assertRaises(AssertionError) as caught_quoted:
            quoted.because("__")
        self.assertIn("state the mechanism in one line", str(caught_quoted.exception).lower())

        inline = Sample("test_body")
        inline.because("names rebind", requires=["rebind"])

        alt = Sample("test_alt")
        alt.because("the second assignment will rebind")
        with self.assertRaises(AssertionError):
            alt.because("they are an alias")

    def test_runner_stops_at_the_first_failure(self):
        steps: list[str] = []

        class Ordered(Koan):
            def test_zebra(self):
                steps.append("zebra")
                self.fail("alpha-stop")

            def test_alpha(self):
                steps.append("alpha")
                self.fail("should-not-run")

        stream = io.StringIO()
        code = run_suite(suite_from_classes([Ordered]), stream)
        text = stream.getvalue()
        self.assertEqual(code, 1)
        self.assertEqual(steps, ["zebra"])
        self.assertIn("alpha-stop", text)
        self.assertNotIn("should-not-run", text)
        self.assertIn("Passed 0 of 2.", text)
        self.assertRegex(text, r"tests/test_harness\.py:\d+")

        class PassThenFail(Koan):
            def test_ok(self):
                steps.append("ok")
                self.assertEqual(1, 1)

            def test_bad(self):
                steps.append("bad")
                self.fail("stopped-here")

            def test_later(self):
                steps.append("later")
                self.fail("not-reached")

        steps.clear()
        stream = io.StringIO()
        code = run_suite(suite_from_classes([PassThenFail]), stream)
        text = stream.getvalue()
        self.assertEqual(code, 1)
        self.assertEqual(steps, ["ok", "bad"])
        self.assertIn("stopped-here", text)
        self.assertNotIn("not-reached", text)
        self.assertIn("Passed 1 of 3.", text)

    def test_the_path_stops_on_the_first_unfilled_blank(self):
        completed = subprocess.run(
            [sys.executable, "path_to_enlightenment.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("koans/about_asserts.py:", completed.stdout)
        self.assertIn("fill in the blank", completed.stdout)
        self.assertRegex(completed.stdout, r"Passed 0 of \d+\.")
        self.assertNotIn("about_objects.py", completed.stdout)
        self.assertNotIn("\x1b", completed.stdout)
        self.assertEqual(completed.stderr, "")

    def test_start_continues_from_any_directory(self):
        env = dict(**os.environ)
        env["PYTHONPATH"] = str(ROOT)
        completed = subprocess.run(
            [sys.executable, "-m", "koans", "start"],
            cwd="/tmp",
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("koans/about_asserts.py:", completed.stdout)
        self.assertIn("fill in the blank", completed.stdout)
        self.assertIn("about_asserts", completed.stdout)
        self.assertIn("test_replace_the_blank_with_the_predicted_value", completed.stdout)
        self.assertRegex(completed.stdout, r"Passed 0 of \d+\.")
        self.assertNotIn("about_objects.py", completed.stdout)
        self.assertNotIn("\x1b", completed.stdout)


if __name__ == "__main__":
    unittest.main()
