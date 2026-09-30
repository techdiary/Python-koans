# Axiom: importing a module executes its body once and caches the module object. A later import returns that same object. from-import binds the current object into this module; a later assignment in the source module does not move that name.

import importlib

import koans.fixtures.meter as meter
from koans.engine import Koan, blank, expects
from koans.fixtures.meter import publish
from koans.fixtures.meter import value as imported_value

__ = blank


class AboutModules(Koan):
    @expects("once", hint="Say how many times the module body runs across two imports.")
    def test_import_executes_the_module_once(self):
        again = importlib.import_module("koans.fixtures.meter")
        self.assertEqual(meter.loads, __)
        self.assertEqual(again is meter, __)
        self.because(__)

    # Bridge: an ES module export is a live binding. Python from-import assigns the object the name refers to at that moment.
    @expects("assignment", hint="Say what from-import does, and which name publish updates.")
    def test_from_import_binds_the_current_object(self):
        publish("changed")
        self.assertEqual(meter.value, __)
        self.assertEqual(imported_value, __)
        self.because(__)
