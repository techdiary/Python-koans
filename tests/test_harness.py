"""Prove the blank, because(), and the runner. These tests do not fill the koans."""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from koans.catalog import KOAN_MODULES
from koans.engine import Koan, blank, expects
from koans.progress import (
    has_unfilled_blank,
    lesson_rows,
    restart_journey,
    student_work_is_implemented,
    write_lesson_list,
)
from koans.prompt import offer_fill
from koans.runner import open_output, run_suite, suite_from_classes

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
        self.assertIn("The prediction did not match.", text)
        self.assertIn("Change that blank, save, and run `python-koans start` again.", text)
        self.assertNotIn("alpha-stop", text)
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
        self.assertIn("The prediction did not match.", text)
        self.assertNotIn("stopped-here", text)
        self.assertNotIn("not-reached", text)
        self.assertIn("Passed 1 of 3.", text)

    def test_unfilled_blank_report_names_the_file_and_the_next_action(self):
        secret = "expected-answer-9f3c"

        class NextKoan(Koan):
            @expects("rebind", hint="Say what the assertion compares.")
            def test_predict_the_sum(self):
                self.assertEqual(secret, blank)
                self.because(blank)

        stream = io.StringIO()
        code = run_suite(suite_from_classes([NextKoan]), stream)
        text = stream.getvalue()
        self.assertEqual(code, 1)
        self.assertRegex(text, r"tests/test_harness\.py:\d+")
        self.assertIn("test_predict_the_sum", text)
        self.assertIn("not a crash", text)
        self.assertIn("Replace `__` with the value you predict.", text)
        self.assertIn("Replace `because(__)` with one sentence naming the mechanism.", text)
        self.assertIn("Say what the assertion compares.", text)
        self.assertIn("Save the file, then run `python-koans start` again.", text)
        self.assertNotIn(secret, text)
        self.assertNotIn("rebind", text)
        self.assertNotIn("\x1b", text)

    def test_because_stop_prints_the_hint_and_not_the_stems(self):
        class Missing(Koan):
            @expects("rebind", hint="Say what the second assignment does to the name.")
            def test_sentence(self):
                self.assertEqual(1, 1)
                self.because(blank)

        class Rejected(Koan):
            @expects(
                "alias",
                hint="Say whether the two names refer to one object.",
            )
            def test_sentence(self):
                self.assertEqual(1, 1)
                self.because("they look the same")

        missing = io.StringIO()
        self.assertEqual(run_suite(suite_from_classes([Missing]), missing), 1)
        missing_text = missing.getvalue()
        self.assertIn("does not name the mechanism", missing_text)
        self.assertIn("Say what the second assignment does to the name.", missing_text)
        self.assertIn("Save the file, then run `python-koans start` again.", missing_text)
        self.assertNotIn("rebind", missing_text)

        rejected = io.StringIO()
        self.assertEqual(run_suite(suite_from_classes([Rejected]), rejected), 1)
        rejected_text = rejected.getvalue()
        self.assertIn("does not name the mechanism", rejected_text)
        self.assertIn("Say whether the two names refer to one object.", rejected_text)
        self.assertNotIn("alias", rejected_text)
        self.assertNotIn("they look the same", rejected_text)

    def test_wrong_prediction_does_not_print_the_expected_value(self):
        secret = "expected-answer-9f3c"

        class Wrong(Koan):
            def test_guess(self):
                self.assertEqual(secret, "student-guess")

        stream = io.StringIO()
        code = run_suite(suite_from_classes([Wrong]), stream)
        text = stream.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("The prediction did not match.", text)
        self.assertRegex(text, r"tests/test_harness\.py:\d+")
        self.assertIn("Change that blank, save, and run `python-koans start` again.", text)
        self.assertNotIn(secret, text)
        self.assertNotIn("student-guess", text)

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

    def test_restart_restores_a_filled_blank_and_starts_at_the_first_koan(self):
        path = ROOT / "koans" / "about_asserts.py"
        original = path.read_text(encoding="utf-8")
        filled = original.replace(
            "self.assertEqual(1 + 1, __)",
            "self.assertEqual(1 + 1, 2)",
            1,
        )
        self.assertNotEqual(filled, original)
        path.write_text(filled, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, "-m", "koans", "start", "--restart"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            restored = path.read_text(encoding="utf-8")
            self.assertIn("self.assertEqual(1 + 1, __)", restored)
            self.assertNotIn("self.assertEqual(1 + 1, 2)", restored)
            self.assertEqual(restored, original)
            stdout = completed.stdout
            self.assertNotEqual(completed.returncode, 0)
            self.assertLess(stdout.index("Journey reset."), stdout.index("fill in the blank"))
            self.assertIn("koans/about_asserts.py:", stdout)
            self.assertRegex(stdout, r"Passed 0 of \d+\.")
            self.assertNotIn("about_objects.py", stdout)
            self.assertNotIn("\x1b", stdout)
            self.assertEqual(completed.stderr, "")
        finally:
            path.write_text(original, encoding="utf-8")

    def test_restart_copies_pristine_lessons_in_a_scratch_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pristine = root / "pristine"
            pristine.mkdir()
            lesson = "self.assertEqual(1 + 1, __)\n__ = blank\n"
            (pristine / "about_asserts.py").write_text(lesson, encoding="utf-8")
            (root / "about_asserts.py").write_text(
                "self.assertEqual(1 + 1, 2)\n__ = blank\n",
                encoding="utf-8",
            )
            for name in KOAN_MODULES:
                stem = name.rsplit(".", 1)[-1]
                target = pristine / f"{stem}.py"
                if not target.exists():
                    target.write_text(lesson, encoding="utf-8")
                if not (root / f"{stem}.py").exists():
                    (root / f"{stem}.py").write_text("self.assertEqual(1, __)\n", encoding="utf-8")
            (pristine / "student_work.py").write_text("raise NotImplementedError\n", encoding="utf-8")
            (root / "student_work.py").write_text("def add(self, track):\n    return track\n", encoding="utf-8")
            restart_journey(root)
            self.assertEqual(
                (root / "about_asserts.py").read_text(encoding="utf-8"),
                lesson,
            )
            self.assertEqual(
                (root / "student_work.py").read_text(encoding="utf-8"),
                "raise NotImplementedError\n",
            )

    def test_list_marks_a_tick_and_a_cross(self):
        self.assertTrue(has_unfilled_blank("self.because(__)\n__ = blank\n"))
        self.assertFalse(has_unfilled_blank("__ = blank\nself.assertEqual(item.__dict__, {})\n"))
        self.assertFalse(student_work_is_implemented("def add(self, track):\n    pass\n"))
        self.assertFalse(
            student_work_is_implemented("def add(self, track):\n    raise NotImplementedError\n")
        )
        self.assertTrue(
            student_work_is_implemented("def add(self, track):\n    self.tracks.append(track)\n")
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "about_asserts.py").write_text(
                "__ = blank\nself.assertEqual(1, 1)\n",
                encoding="utf-8",
            )
            for name in KOAN_MODULES:
                stem = name.rsplit(".", 1)[-1]
                path = root / f"{stem}.py"
                if path.exists():
                    continue
                path.write_text("self.because(__)\n__ = blank\n", encoding="utf-8")
            (root / "student_work.py").write_text(
                "def add(self, track):\n    raise NotImplementedError\n",
                encoding="utf-8",
            )
            rows = dict(lesson_rows(root))
            self.assertTrue(rows["about_asserts"])
            self.assertFalse(rows["about_objects"])
            self.assertFalse(rows["about_transfer"])

        stream = io.StringIO()
        write_lesson_list(
            open_output(stream),
            [("about_asserts", True), ("about_objects", False)],
        )
        text = stream.getvalue()
        self.assertIn("✓ about_asserts", text)
        self.assertIn("✗ about_objects", text)
        self.assertNotIn("\x1b", text)

        completed = subprocess.run(
            [sys.executable, "-m", "koans", "list"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertNotIn("\x1b", completed.stdout)
        self.assertEqual(completed.stderr, "")
        for name in KOAN_MODULES:
            stem = name.rsplit(".", 1)[-1]
            self.assertIn(f"✗ {stem}", completed.stdout)
        self.assertNotIn("✓", completed.stdout)

    def test_non_tty_start_does_not_prompt(self):
        lesson = ROOT / "koans" / "about_asserts.py"
        before = lesson.read_text(encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "-m", "koans", "start"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            stdin=subprocess.DEVNULL,
            timeout=30,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("fill in the blank", completed.stdout)
        self.assertNotIn("Python expression:", completed.stdout)
        self.assertNotIn("One sentence naming the mechanism:", completed.stdout)
        self.assertEqual(completed.stderr, "")
        self.assertEqual(lesson.read_text(encoding="utf-8"), before)

    def test_tty_style_fill_writes_value_and_because_into_a_copy(self):
        original = (ROOT / "koans" / "about_asserts.py").read_text(encoding="utf-8")
        pristine = (ROOT / "koans" / "pristine" / "about_asserts.py").read_text(encoding="utf-8")
        hint = "Say what kind of comparison the assertion performs."
        method = "test_replace_the_blank_with_the_predicted_value"
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "about_asserts.py"
            dest.write_text(original, encoding="utf-8")
            blocked = Path(tmp) / "pristine" / "about_asserts.py"
            blocked.parent.mkdir()
            blocked.write_text(original, encoding="utf-8")

            empty_out = io.StringIO()
            empty = offer_fill(
                dest,
                method,
                kind="unfilled",
                failing_lineno=11,
                hint=hint,
                stdin=io.StringIO("\n"),
                output=open_output(empty_out),
            )
            self.assertFalse(empty)
            self.assertEqual(dest.read_text(encoding="utf-8"), original)
            self.assertIn("not a crash", empty_out.getvalue())
            self.assertIn("def test_replace_the_blank_with_the_predicted_value", empty_out.getvalue())

            prompted = io.StringIO()
            wrote = offer_fill(
                dest,
                method,
                kind="unfilled",
                failing_lineno=11,
                hint=hint,
                stdin=io.StringIO("3\nnames rebind\n"),
                output=open_output(prompted),
            )
            text = prompted.getvalue()
            filled = dest.read_text(encoding="utf-8")
            self.assertTrue(wrote)
            self.assertIn("about_asserts.py:", text)
            self.assertIn("def test_replace_the_blank_with_the_predicted_value", text)
            self.assertIn("self.assertEqual(1 + 1, __)", text)
            self.assertIn("self.because(__)", text)
            self.assertIn("This stop is the next koan, not a crash.", text)
            self.assertIn(f"Hint: {hint}", text)
            self.assertIn("Line 11: Python expression:", text)
            self.assertIn("Line 12: One sentence naming the mechanism:", text)
            self.assertNotIn("@expects", text)
            self.assertNotIn('"value"', text)
            self.assertIn("self.assertEqual(1 + 1, 3)", filled)
            self.assertIn('self.because("names rebind")', filled)
            self.assertIn('self.assertEqual("2" == 2, __)', filled)
            self.assertNotIn("self.assertEqual(1 + 1, __)", filled)

            again = io.StringIO()
            lineno = next(
                index + 1
                for index, line in enumerate(filled.splitlines())
                if "1 + 1, 3" in line
            )
            replaced = offer_fill(
                dest,
                method,
                kind="prediction",
                failing_lineno=lineno,
                hint=hint,
                stdin=io.StringIO("2\n"),
                output=open_output(again),
            )
            corrected = dest.read_text(encoding="utf-8")
            self.assertTrue(replaced)
            self.assertIn("Line 11: Python expression:", again.getvalue())
            self.assertNotIn("One sentence naming the mechanism:", again.getvalue())
            self.assertIn("self.assertEqual(1 + 1, 2)", corrected)
            self.assertIn('self.because("names rebind")', corrected)

            with self.assertRaises(ValueError):
                offer_fill(
                    blocked,
                    method,
                    kind="unfilled",
                    failing_lineno=11,
                    hint=hint,
                    stdin=io.StringIO("2\nnames rebind\n"),
                    output=open_output(io.StringIO()),
                )
            self.assertEqual(blocked.read_text(encoding="utf-8"), original)

        self.assertEqual((ROOT / "koans" / "about_asserts.py").read_text(encoding="utf-8"), original)
        self.assertEqual(
            (ROOT / "koans" / "pristine" / "about_asserts.py").read_text(encoding="utf-8"),
            pristine,
        )


if __name__ == "__main__":
    unittest.main()
