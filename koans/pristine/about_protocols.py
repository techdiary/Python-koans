# Axiom: Python asks an object for behavior by calling special methods. You do not declare an interface. __iter__, __len__, __eq__, __enter__, and __exit__ are enough for the operations below.

from __future__ import annotations

from koans.engine import Koan, blank, expects

__ = blank


class Bag:
    def __init__(self, items: list[object]) -> None:
        self.items = list(items)

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bag):
            return NotImplemented
        return self.items == other.items

    def __enter__(self) -> Bag:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.items.clear()
        return False


class AboutProtocols(Koan):
    @expects("__iter__", hint="Say which method a for-loop uses to walk this object.")
    def test_iter_makes_the_object_iterable(self):
        self.assertEqual(list(Bag([1, 2])), __)
        self.because(__)

    @expects("__len__", hint="Say which method len uses.")
    def test_len_uses_the_length_method(self):
        self.assertEqual(len(Bag([1, 2, 3])), __)
        self.because(__)

    # Bridge: Java == on objects is identity unless you call equals. Python == calls __eq__.
    @expects("__eq__", hint="Say which method the value comparison calls.")
    def test_eq_compares_contents(self):
        self.assertEqual(Bag([1, 2]) == Bag([1, 2]), __)
        self.assertEqual(Bag([1, 2]) is Bag([1, 2]), __)
        self.because(__)

    @expects("__exit__", hint="Say which method runs as the with block ends.")
    def test_with_enters_and_then_exits(self):
        bag = Bag([1, 2])
        with bag as entered:
            seen = list(entered)
        self.assertEqual(seen, __)
        self.assertEqual(list(bag), __)
        self.assertEqual(entered is bag, __)
        self.because(__)
