# Axiom: a list comprehension builds the whole list when the statement runs. A generator expression computes each value when that value is requested. A comprehension has its own scope.

from koans.engine import Koan, blank, expects

__ = blank


class AboutComprehensions(Koan):
    @expects("immediately", hint="Say when the list comprehension runs the appends.")
    def test_a_list_comprehension_runs_at_once(self):
        seen = []
        built = [seen.append(n) or n for n in (1, 2)]
        self.assertEqual(seen, __)
        self.assertEqual(built, __)
        self.because(__)

    # Bridge: JS Array.map runs immediately, like a list comprehension. A generator expression does not run until the next value is requested.
    @expects("lazy", hint="Say when the generator expression runs the appends.")
    def test_a_generator_expression_is_lazy(self):
        seen = []
        lazy = (seen.append(n) or n for n in (1, 2))
        self.assertEqual(seen, __)
        self.assertEqual(list(lazy), __)
        self.assertEqual(seen, __)
        self.because(__)

    # A for statement rebinds a name in the surrounding scope. A comprehension keeps its names inside its own scope.
    @expects("scope", hint="Say whether the comprehension name is visible after the comprehension.")
    def test_a_comprehension_does_not_leak_its_names(self):
        for leaked in (7, 8):
            pass
        self.assertEqual(leaked, __)
        [hidden for hidden in (7, 8)]
        found = "visible"
        try:
            found = hidden
        except NameError:
            found = "NameError"
        self.assertEqual(found, __)
        self.because(__)
