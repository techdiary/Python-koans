# Axiom: unpacking is assignment. It binds names to objects already in the sequence. A slice of a list is a new list, and the copy is shallow.

from koans.engine import Koan, blank, expects

__ = blank


class AboutSequences(Koan):
    @expects("bind", hint="Say what unpacking does to names.")
    def test_unpacking_binds_names(self):
        first, second, *rest = [1, 2, 3, 4]
        self.assertEqual(first, __)
        self.assertEqual(second, __)
        self.assertEqual(rest, __)
        self.because(__)

    # Bridge: Java charAt returns a char. Indexing a Python string returns a one-character string.
    @expects("string", hint="Say what type one element of a text sequence has.")
    def test_a_string_is_a_sequence_of_strings(self):
        first, second = "go"
        self.assertEqual(first, __)
        self.assertEqual(type(first).__name__, __)
        self.assertEqual(len(first), __)
        self.because(__)

    # Bridge: Java List.subList is a view of the same list. Python slicing builds a new list and still shares the inner objects.
    @expects("shallow", hint="Say what the slice copied and what the two lists still share.")
    def test_a_slice_is_a_new_list_and_the_copy_is_shallow(self):
        base = [1, 2, 3]
        sliced = base[:]
        sliced.append(4)
        self.assertEqual(base, __)
        nested = [[1], [2]]
        copied = nested[:]
        copied[0].append(9)
        self.assertEqual(nested, __)
        self.assertEqual(copied[0] is nested[0], __)
        self.because(__)

    @expects("left to right", hint="Say in which order the targets are bound.")
    def test_targets_are_bound_left_to_right(self):
        nums = [0, 1]
        index = 0
        index, nums[index] = 1, 2
        self.assertEqual(index, __)
        self.assertEqual(nums, __)
        self.because(__)
