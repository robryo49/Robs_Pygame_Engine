from typing import Optional

from .sub_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Transform, inf, vec2


class DebugObjectFactory(SubObjectFactory):
    
    def make_debug_overlay(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool=True
    ) -> DebugOverlay:
        obj = DebugOverlay(
            Transform(position, rotation, scale),
            RectRenderer(vec2(), None, cache),
            self.factory.services, layer, anchor
        ).skip_rendering()
        
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