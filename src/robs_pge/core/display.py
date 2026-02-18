import pygame as pg

from ..utils import Color, Vec2, Vec2Like


class Display:
    def __init__(self, dims: Vec2Like):
        
        self._dims: Vec2 = Vec2(dims)
        
        self._surface: pg.Surface = pg.display.set_mode(self.dims, pg.SRCALPHA | pg.FULLSCREEN, vsync=True)
        
        self._clear_color: Color = Color(20, 30, 50)
        
    # region PROPERTIES
    
    @property
    def surface(self) -> pg.Surface:
        return self._surface
    
    @property
    def dims(self) -> Vec2:
        return self._dims
    
    @property
    def clear_color(self) -> Color:
        return self._clear_color
    
    # endregion
    
    def clear(self) -> "Display":
        self.surface.fill(self.clear_color)
        return self
    
    def update(self, dt: float) -> "Display":
        pg.display.flip()
        return self
    