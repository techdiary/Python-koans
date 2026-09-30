"""The transfer project. Implement Playlist. The tests in about_transfer.py are already written.

Playlist stores track names in order.

- Playlist() starts empty. Playlist(tracks) copies those tracks.
- add(track) appends one track.
- len(playlist) is the number of tracks.
- playlist[index] accepts the same indexes as a list, including negative indexes.
- Iteration yields tracks from first to last.
- playlist == other is true only when other is a Playlist with the same tracks in the same order.
- Comparing a Playlist to a non-Playlist is false.
"""


class Playlist:
    def __init__(self, tracks=()):
        raise NotImplementedError

    def add(self, track):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def __getitem__(self, index):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError
