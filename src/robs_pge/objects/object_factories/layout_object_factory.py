from typing import Iterable, Literal, Optional, cast

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject
from ..object import PygameObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2


class LayoutObjectFactory(SubObjectFactory):

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
    
    def stack_horizontal(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, objects: Optional[Iterable[PygameObject]] = None, cell_anchor: vec2 = Anchor.C,
            invert_x=False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ):
        
        layout = self.grid_layout(position, width, height, invert_x, False, style, rotation, scale, layer, anchor, cache)
        
        if objects is not None:
            for obj in objects:
                layout.stack_x(obj, anchor=cell_anchor)
        
        return layout
    
    def stack_vertical(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, objects: Optional[Iterable[PygameObject]] = None, cell_anchor: vec2 = Anchor.C,
            invert_y=False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ):
        
        layout = self.grid_layout(position, width, height, False, invert_y, style, rotation, scale, layer, anchor, cache)
        
        if objects is not None:
            for obj in objects:
                layout.stack_y(obj, anchor=cell_anchor)
        
        return layout
    
    def stack_in_grid(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
            mode: Literal["grid", "rows", "columns"] = LayoutObject.GRID_MODE, invert_x=False, invert_y: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ):
        
        layout = self.grid_layout(position, width, height, invert_x, invert_y, style, rotation, scale, layer, anchor, cache)
        
        if objects is not None:
            for y, row in enumerate(objects):
                for x, obj in enumerate(row):
                    layout.add(obj, x, y, anchor=cell_anchor)
        
        layout.mode = mode
        
        return layout
