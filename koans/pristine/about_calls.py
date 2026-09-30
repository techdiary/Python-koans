# Axiom: a call binds argument objects to parameter names. The rule is the same as assignment. The call does not copy the object.

from koans.engine import Koan, blank, expects

__ = blank


class AboutCalls(Koan):
    @expects("bind", hint="Say what a call does with the argument object and the parameter name.")
    def test_a_call_binds_the_parameter_name(self):
        def same(obj):
            return obj

        box = ["a"]
        self.assertEqual(same(box) is box, __)
        self.because(__)

    # Bridge: Java copies primitives and copies object references. Reassigning a parameter never updates the caller's name. Mutating the object does. Python has no primitive parameters, so every argument follows that object rule.
    @expects("rebind", hint="Say which name the assignment inside the function changes.")
    def test_rebinding_a_parameter_leaves_the_caller(self):
        def replace(items):
            items = ["local"]
            return items

        caller = ["caller"]
        self.assertEqual(replace(caller), __)
        self.assertEqual(caller, __)
        self.because(__)

    @expects("mutate", hint="Say why the caller sees the append.")
    def test_mutating_the_argument_is_visible_to_the_caller(self):
        def grow(items):
            items.append("more")

        caller = ["caller"]
        grow(caller)
        self.assertEqual(caller, __)
        self.because(__)
