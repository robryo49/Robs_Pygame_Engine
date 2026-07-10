from typing import Optional

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, Vec2, inf


class LayoutObjectFactory(SubObjectFactory):
    def make_grid_layout(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        
        style = self._get_resource(style, RectStyle)
        obj = self._make_object(LayoutObject, position, rotation, scale, RectRenderer(Vec2(), style, cache), layer, anchor)
        
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
    
    def make_vertical_layout(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_row=0, max_row=inf, invert_y=False, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.make_grid_layout(
            position, width, height, 0, 0, min_row, max_row, False, invert_y,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_horizontal_layout(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_col=0, max_col=inf, invert_x=False, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.make_grid_layout(
            position, width, height, min_col, max_col, 0, 0, invert_x, False,
            style, rotation, scale, layer, anchor, cache
        )