"""Tracks mouse position, movement, scroll, and button states across frames."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from ..utils import Transform, vec2

if TYPE_CHECKING:
    from ..core import Camera


class Mouse:
    """Snapshots mouse state and tracks per-frame button transitions."""

    def __init__(self) -> None:
        """Initialize mouse state from the current pygame mouse position and movement."""
        self._transform: Transform = Transform(vec2(pg.mouse.get_pos()))
        self._movement: vec2 = vec2(pg.mouse.get_rel())
        self._scroll: int = 0
        
        self._pressed_buttons: set[int] = set()
        self._held_buttons: dict[int, int]  = {}
        self._released_buttons: set[int] = set()
    
    # region PROPERTIES
    
    @property
    def transform(self) -> Transform:
        """Return the transform holding the mouse position in screen coordinates."""
        return self._transform
    
    @property
    def pos(self) -> vec2:
        """Return the mouse position in screen coordinates."""
        return self.transform.pos
    
    @property
    def movement(self) -> vec2:
        """Return the mouse movement since the previous update."""
        return self._movement
    
    @property
    def scroll(self) -> int:
        """Return the mouse wheel scroll amount for the current frame."""
        return self._scroll
    
    @property
    def pressed_buttons(self) -> set[int]:
        """Return the mouse buttons pressed during the current frame."""
        return self._pressed_buttons
    
    @property
    def held_buttons(self) -> dict[int, int]:
        """Return the held mouse buttons mapped to their hold duration in frames."""
        return self._held_buttons
    
    @property
    def released_buttons(self) -> set[int]:
        """Return the mouse buttons released during the current frame."""
        return self._released_buttons
    
    # endregion
    
    def world_pos(self, camera: Camera) -> vec2:
        """
        Convert the current screen position to world coordinates.

        :param camera: camera used for the conversion
        :return: mouse position in world coordinates
        """
        return camera.screen_to_world_pos(self.pos)
    
    def update(self)  -> Mouse:
        """
        Refresh position and movement, advance hold durations, and clear per-frame state.

        :return: this mouse tracker
        """
        self.transform.pos = vec2(pg.mouse.get_pos())
        self._movement = vec2(pg.mouse.get_rel())
        
        for button in list(self.held_buttons):
            self.held_buttons[button] += 1
        for button in list(self.pressed_buttons):
            self.held_buttons[button] = 0
        for button in list(self.released_buttons):
            self.held_buttons.pop(button, None)
            
        self.pressed_buttons.clear()
        self.released_buttons.clear()
        self._scroll = 0
        return self
    
    def process_event(self, event: pg.Event) -> Mouse:
        """
        Update button and scroll state from a pygame event.

        :param event: pygame event to process
        :return: this mouse tracker
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            self.pressed_buttons.add(event.button)
        elif event.type == pg.MOUSEBUTTONUP:
            self.released_buttons.add(event.button)
        elif event.type == pg.MOUSEWHEEL:
            self._scroll = event.y
        return self
        

    def pressed(self, button: int) -> bool:
        """
        Return whether a mouse button was pressed during the current frame.

        :param button: pygame mouse button constant
        :return: ``True`` if the button was pressed
        """
        return button in self.pressed_buttons
    
    def held(self, button: int) -> bool:
        """
        Return whether a mouse button is currently held.

        :param button: pygame mouse button constant
        :return: ``True`` if the button is held
        """
        return button in self.held_buttons
    
    def hold_duration(self, button: int) -> int:
        """
        Return how many frames a mouse button has been held.

        :param button: pygame mouse button constant
        :return: hold duration in frames, or 0 when not held
        """
        return self.held_buttons.get(button, 0)
    
    def released(self, button: int) -> bool:
        """
        Return whether a mouse button was released during the current frame.

        :param button: pygame mouse button constant
        :return: ``True`` if the button was released
        """
        return button in self.released_buttons