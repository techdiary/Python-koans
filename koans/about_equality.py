# Axiom: == asks for value by calling __eq__. `is` asks whether two names refer to the same object. Do not compare numbers with `is`.

from koans.engine import Koan, blank, expects

__ = blank


class AboutEquality(Koan):
    # Bridge: JS === is not Python `is`, and it is not Python ==. Java == on objects is identity. Python == calls __eq__.
    @expects("__eq__", hint="Say which method the value comparison calls.")
    def test_double_equals_asks_for_value(self):
        self.assertEqual([1, 2] == [1, 2], __)
        self.assertEqual([1, 2] is [1, 2], __)
        self.because(__)

    @expects("same object", hint="Say what `is` reports.")
    def test_is_asks_whether_names_share_an_object(self):
        sentinel = object()
        alias = sentinel
        self.assertEqual(alias is sentinel, __)
        self.assertEqual(object() is object(), __)
        self.because(__)

    # Accident, once: on some runtimes int("3") is int("3") because one object was reused. That is not a rule.
    @expects("not a rule", hint="Say whether you may use identity to compare numbers.")
    def test_number_identity_is_not_a_rule(self):
        self.assertEqual(int("4000") == int("4000"), __)
        self.assertEqual(None is None, __)
        self.because(__)
