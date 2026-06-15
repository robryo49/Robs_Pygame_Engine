import pygame as pg

from core import Camera
from utils import Transform, Vec2


class Mouse:
    def __init__(self):
        
        self._transform: Transform = Transform(Vec2(pg.mouse.get_pos()))
        self._movement: Vec2 = Vec2(pg.mouse.get_rel())
        self._scroll: int = 0
        
        self._pressed_buttons: set[int] = set()
        self._held_buttons: dict[int, int]  = {}
        self._released_buttons: set[int] = set()
    
    # region PROPERTIES
    
    @property
    def transform(self) -> Transform:
        return self._transform
    
    @property
    def pos(self) -> Vec2:
        return self.transform.pos
    
    @property
    def movement(self) -> Vec2:
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
    
    def world_pos(self, camera: Camera) -> Vec2:
        return camera.screen_to_world_pos(self.pos)
    
    def update(self)  -> "Mouse":
        self.transform.pos = Vec2(pg.mouse.get_pos())
        self._movement = Vec2(pg.mouse.get_rel())
        
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
    
    def process_event(self, event: pg.Event) -> "Mouse":
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