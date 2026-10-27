from typing import Optional

from .music import Music


class Playlist:
    def __init__(self, name: str, musics: Optional[list[Music]] = None):
        self._name = name
        self._musics = musics or []

    # region PROPERTIES

    @property
    def name(self):
        return self._name

    @property
    def musics(self):
        return self._musics

    # endregion

    def add_music(self, music: Music):
        self._musics.append(music)

    def remove_music(self, music: Music):
        if music in self._musics:
            self._musics.remove(music)

    def __str__(self):
        return f"Playlist({self._name})"
