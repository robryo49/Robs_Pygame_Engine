from typing import Optional, cast

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject
from ..object import PygameObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2


class LayoutObjectFactory(SubObjectFactory):

    @staticmethod
    def _unpack_stack_item(item: PygameObject | tuple[PygameObject, int]) -> tuple[PygameObject, int]:
        if isinstance(item, tuple):
            if len(item) == 2:
                return item[0], item[1]
            raise ValueError(f"Object definition must be Obj or (Obj, span). Got {len(item)} elements")
        return item, 1

    @staticmethod
    def _unpack_grid_item(item: PygameObject | tuple[PygameObject, int] | tuple[PygameObject, int, int]) -> tuple[PygameObject, int, int]:
        if isinstance(item, tuple):
            if len(item) == 2:
                return cast(PygameObject, item[0]), cast(int, item[1]), 1
            if len(item) == 3:
                return cast(PygameObject, item[0]), cast(int, item[1]), cast(int, item[2])
            raise ValueError(f"Object definition must be Obj, (Obj, span_x), or (Obj, span_x, span_y). Got {len(item)} elements")
        return item, 1, 1

    def grid_layout(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None,
            invert_x=False, invert_y=False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        no_bg = style is None

        style = self._get_resource(style, RectStyle)
        obj = self._create_object(LayoutObject, position, rotation, scale, RectRenderer(vec2(), style, cache), layer, anchor)

        if width is not None:
            obj.set_fixed_width(width)
        if height is not None:
            obj.set_fixed_height(height)

        if invert_x:
            obj.flip_x = True
        if invert_y:
            obj.flip_y = True

        if no_bg:
            obj.skip_rendering()

        return obj
