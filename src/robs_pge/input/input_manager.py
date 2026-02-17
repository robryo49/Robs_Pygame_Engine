import pygame as pg

from .mouse import Mouse


class InputManager:
    def __init__(self):
        
        self._pressed_keys: set[int] = set()
        self._held_keys: dict[int, int] = {}
        self._released_keys: set[int] = set()
        
        self._mouse = Mouse()
        
    # region PROPERTIES
    
    @property
    def pressed_keys(self):
        return self._pressed_keys
    
    @property
    def held_keys(self):
        return self._held_keys
    
    @property
    def released_keys(self):
        return self._released_keys

    @property
    def pressed_buttons(self):
        return self.mouse.pressed_buttons
    
    @property
    def held_buttons(self):
        return self.mouse.held_buttons
    
    @property
    def released_buttons(self):
        return self.mouse.released_buttons
    
    @property
    def mouse(self):
        return self._mouse
    
    @property
    def mouse_pos(self):
        return self.mouse.pos
    
    @property
    def mouse_movement(self):
        return self.mouse.movement
    
    @property
    def mouse_scroll(self):
        return self.mouse.scroll
    
    # endregion
    
    def update(self):
        for key in list(self.held_keys):
            self.held_keys[key] += 1
        for key in list(self.pressed_keys):
            self.held_keys[key] = 0
        for key in list(self.released_keys):
            self.held_keys.pop(key, None)
            
        self.pressed_keys.clear()
        self.released_keys.clear()
        
        self.mouse.update()
        
    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            self.pressed_keys.add(event.key)
        elif event.type == pg.KEYUP:
            self.released_keys.add(event.key)
        
        self.mouse.process_event(event)
            
    def pressed_key(self, key: int):
        return key in self.pressed_keys
    
    def pressed_button(self, button: int):
        return self.mouse.pressed(button)
    
    def pressed(self, kb):
        return self.pressed_key(kb) or self.pressed_button(kb)
    
    
    def held_key(self, key:int):
        return key in self.held_keys
    
    def held_button(self, button:int):
        return self.mouse.held(button)
    
    def held(self, kb):
        return self.held_key(kb) or self.held_button(kb)
    
    
    def key_hold_duration(self, key:int):
        return self.held_keys.get(key, 0)
    
    def button_hold_duration(self, button:int):
        return self.mouse.hold_duration(button)
    
    
    def released_key(self, key:int):
        return key in self.released_keys
    
    def released_button(self, button:int):
        return self.mouse.released(button)
    
    def released(self, kb):
        return self.released_key(kb) or self.released_button(kb)
    
    

