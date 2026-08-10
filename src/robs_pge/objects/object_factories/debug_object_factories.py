from typing import Optional

from pygame import Color

from .sub_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Transform, inf, vec2


class DebugObjectFactory(SubObjectFactory):

    def debug_overlay(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None,
            invert_x=False, invert_y=False,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> DebugOverlay:
        obj = DebugOverlay(
            Transform(position, rotation, scale),
            RectRenderer(vec2(), RectStyle(Color(255, 255, 255, 100), 10, Color(255, 255, 255, 200)), cache),
            self.factory.services, layer, anchor
        ).skip_rendering()

        if invert_x:
            obj.flip_x = True
        if invert_y:
            obj.flip_y = True

        return obj