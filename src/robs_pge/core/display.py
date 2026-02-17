import pygame as pg

from ..utils import Color, Vec2


class Display:
    def __init__(self, dims: Vec2):
        
        self._dims = dims
        
        self._surface = pg.display.set_mode(self.dims, pg.SRCALPHA | pg.FULLSCREEN, vsync=True)
        
        self._clear_color = Color(20, 30, 50)
        
    # region PROPERTIES
    
    @property
    def surface(self):
        return self._surface
    
    @property
    def dims(self):
        return self._dims
    
    @property
    def clear_color(self):
        return self._clear_color
    
    # endregion
    
    def clear(self):
        self.surface.fill(self.clear_color)
    
    @staticmethod
    def update():
        pg.display.flip()
    