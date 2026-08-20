from typing import Optional, Callable, Any

from pygame import Color

from .sub_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Transform, vec2, StyleOrName


class DebugObjectFactory(SubObjectFactory):

    def debug_overlay(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> DebugOverlay:
        obj = DebugOverlay(
            Transform(position, rotation, scale),
            RectRenderer(vec2(), RectStyle(Color(255, 255, 255, 100), 10, Color(255, 255, 255, 200)), cache),
            self.factory.services, layer, anchor
        ).skip_rendering()
        obj.set_mode(obj.COL_MODE)
        obj.set_fit_mode(obj.PRESERVE_MODE)
        obj.set_justify(Anchor.TL)

        if width is not None:
            obj.set_fixed_width(width)
        if height is not None:
            obj.set_fixed_height(height)

        return obj
    
    def debug_info_window(
            self, position: vec2, title: str, width: int,
            title_column_width: Optional[int] = None, value_column_width: Optional[int] = None,
            title_font: StyleOrName[Font] = None, value_font: StyleOrName[Font] = None, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> DebugInfoWindow:
        
        title_font = self._get_resource(title_font, Font)
        value_font = self._get_resource(value_font, Font)
        
        title_factory = lambda t: self.factory.text.label(vec2(), t, title_font, cache=False)
        value_factory = lambda t, g: self.factory.text.dynamic_label(vec2(), t, g, value_font, cache=False)
        
        window = self.factory.window.create_window(
            DebugInfoWindow, position, title, width, None, DebugInfoWindow.GRID_MODE, DebugInfoWindow.STRETCH_MODE, DebugInfoWindow.STRETCH_MODE, Anchor.T, False,
            style, rotation, scale, layer, anchor, cache, title_factory, value_factory
        )
        
        if title_column_width is not None:
            window.content.set_fixed_col_width(title_column_width, 0)
        if value_column_width is not None:
            window.content.set_fixed_col_width(value_column_width, 1)
        
        return window
    
    def dynamic_debug_info_window(
            self, position: vec2, title: str, width: int, values_getter: Callable[[], dict[str, Any]],
            title_column_width: Optional[int] = None, value_column_width: Optional[int] = None,
            title_font: StyleOrName[Font] = None, value_font: StyleOrName[Font] = None, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ):
        window = self.factory.window.regular(
            position, title, width, None, DebugInfoWindow.GRID_MODE, DebugInfoWindow.STRETCH_MODE, DebugInfoWindow.STRETCH_MODE, Anchor.T, False,
            style, rotation, scale, layer, anchor, cache
        )
        
        window.stack_content_x(self.factory.text.dynamic_label(vec2(), "{}", lambda: "\n".join(str(v) for v in values_getter().keys()), font=title_font), anchor=Anchor.TL)
        window.stack_content_x(self.factory.text.dynamic_label(vec2(), "{}", lambda: "\n".join(str(v) for v in values_getter().values()), font=value_font), anchor=Anchor.TL)
        
        if title_column_width is not None:
            window.content.set_fixed_col_width(title_column_width, 0)
        if value_column_width is not None:
            window.content.set_fixed_col_width(value_column_width, 1)
        
        return window
        