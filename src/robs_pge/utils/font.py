from typing import Optional

import pygame as pg

from .color import Color
from .math_tools import vec2


class Font:
    def __init__(self, name="dejavusansmono", size=24, color: Optional[Color] = None, bold=False, italic=False, line_spacing=0):
        
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
    
    def _with(self, **kwargs):
        args = {"name": self.name, "size": self.size, "color": self.color, "bold": self.bold, "italic": self.italic, "line_spacing": self.line_spacing}
        args.update(kwargs)
        return Font(**args)
    
    def copy(self):
        return Font(self.name, self.size, self.color, self.bold, self.italic, self.line_spacing)
    
    def get_render_size(self, text):
        return vec2(self._pg_font.size(text))
    