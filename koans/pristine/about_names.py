# Axiom: assignment binds a name to an object. It does not copy the object, and it does not update other names.

from koans.engine import Koan, blank, expects

__ = blank


class AboutNames(Koan):
    @expects("bind", hint="Say what an assignment does to a name.")
    def test_assignment_binds_a_name(self):
        color = "blue"
        other = color
        self.assertEqual(color, __)
        self.assertEqual(other, __)
        self.assertEqual(other is color, __)
        self.because(__)

    @expects("rebind", hint="Say what the second assignment changes, and what it leaves alone.")
    def test_rebinding_one_name_leaves_the_other(self):
        color = "blue"
        other = color
        color = "red"
        self.assertEqual(color, __)
        self.assertEqual(other, __)
        self.because(__)

    # Bridge: Java copies a primitive on assignment. Python assignment never copies; it binds another name to the same object.
    @expects("same object", hint="Say why the append is visible through both names.")
    def test_two_names_can_refer_to_one_object(self):
        items = ["pen"]
        alias = items
        items.append("cup")
        self.assertEqual(alias, __)
        self.assertEqual(items is alias, __)
        self.because(__)
