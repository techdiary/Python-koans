# Axiom: a name is resolved local, then enclosing, then global, then built-in. A closure reads the name when it is called. A for loop rebinds one name.

from koans.engine import Koan, blank, expects

__ = blank


class AboutScope(Koan):
    @expects("local", hint="Say which scope supplied the value that paint returns.")
    def test_a_local_name_hides_the_global(self):
        color = "global"

        def paint():
            color = "local"
            return color

        self.assertEqual(paint(), __)
        self.assertEqual(color, __)
        self.because(__)

    @expects("unbound", hint="Say why the read fails even though a global of that name exists.")
    def test_an_assignment_makes_the_name_local_throughout_the_function(self):
        color = "global"

        def paint():
            try:
                seen = color
            except UnboundLocalError:
                seen = "unbound"
            color = "local"
            return seen

        self.assertEqual(paint(), __)
        self.because(__)

    # Bridge: JS let creates a new binding per iteration. Python for rebinds a single name. A closure looks up that name when it is called.
    @expects("late", hint="Say when the closure reads the loop name.")
    def test_closures_see_the_loop_name_late(self):
        funcs = []
        for i in range(3):
            funcs.append(lambda: i)
        self.assertEqual([fn() for fn in funcs], __)
        self.because(__)

    @expects("default", hint="Say when the parameter value is captured.")
    def test_a_default_captures_the_value_at_definition(self):
        funcs = []
        for i in range(3):
            funcs.append(lambda i=i: i)
        self.assertEqual([fn() for fn in funcs], __)
        self.because(__)
