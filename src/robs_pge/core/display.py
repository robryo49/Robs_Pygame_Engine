import pygame as pg
from pyglm.glm import vec2

from ..utils import Color, Colors, ScreenAnchor


class Display:
    def __init__(self, dims: vec2, vsync: bool = True, clear_color: Color = Colors.DARK_NAVY):
        
        self._screen_dims: vec2 = vec2(pg.display.get_desktop_sizes()[0])
        self._viewport_dims: vec2 = vec2(dims)
        
        self._s2v_ratios: vec2 = self.viewport_dims / self.screen_dims
        self._v2s_ratios: vec2 = self.screen_dims / self.viewport_dims
        
        self._surface: pg.Surface = pg.display.set_mode(self._screen_dims, (pg.SRCALPHA | pg.FULLSCREEN), vsync=vsync)
        ScreenAnchor.set_screen_dims(self._viewport_dims)
        
        self._clear_color: Color = clear_color
        
    # region PROPERTIES
    
    @property
    def surface(self) -> pg.Surface:
        return self._surface
    
    # region dims
    
    @property
    def screen_dims(self) -> vec2:
        return self._screen_dims
    
    @property
    def screen_width(self) -> float:
        return self.screen_dims.x
    
    @property
    def screen_height(self) -> float:
        return self.screen_dims.y
    
    
    @property
    def screen_center_x(self) -> float:
        return self.screen_width * 0.5
    
    @property
    def screen_center_y(self) -> float:
        return self.screen_height * 0.5
    
    @property
    def screen_center(self) -> vec2:
        return self.screen_dims * 0.5
    
    
    
    @property
    def viewport_dims(self) -> vec2:
        return self._viewport_dims
    
    @property
    def viewport_width(self) -> float:
        return self.viewport_dims.x
    
    @property
    def viewport_height(self) -> float:
        return self.viewport_dims.y
    
    @property
    def viewport_center_x(self) -> float:
        return self.viewport_width * 0.5
    
    @property
    def viewport_center_y(self) -> float:
        return self.viewport_height * 0.5
    
    @property
    def viewport_center(self) -> vec2:
        return self.viewport_dims * 0.5
    
    # endregion
    
    
    @property
    def clear_color(self) -> Color:
        return self._clear_color
    
    # endregion
    
    # region Coordinate Conversion Methods
    
    def screen_to_viewport_pos(self, screen_pos: vec2) -> vec2: return screen_pos * self._s2v_ratios
    def screen_to_viewport_vec(self, screen_vec: vec2) -> vec2: return screen_vec * self._s2v_ratios
    
    def viewport_to_screen_pos(self, viewport_pos: vec2) -> vec2: return viewport_pos * self._v2s_ratios
    def viewport_to_screen_vec(self, viewport_vec: vec2) -> vec2: return viewport_vec * self._v2s_ratios
    
    # endregion
    
    def clear(self) -> "Display":
        self.surface.fill(self.clear_color)
        return self
    
    def update(self, dt: float) -> "Display":
        pg.display.flip()
        return self
    