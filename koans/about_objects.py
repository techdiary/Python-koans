# Axiom: every value is an object. Identity, type, and value are three different questions.

from koans.engine import Koan, blank, expects

__ = blank


class AboutObjects(Koan):
    # Bridge: Java int and boolean are primitives, not objects. A Python name always refers to an object.
    @expects("object", hint="Say what a Python value is.")
    def test_every_value_is_an_object(self):
        self.assertEqual(isinstance(1, object), __)
        self.assertEqual(isinstance(True, object), __)
        self.assertEqual(isinstance(None, object), __)
        self.assertEqual(type(1).__name__, __)
        self.because(__)

    @expects("type", hint="Say what you get when you ask for the class of a value.")
    def test_type_reports_the_class(self):
        self.assertEqual(type([]).__name__, __)
        self.assertEqual(type([]) is list, __)
        self.because(__)

    # Bridge: JS == on two arrays is identity, and Java == on objects is identity. Python == asks whether the values match.
    @expects(
        "identity",
        "value",
        hint="Say which operator asks for one object, and which asks whether the contents match.",
    )
    def test_equal_contents_can_be_different_objects(self):
        left = [1, 2]
        right = [1, 2]
        self.assertEqual(left == right, __)
        self.assertEqual(left is right, __)
        self.because(__)
