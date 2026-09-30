# Axiom: a sequence you write yourself is an object with the protocol methods. len, indexing, iteration, and == call those methods.

from koans.engine import Koan, blank, expects
from koans.student_work import Playlist

__ = blank


class AboutTransfer(Koan):
    @expects("__len__", hint="Say which method len calls on your type.")
    def test_length_follows_the_tracks(self):
        playlist = Playlist(["a", "b"])
        self.assertEqual(len(playlist), 2)
        playlist.add("c")
        self.assertEqual(len(playlist), 3)
        self.because(__)

    @expects("__getitem__", hint="Say which method indexing calls.")
    def test_indexing_returns_the_track(self):
        playlist = Playlist(["a", "b", "c"])
        self.assertEqual(playlist[0], "a")
        self.assertEqual(playlist[-1], "c")
        self.because(__)

    @expects("__iter__", hint="Say which method a for-loop uses to walk your type.")
    def test_iteration_yields_tracks_in_order(self):
        playlist = Playlist(["a", "b"])
        self.assertEqual(list(playlist), ["a", "b"])
        self.assertEqual(list(Playlist()), [])
        self.because(__)

    # Bridge: Java == would compare identity here. Python == calls the method you implement, and it compares track values.
    @expects("__eq__", hint="Say which method == calls, and what it compares.")
    def test_equality_compares_tracks_not_identity(self):
        left = Playlist(["a", "b"])
        right = Playlist(["a", "b"])
        self.assertTrue(left == right)
        self.assertFalse(left is right)
        self.assertFalse(left == Playlist(["a"]))
        self.assertFalse(left == ["a", "b"])
        self.because(__)
