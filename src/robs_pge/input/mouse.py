from __future__ import annotations
from typing import TYPE_CHECKING

import pygame as pg

from ..utils import Transform, vec2

if TYPE_CHECKING:
    from ..core import Camera


class Mouse:
    def __init__(self):
        
        self._transform: Transform = Transform(vec2(pg.mouse.get_pos()))
        self._movement: vec2 = vec2(pg.mouse.get_rel())
        self._scroll: int = 0
        
        self._pressed_buttons: set[int] = set()
        self._held_buttons: dict[int, int]  = {}
        self._released_buttons: set[int] = set()
    
    # region PROPERTIES
    
    @property
    def transform(self) -> Transform:
        return self._transform
    
    @property
    def pos(self) -> vec2:
        return self.transform.pos
    
    @property
    def movement(self) -> vec2:
        return self._movement
    
    @property
    def scroll(self) -> int:
        return self._scroll
    
    @property
    def pressed_buttons(self) -> set[int]:
        return self._pressed_buttons
    
    @property
    def held_buttons(self) -> dict[int, int]:
        return self._held_buttons
    
    @property
    def released_buttons(self) -> set[int]:
        return self._released_buttons
    
    # endregion
    
    def world_pos(self, camera: Camera) -> vec2:
        return camera.screen_to_world_pos(self.pos)
    
    def update(self)  -> Mouse:
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
        if event.type == pg.MOUSEBUTTONDOWN:
            self.pressed_buttons.add(event.button)
        elif event.type == pg.MOUSEBUTTONUP:
            self.released_buttons.add(event.button)
        elif event.type == pg.MOUSEWHEEL:
            self._scroll = event.y
        return self
        

    def pressed(self, button: int) -> bool:
        return button in self.pressed_buttons
    
    def held(self, button: int) -> bool:
        return button in self.held_buttons
    
    def hold_duration(self, button: int) -> int:
        return self.held_buttons.get(button, 0)
    
    def released(self, button: int) -> bool:
        return button in self.released_buttons