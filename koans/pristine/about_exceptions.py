# Axiom: an exception is an object. It propagates until an except clause matches its class. else runs when the try body does not raise. finally runs on the way out.

from koans.engine import Koan, blank, expects

__ = blank


class AboutExceptions(Koan):
    @expects("object", hint="Say what the except clause binds.")
    def test_an_exception_is_an_object(self):
        caught = None
        try:
            raise ValueError("nope")
        except ValueError as err:
            caught = err
        self.assertEqual(type(caught).__name__, __)
        self.assertEqual(str(caught), __)
        self.because(__)

    @expects("propagate", hint="Say how the exception leaves the inner function.")
    def test_an_exception_propagates_until_it_matches(self):
        def inner():
            raise KeyError("missing")

        def outer():
            inner()

        name = "none"
        try:
            outer()
        except KeyError as err:
            name = type(err).__name__
        self.assertEqual(name, __)
        self.because(__)

    # Bridge: JS can throw a string. Python raise expects an exception class or an exception object.
    @expects("exception object", hint="Say what raise does when its argument is a string.")
    def test_raise_requires_an_exception(self):
        kind = "none"
        try:
            raise "nope"
        except TypeError:
            kind = "TypeError"
        self.assertEqual(kind, __)
        self.because(__)

    @expects("subclass", hint="Say why the LookupError clause matches this raise.")
    def test_except_matches_a_subclass(self):
        class Smaller(LookupError):
            pass

        name = "none"
        try:
            raise Smaller("x")
        except LookupError as err:
            name = type(err).__name__
        except Exception:
            name = "Exception"
        self.assertEqual(name, __)
        self.because(__)

    @expects("else", hint="Say which clause runs when the try body does not raise, besides the one that always runs.")
    def test_else_runs_only_when_try_does_not_raise(self):
        quiet = []
        try:
            quiet.append("try")
        except Exception:
            quiet.append("except")
        else:
            quiet.append("else")
        finally:
            quiet.append("finally")

        noisy = []
        try:
            noisy.append("try")
            raise RuntimeError("boom")
        except RuntimeError:
            noisy.append("except")
        else:
            noisy.append("else")
        finally:
            noisy.append("finally")

        self.assertEqual(quiet, __)
        self.assertEqual(noisy, __)
        self.because(__)
