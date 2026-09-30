# Axiom: a function is an object you can pass and call. A default argument expression runs once, when the def statement runs, not on each call.

from koans.engine import Koan, blank, expects

__ = blank


class AboutFunctions(Koan):
    @expects("first-class", hint="Say what kind of value was passed into apply.")
    def test_a_function_can_be_passed(self):
        def add(left, right):
            return left + right

        def apply(fn, left, right):
            return fn(left, right)

        self.assertEqual(apply(add, 2, 5), __)
        self.assertEqual(type(add).__name__, __)
        self.because(__)

    # Bridge: JS evaluates a default expression on each call. Python evaluates it once, when def runs, and reuses that object.
    @expects("once", hint="Say how many times Python evaluates the default expression.")
    def test_a_default_argument_is_evaluated_once(self):
        def collect(item, bucket=[]):
            bucket.append(item)
            return bucket

        first = collect("a")
        second = collect("b")
        self.assertEqual(first, __)
        self.assertEqual(second, __)
        self.assertEqual(first is second, __)
        self.because(__)

    @expects("per call", hint="Say when this version builds the list.")
    def test_a_none_default_builds_a_new_list_per_call(self):
        def collect(item, bucket=None):
            if bucket is None:
                bucket = []
            bucket.append(item)
            return bucket

        self.assertEqual(collect("a"), __)
        self.assertEqual(collect("b"), __)
        self.assertEqual(collect("c") is collect("d"), __)
        self.because(__)
