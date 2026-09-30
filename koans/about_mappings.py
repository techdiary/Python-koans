# Axiom: a dict treats keys that compare equal as one key. Equal keys must share a hash, and that hash must stay stable while the key is in the dict.

from koans.engine import Koan, blank, expects

__ = blank


class AboutMappings(Koan):
    # Bridge: JS object keys are strings, so 1 and true stay different. Python uses ==. True == 1, so they are one key.
    @expects("equal", hint="Say why the later write replaced the earlier one.")
    def test_equal_keys_are_one_key(self):
        box = {1: "number"}
        box[True] = "bool"
        self.assertEqual(box[1], __)
        self.assertEqual(len(box), __)
        self.assertEqual(True == 1, __)
        self.because(__)

    @expects("stable", hint="Say what must not change while an object sits in a dict.")
    def test_a_key_must_keep_a_stable_hash(self):
        class Point:
            def __init__(self, x: int) -> None:
                self.x = x

            def __eq__(self, other: object) -> bool:
                return isinstance(other, Point) and self.x == other.x

            def __hash__(self) -> int:
                return hash(self.x)

        point = Point(1)
        places = {point: "here"}
        self.assertEqual(places[Point(1)], __)
        point.x = 2
        self.assertEqual(places.get(Point(1), "missing"), __)
        self.assertEqual(places.get(Point(2), "missing"), __)
        self.because(__)

    @expects("unhashable", hint="Say why a list is refused as a key, while a tuple of numbers is accepted.")
    def test_a_list_cannot_be_a_key(self):
        error = "none"
        try:
            {[]: "no"}
        except TypeError:
            error = "TypeError"
        self.assertEqual(error, __)
        pair = {(1, 2): "yes"}
        self.assertEqual(pair[(1, 2)], __)
        self.because(__)
