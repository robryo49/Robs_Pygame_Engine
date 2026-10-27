from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import pygame as pg
from pygame.mixer import Sound

from .playlist import Playlist
from .music import Music

if TYPE_CHECKING:
    from ..resources import ResourceManager


class SoundManager:
    MUSIC_END_EVENT = pg.USEREVENT + 1

    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager

        self._playing_playlist: Optional[Playlist] = None
        self._playing_music: Optional[Music] = None
        self._playlist_index: int = 0
        self._playlist_loop: bool = True

        self._music_volume: float = 1.0
        self._global_volume: float = 1.0
        self._sound_volumes: dict[str, float] = {"main": 1.0}

        pg.mixer.music.set_volume(self._music_volume)
        pg.mixer.music.set_endevent(self.MUSIC_END_EVENT)

    # region PROPERTIES

    @property
    def playing_playlist(self):
        return self._playing_playlist

    @property
    def playing_music(self):
        return self._playing_music

    @property
    def playlist_index(self):
        return self._playlist_index

    @property
    def playlist_loop(self):
        return self._playlist_loop

    @property
    def music_volume(self):
        return self._music_volume
    
    @property
    def sound_volumes(self):
        return dict(self._sound_volumes)
        

    # endregion

    def handle_event(self, event: pg.event.Event):
        """Call this inside your main event loop when processing pg.QUIT, etc."""
        if event.type == self.MUSIC_END_EVENT:
            self._on_music_finished()

    # region HELPERS

    def _on_music_finished(self):
        """Handles advancing and queuing the next track when a playlist song ends."""
        if self._playing_playlist and self._playing_playlist.musics:
            self._playlist_index = (self._playlist_index + 1) % len(self._playing_playlist.musics)

            if self._playlist_index == 0 and not self._playlist_loop:
                self.stop_playlist()
                return

            next_index = (self._playlist_index + 1) % len(self._playing_playlist.musics)
            next_music = self._playing_playlist.musics[next_index]
            self._queue_music(next_music)

    @staticmethod
    def _start_music(music: Music, loops: int = 0, start: int = 0, fade_time: float = 0.0):
        pg.mixer.music.load(music.path)
        pg.mixer.music.play(loops, start, round(fade_time * 1000))

    @staticmethod
    def _queue_music(music: Music):
        pg.mixer.music.queue(music.path)

    # endregion

    # region MUSICS & PLAYLISTS

    def stop_music(self):
        pg.mixer.music.stop()
        self._playing_music = None

    def stop_playlist(self):
        self.stop_music()
        self._playing_playlist = None
        self._playlist_index = 0

    def play_playlist(self, playlist: Playlist | str, loop: bool = True, fade_time: float = 0.0):


        self.stop_playlist()

        if isinstance(playlist, str):
            playlist = self._resources.get_playlist(playlist)

        if not playlist or not playlist.musics:
            return

        self._playing_playlist = playlist
        self._playlist_loop = loop
        self._playlist_index = 0

        first_music = playlist.musics[0]
        self._start_music(first_music, loops=0, fade_time=fade_time)

        if len(playlist.musics) > 1:
            second_music = playlist.musics[1]
            self._queue_music(second_music)
        elif loop:
            self._start_music(first_music, loops=-1, fade_time=fade_time)

    def play_music(self, music: Music | str, loops: int = 0, start: int = 0, fade_time: float = 0.0):
        self.stop_playlist()
        if isinstance(music, str):
            music = self._resources.get_music(music)
        self._playing_music = music
        self._start_music(music, loops=loops, start=start, fade_time=fade_time)

    @staticmethod
    def pause_music():
        pg.mixer.music.pause()

    @staticmethod
    def unpause_music():
        pg.mixer.music.unpause()

    @staticmethod
    def rewind_music():
        """Rewinds the currently playing music track back to the beginning."""
        pg.mixer.music.rewind()

    def next_track(self):
        """Skips to the next track immediately if a playlist is currently playing."""
        if self._playing_playlist and self._playing_playlist.musics:
            self._playlist_index = (self._playlist_index + 1) % len(self._playing_playlist.musics)
            current_music = self._playing_playlist.musics[self._playlist_index]
            self._start_music(current_music)

            if len(self._playing_playlist.musics) > 1:
                next_index = (self._playlist_index + 1) % len(self._playing_playlist.musics)
                self._queue_music(self._playing_playlist.musics[next_index])

    # endregion

    # region VOLUME CONTROLS

    def set_music_volume(self, volume: float):
        """Sets music volume clamped between 0.0 and 1.0."""
        self._music_volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self._music_volume)

    def increase_music_volume(self, amount: float):
        """Increases music volume by a certain amount."""
        self.set_music_volume(self._music_volume + amount)

    def decrease_music_volume(self, amount: float):
        """Decreases music volume by a certain amount."""
        self.increase_music_volume(-amount)

    def get_music_volume(self) -> float:
        return self._music_volume

    def set_global_volume(self, volume: float):
        """Sets the global master volume factor clamped between 0.0 and 1.0."""
        self._global_volume = max(0.0, min(1.0, volume))

    def increase_global_volume(self, amount: float):
        """Increases global volume by a certain amount."""
        self.set_global_volume(self._global_volume + amount)

    def decrease_global_volume(self, amount: float):
        """Decreases global volume by a certain amount."""
        self.increase_global_volume(-amount)

    def get_global_volume(self) -> float:
        return self._global_volume

    def set_sound_volume(self, volume: float, category: str = "main"):
        """Sets sound volume for a specific category clamped between 0.0 and 1.0."""
        self._sound_volumes[category] = max(0.0, min(1.0, volume))

    def increase_sound_volume(self, amount: float, category: str = "main"):
        """Increases sound volume for a certain category by a certain amount."""
        current = self.get_sound_volume(category)
        self.set_sound_volume(current + amount, category)

    def decrease_sound_volume(self, amount: float, category: str = "main"):
        """Decreases sound volume for a certain category by a certain amount."""
        self.increase_sound_volume(-amount, category)

    def get_sound_volume(self, category: str = "main") -> float:
        """Returns the base volume of a sound category."""
        return self._sound_volumes.get(category, 1.0)

    # endregion

    # region SOUNDS

    def play_sound(self, sound: Sound | str, volume: float=1.0, loops: int = 0, max_time: float = 0.0, fade_time: float = 0.0, category: str = "main"):
        if isinstance(sound, str):
            sound = self._resources.get_sound(sound)

        category_volume = self.get_sound_volume(category)
        final_volume = category_volume * self._global_volume * volume

        sound.set_volume(final_volume)
        sound.play(loops, round(max_time * 1000), round(fade_time * 1000))

    # endregion