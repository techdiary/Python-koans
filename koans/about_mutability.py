# Axiom: a list can change in place. A tuple cannot. Rebinding a name is separate from mutating an object. An immutable container can still hold a mutable object.

from koans.engine import Koan, blank, expects

__ = blank


class AboutMutability(Koan):
    @expects("in place", hint="Say whether += built a new list or changed the original.")
    def test_plus_equals_mutates_a_list(self):
        nums = [1, 2]
        other = nums
        nums += [3]
        self.assertEqual(nums, __)
        self.assertEqual(other, __)
        self.assertEqual(nums is other, __)
        self.because(__)

    @expects("rebind", hint="Say whether the original tuple object gained an element.")
    def test_plus_equals_rebinds_a_tuple(self):
        pair = (1, 2)
        other = pair
        pair += (3,)
        self.assertEqual(pair, __)
        self.assertEqual(other, __)
        self.assertEqual(pair is other, __)
        self.because(__)

    # Bridge: Java final and JS const freeze the variable, not the object graph. A tuple freezes its sequence of references, not the objects those references point at.
    @expects("inner", hint="Say which object the append changed.")
    def test_a_tuple_does_not_freeze_what_it_holds(self):
        shell = ([],)
        replaced = False
        try:
            shell[0] = ["no"]
            replaced = True
        except TypeError:
            replaced = False
        shell[0].append("yes")
        self.assertEqual(replaced, __)
        self.assertEqual(shell, __)
        self.because(__)
