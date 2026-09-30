# Axiom: a koan passes when every blank holds a real value and because() names the mechanism in one sentence.

from koans.engine import Koan, blank, expects

__ = blank


class AboutAsserts(Koan):
    @expects("value", hint="Say what kind of comparison the assertion performs.")
    def test_replace_the_blank_with_the_predicted_value(self):
        self.assertEqual(1 + 1, __)
        self.because(__)

    # Bridge: JS == may coerce "2" and 2 into one value. Python == does not coerce.
    @expects("coerce", hint="Say whether Python converts the two sides into one type first.")
    def test_equality_does_not_coerce_types(self):
        self.assertEqual("2" == 2, __)
        self.assertEqual(2 == 2, __)
        self.because(__)
