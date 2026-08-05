import pygame as pg

from .mouse import Mouse
from ..utils import vec2


class InputManager:
    def __init__(self):
        
        self._pressed_keys: set[int] = set()
        self._held_keys: dict[int, int] = {}
        self._released_keys: set[int] = set()
        
        self._mouse: Mouse = Mouse()
        
    # region PROPERTIES
    
    @property
    def pressed_keys(self) -> set[int]:
        return self._pressed_keys
    
    @property
    def held_keys(self) -> dict[int, int]:
        return self._held_keys
    
    @property
    def released_keys(self) -> set[int]:
        return self._released_keys

    @property
    def pressed_buttons(self) -> set[int]:
        return self.mouse.pressed_buttons
    
    @property
    def held_buttons(self) -> dict[int, int]:
        return self.mouse.held_buttons
    
    @property
    def released_buttons(self) -> set[int]:
        return self.mouse.released_buttons
    
    @property
    def mouse(self) -> Mouse:
        return self._mouse
    
    @property
    def mouse_pos(self) -> vec2:
        return self.mouse.pos
    
    @property
    def mouse_movement(self) -> vec2:
        return self.mouse.movement
    
    @property
    def mouse_scroll(self) -> int:
        return self.mouse.scroll
    
    # endregion
    
    def update(self) -> "InputManager":
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
        if event.type == pg.KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == pg.KEYUP:
            self.released_keys.add(event.key)
        
        self.mouse.process_event(event)
        return self
            
    def pressed_key(self, key: int) -> bool:
        return key in self.pressed_keys
    
    def pressed_button(self, button: int) -> bool:
        return self.mouse.pressed(button)
    
    def pressed(self, kb) -> bool:
        return self.pressed_key(kb) or self.pressed_button(kb)
    
    
    def held_key(self, key:int) -> bool:
        return key in self.held_keys
    
    def held_button(self, button:int) -> bool:
        return self.mouse.held(button)
    
    def held(self, kb) -> bool:
        return self.held_key(kb) or self.held_button(kb)
    
    
    def key_hold_duration(self, key:int) -> int:
        return self.held_keys.get(key, 0)
    
    def button_hold_duration(self, button:int) -> int:
        return self.mouse.hold_duration(button)
    
    
    def released_key(self, key:int) -> bool:
        return key in self.released_keys
    
    def released_button(self, button:int) -> bool:
        return self.mouse.released(button)
    
    def released(self, kb) -> bool:
        return self.released_key(kb) or self.released_button(kb)
    
