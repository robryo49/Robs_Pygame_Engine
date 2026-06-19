import pygame as pg

from utils import Vec2, Vec2Like, Color, Colors


class Display:
    def __init__(self, dims: Vec2Like, fullscreen: bool = True, vsync: bool = True, clear_color: Color = Colors.DARK_NAVY):
        
        self._dims: Vec2 = Vec2(dims)
        
        self._surface: pg.Surface = pg.display.set_mode(self.dims, (pg.SRCALPHA | pg.FULLSCREEN) if fullscreen else pg.SRCALPHA, vsync=vsync)
        
        self._clear_color: Color = clear_color
        
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
    