# Axiom: an iterable produces a new iterator when iteration starts. An iterator yields until it is exhausted, and it is its own iterator.

from koans.engine import Koan, blank, expects

__ = blank


class AboutIteration(Koan):
    @expects("new iterator", hint="Say what each call to iter on a list returns.")
    def test_a_list_gives_a_fresh_iterator(self):
        nums = [1, 2, 3]
        left = iter(nums)
        right = iter(nums)
        self.assertEqual(next(left), __)
        self.assertEqual(next(right), __)
        self.assertEqual(iter(nums) is nums, __)
        self.because(__)

    # Bridge: a JS array can be walked twice. A Python iterator is spent after one pass. A list is an iterable, not an iterator.
    @expects("exhausted", hint="Say what a second pass over one iterator finds.")
    def test_an_iterator_is_spent_after_one_pass(self):
        nums = [1, 2, 3]
        walker = iter(nums)
        self.assertEqual(list(walker), __)
        self.assertEqual(list(walker), __)
        self.assertEqual(list(nums), __)
        self.because(__)

    @expects("itself", hint="Say what iter returns when its argument is a generator.")
    def test_a_generator_is_its_own_iterator(self):
        gen = (n for n in [1, 2])
        self.assertEqual(iter(gen) is gen, __)
        self.assertEqual(next(gen), __)
        self.assertEqual(list(gen), __)
        self.because(__)
