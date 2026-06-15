import pygame as pg

from utils import Vec2, Vec2Like, Color, Colors


class Display:
    def __init__(self, dims: Vec2Like):
        
        self._dims: Vec2 = Vec2(dims)
        
        self._surface: pg.Surface = pg.display.set_mode(self.dims, pg.SRCALPHA | pg.FULLSCREEN, vsync=True)
        
        self._clear_color: Color = Colors.DARK_NAVY
        
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
    