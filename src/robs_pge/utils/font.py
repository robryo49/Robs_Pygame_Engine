import pygame as pg

from .color import Color
from .math import Vec2


class Font:
    def __init__(self, name="dejavusansmono", size=24, color: Color = None, bold=False, italic=False, line_spacing=0):
        
        self.name = name
        self.size = size
        self.color = color or Color(0, 0, 0)
        self.bold = bold
        self.italic = italic
        self.line_spacing = line_spacing
        
        self._pg_font = pg.font.SysFont(self.name, self.size, self.bold, self.italic)
        
    # region PROPERTIES
    
    @property
    def key(self):
        return self.name, tuple(self.color), self.bold, self.italic
    
    @property
    def pg_font(self):
        return self._pg_font
    
    # endregion
    
    def get_render_size(self, text):
        return Vec2(self._pg_font.size(text))
    