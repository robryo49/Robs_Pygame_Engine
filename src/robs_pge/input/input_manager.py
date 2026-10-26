"""Aggregates keyboard and mouse state from pygame events and per-frame updates."""

import pygame as pg

from .mouse import Mouse
from ..utils import vec2


class InputManager:
    """Tracks pressed, held, and released keyboard keys alongside mouse input."""

    def __init__(self) -> None:
        """Initialize empty keyboard state and an internal mouse tracker."""
        self._pressed_keys: set[int] = set()
        self._held_keys: dict[int, int] = {}
        self._released_keys: set[int] = set()
        
        self._mouse: Mouse = Mouse()
        
    # region PROPERTIES
    
    @property
    def pressed_keys(self) -> set[int]:
        """Return the keys pressed during the current frame."""
        return self._pressed_keys
    
    @property
    def held_keys(self) -> dict[int, int]:
        """Return the held keys mapped to their hold duration in frames."""
        return self._held_keys
    
    @property
    def released_keys(self) -> set[int]:
        """Return the keys released during the current frame."""
        return self._released_keys

    @property
    def pressed_buttons(self) -> set[int]:
        """Return the mouse buttons pressed during the current frame."""
        return self.mouse.pressed_buttons
    
    @property
    def held_buttons(self) -> dict[int, int]:
        """Return the held mouse buttons mapped to their hold duration in frames."""
        return self.mouse.held_buttons
    
    @property
    def released_buttons(self) -> set[int]:
        """Return the mouse buttons released during the current frame."""
        return self.mouse.released_buttons
    
    @property
    def mouse(self) -> Mouse:
        """Return the tracked mouse state."""
        return self._mouse
    
    @property
    def mouse_pos(self) -> vec2:
        """Return the current mouse position in screen coordinates."""
        return self.mouse.pos
    
    @property
    def mouse_movement(self) -> vec2:
        """Return the mouse movement since the previous update."""
        return self.mouse.movement
    
    @property
    def mouse_scroll(self) -> int:
        """Return the mouse wheel scroll amount for the current frame."""
        return self.mouse.scroll
    
    # endregion
    
    def update(self) -> "InputManager":
        """
        Advance hold durations, clear per-frame key state, and update the mouse.

        :return: this manager
        """
        for key in list(self.held_keys):
            self.held_keys[key] += 1
        for key in list(self.pressed_keys):
            self.held_keys[key] = 0
        for key in list(self.released_keys):
            self.held_keys.pop(key, None)
            
        self.pressed_keys.clear()
        self.released_keys.clear()
        
        self.mouse.update()
        return self
        
    def process_event(self, event: pg.Event) -> "InputManager":
        """
        Update keyboard and mouse state from a pygame event.

        :param event: pygame event to process
        :return: this manager
        """
        if event.type == pg.KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == pg.KEYUP:
            self.released_keys.add(event.key)
        
        self.mouse.process_event(event)
        return self
            
    def pressed_key(self, key: int) -> bool:
        """
        Return whether a key was pressed during the current frame.

        :param key: pygame key constant
        :return: ``True`` if the key was pressed
        """
        return key in self.pressed_keys
    
    def pressed_button(self, button: int) -> bool:
        """
        Return whether a mouse button was pressed during the current frame.

        :param button: pygame mouse button constant
        :return: ``True`` if the button was pressed
        """
        return self.mouse.pressed(button)
    
    def pressed(self, kb) -> bool:
        """
        Return whether a key or mouse button was pressed during the current frame.

        :param kb: pygame key or mouse button constant
        :return: ``True`` if either the key or button was pressed
        """
        return self.pressed_key(kb) or self.pressed_button(kb)
    
    
    def held_key(self, key:int) -> bool:
        """
        Return whether a key is currently held.

        :param key: pygame key constant
        :return: ``True`` if the key is held
        """
        return key in self.held_keys
    
    def held_button(self, button:int) -> bool:
        """
        Return whether a mouse button is currently held.

        :param button: pygame mouse button constant
        :return: ``True`` if the button is held
        """
        return self.mouse.held(button)
    
    def held(self, kb) -> bool:
        """
        Return whether a key or mouse button is currently held.

        :param kb: pygame key or mouse button constant
        :return: ``True`` if either the key or button is held
        """
        return self.held_key(kb) or self.held_button(kb)
    
    
    def key_hold_duration(self, key:int) -> int:
        """
        Return how many frames a key has been held.

        :param key: pygame key constant
        :return: hold duration in frames, or 0 when not held
        """
        return self.held_keys.get(key, 0)
    
    def button_hold_duration(self, button:int) -> int:
        """
        Return how many frames a mouse button has been held.

        :param button: pygame mouse button constant
        :return: hold duration in frames, or 0 when not held
        """
        return self.mouse.hold_duration(button)
    
    
    def released_key(self, key:int) -> bool:
        """
        Return whether a key was released during the current frame.

        :param key: pygame key constant
        :return: ``True`` if the key was released
        """
        return key in self.released_keys
    
    def released_button(self, button:int) -> bool:
        """
        Return whether a mouse button was released during the current frame.

        :param button: pygame mouse button constant
        :return: ``True`` if the button was released
        """
        return self.mouse.released(button)
    
    def released(self, kb) -> bool:
        """
        Return whether a key or mouse button was released during the current frame.

        :param kb: pygame key or mouse button constant
        :return: ``True`` if either the key or button was released
        """
        return self.released_key(kb) or self.released_button(kb)
    
