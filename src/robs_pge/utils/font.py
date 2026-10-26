"""Font configuration backed by a pygame system font."""

from typing import Optional

import pygame as pg

from .color import Color
from .math import vec2
from .management_tools import Style


class Font(Style):
    """Font configuration backed by a pygame system font."""

    def __init__(self, name: str = "dejavusansmono", size: int = 24, color: Optional[Color] = None, bold: bool = False, italic: bool = False, line_spacing: int = 0) -> None:
        """Create a font style and load the matching pygame system font.

        :param name: System font name passed to pygame.
        :param size: Font size in pixels.
        :param color: Text color, defaulting to black when omitted.
        :param bold: Whether to use the bold font variant.
        :param italic: Whether to use the italic font variant.
        :param line_spacing: Extra spacing between rendered lines.
        """
        self.name = name
        self.size = size
        self.color = color or Color(0, 0, 0)
        self.bold = bold
        self.italic = italic
        self.line_spacing = line_spacing
        
        self._pg_font = pg.font.SysFont(self.name, self.size, self.bold, self.italic)
        
    # region PROPERTIES
    
    @property
    def key(self) -> tuple[str, tuple[int, ...], bool, bool]:
        """Return the cache key describing this font's rendering configuration."""
        return self.name, tuple(self.color), self.bold, self.italic

    @property
    def pg_font(self) -> pg.font.Font:
        """Return the underlying pygame font used for rendering."""
        return self._pg_font
    
    # endregion
    
    def _with(self, **kwargs) -> Font:
        """Build a new font from this style with selected fields overridden.

        :param kwargs: Font constructor fields to replace.
        :return: A new font with the merged configuration.
        """
        args = {
            "name": self.name,
            "size": self.size,
            "color": self.color,
            "bold": self.bold,
            "italic": self.italic,
            "line_spacing": self.line_spacing,
        }
        args.update(kwargs)
        return Font(**args)

    def with_(self, **kwargs) -> Font:
        """Return a copy with the supplied fields replaced.

        :param kwargs: Font constructor fields to replace.
        :return: A new font with the merged configuration.
        """
        return self._with(**kwargs)

    def copy(self) -> Font:
        """Return an independent copy of this font style.

        :return: A new font with the same configuration.
        """
        return self._with()

    def get_render_size(self, text: str) -> vec2:
        """Measure the size of text when rendered with this font.

        :param text: Text to measure.
        :return: The width and height in pixels.
        """
        return vec2(self._pg_font.size(text))

    @staticmethod
    def get_all_fonts() -> list[str]:
        """Return the names of fonts available to pygame.

        :return: A list of available system font names.
        """
        return pg.font.get_fonts()
    