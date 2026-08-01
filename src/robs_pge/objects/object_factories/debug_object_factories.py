from typing import Optional

from .sub_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Transform, Vec2, inf, Color


class DebugObjectFactory(SubObjectFactory):
    
    def make_debug_panel(
            self, position: Vec2, dims: Vec2, style: DebugPanelStyle | str, title: str,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0,
            anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> DebugPanelObject:
        
        style = self._get_resource(style, DebugPanelStyle)
        
        width = round(dims.x)
        
        header_height = 4
        title_height = 30
        panel_height = round(dims.y - title_height - header_height)
        
        panel = self.factory.ui.layouts.make_grid_layout(Vec2(), width, panel_height, style=style.panel_style)
        title_panel = self.factory.shape.make_rect(Vec2(), Vec2(width, title_height), style=style.title_panel_style)
        header = self.factory.shape.make_rect(Vec2(), Vec2(width, header_height), style=style.header_style)
        title_text = self.factory.text.make_text(Vec2(8, -1), title.upper(), style.title_font, anchor=Anchor.L)
        
        title_panel.add_child(title_text, Anchor.L)
        
        layout = DebugPanelObject(
            Transform(position, rotation, scale),
            RectRenderer(Vec2(), None, cache),
            self.factory.services,
            panel,
            title_panel,
            header,
            title_text,
            layer,
            anchor
        ).skip_rendering()
        
        layout.fix_width(width)
        layout.fix_height(round(dims.y))
        
        layout.stack_y(panel)
        layout.stack_y(title_panel)
        layout.stack_y(header)
        
        return layout
    
    
    def make_debug_overlay(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> DebugOverlay:
        obj = DebugOverlay(
            Transform(position, rotation, scale),
            RectRenderer(Vec2(), RectStyle(Color(255, 255, 255, 200)), cache),
            self.factory.services, layer, anchor
        ).enable_rendering()
        
        obj.min_col = min_col
        obj.max_col = max_col
        obj.min_row = min_row
        obj.max_row = max_row
        
        if width is not None:
            obj.fix_width(width)
        if height is not None:
            obj.fix_height(height)
        
        if invert_x:
            obj.invert_left_right()
        if invert_y:
            obj.invert_up_down()
        
        return obj