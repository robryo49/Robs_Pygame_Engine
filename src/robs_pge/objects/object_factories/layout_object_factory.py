from typing import Any, Callable, Optional, cast

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject
from ..object import PygameObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2, inf, validate_signature


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
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, min_col=0, max_col=inf, min_row=0, max_row=inf,
            invert_x=False, invert_y=False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        
        no_bg = style is None
        
        style = self._get_resource(style, RectStyle)
        obj = self._create_object(LayoutObject, position, rotation, scale, RectRenderer(vec2(), style, cache), layer, anchor)
        
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
            
        if no_bg: obj.skip_rendering()
        
        return obj
    
    def vertical_layout(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, min_row=0, max_row=inf, invert_y=False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.grid_layout(
            position, width, height, 0, 0, min_row, max_row, False, invert_y,
            style, rotation, scale, layer, anchor, cache
        )
    
    def horizontal_layout(
            self, position: vec2, width: Optional[float] = None, height: Optional[float] = None, min_col=0, max_col=inf, invert_x=False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.grid_layout(
            position, width, height, min_col, max_col, 0, 0, invert_x, False,
            style, rotation, scale, layer, anchor, cache
        )
    
    def object_stack[T: PygameObject](
            self, position: vec2, object_constructor: Callable[..., T], data: dict[str, list[Any]], horizontal: bool = False, invert_y: bool = False, invert_x=False,
            width: Optional[float] = None, height: Optional[float] = None, spacing: int = 10, margin: Optional[int] = None, style: StyleOrName[RectStyle] = None, object_grid_anchors: vec2 = Anchor.C,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        
        validate_signature(object_constructor, None, data)
        
        length = max((len(d) for d in data.values()), default=0)
        
        layout = self.vertical_layout(
            position, width, height, 0, inf, invert_y, style, rotation, scale, layer, anchor, cache
        ) if not horizontal else self.horizontal_layout(
            position, width, height, 0, inf, invert_x, style, rotation, scale, layer, anchor, cache
        )
        
        stack = layout.stack_y if not horizontal else layout.stack_x
        
        data["grid_anchor"] = data.get("grid_anchor", [object_grid_anchors])
        
        for i in range(length):
            
            d = {key: values[min(i, len(values)-1)] for key, values in data.items()}
            grid_anchor = d.pop("grid_anchor")
            obj = object_constructor(vec2(), **d)
            stack(obj, anchor=grid_anchor)
            
        if margin is None:
            layout.set_constant_padding(spacing)
        else:
            layout.set_cell_padding(spacing/2)
            if margin-spacing/2 > 0: layout.set_outer_padding(margin-spacing/2)
        
        return layout
    
    def stack_objects_in_grid(
            self, position: vec2, objects: list[list[PygameObject | tuple[PygameObject, int] | tuple[PygameObject, int, int]]],
            align_columns: bool = True, align_rows: bool = True, cell_anchor: vec2 = Anchor.C,
            width: Optional[float] = None, height: Optional[float] = None, spacing: int = 10, margin: Optional[int] = None,
            invert_x: bool = False, invert_y: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
    
        if not align_columns and not align_rows:
            raise ValueError("align_columns and align_rows can't both be False")
        
        if align_columns and align_rows:
            layout = self.grid_layout(position, width, height, 0, inf, 0, inf, invert_x, invert_y, style, rotation, scale, layer, anchor, cache)
            
            for y, row_objects in enumerate(objects):
                for x, item in enumerate(row_objects):
                    obj, span_x, span_y = self._unpack_grid_item(item)
                    layout.add_object(obj, x, y, span_x, span_y, cell_anchor)
            
            if margin is None:
                layout.set_constant_padding(spacing)
            else:
                layout.set_cell_padding(spacing/2)
                if margin-spacing/2 > 0:
                    layout.set_outer_padding(margin-spacing/2)
            
            return layout
        
        elif align_rows:
            layout = self.vertical_layout(position, width, height, 0, inf, invert_y, style, rotation, scale, layer, anchor, cache)
            
            for row_objects in objects:
                row_objects_no_span = list(self._unpack_grid_item(item)[0] for item in row_objects)
                row = self.stack_objects_horizontal(vec2(), row_objects_no_span, cell_anchor)
                row.set_cell_padding(spacing/2)
                layout.stack_y(row, anchor=cell_anchor)
            
            if margin is None:
                layout.set_outer_padding(spacing/2)
            elif margin-spacing/2 > 0:
                layout.set_outer_padding(margin-spacing/2)
            
            return layout
        
        else:
            layout = self.horizontal_layout(position, width, height, 0, inf, invert_x, style, rotation, scale, layer, anchor, cache)
            
            num_cols = max((len(r) for r in objects), default=0)
            for col in range(num_cols):
                col_objects = [row_objects[col] for row_objects in objects if col < len(row_objects)]
                col_objects_no_span = list(self._unpack_grid_item(item)[0] for item in col_objects)
                column = self.stack_objects_vertical(vec2(), col_objects_no_span, cell_anchor)
                column.set_cell_padding(spacing/2)
                layout.stack_x(column, anchor=cell_anchor)
            
            if margin is None:
                layout.set_outer_padding(spacing/2)
            elif margin-spacing/2 > 0:
                layout.set_outer_padding(margin-spacing/2)
            
            return layout
    
    def stack_objects_vertical(
            self, position: vec2, objects: list[PygameObject | tuple[PygameObject, int]],
            cell_anchor: vec2 = Anchor.C, width: Optional[float] = None, height: Optional[float] = None,
            spacing: int = 10, margin: Optional[int] = None, invert_y: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        
        layout = self.vertical_layout(position, width, height, 0, inf, invert_y, style, rotation, scale, layer, anchor, cache)
        
        for item in objects:
            obj, span_x = self._unpack_stack_item(item)
            layout.stack_y(obj, span_x=span_x, anchor=cell_anchor)
            
        if margin is None:
            layout.set_constant_padding(spacing)
        else:
            layout.set_cell_padding(spacing/2)
            if margin-spacing/2 > 0:
                layout.set_outer_padding(margin-spacing/2)
        
        return layout
    
    def stack_objects_horizontal(
            self, position: vec2, objects: list[PygameObject | tuple[PygameObject, int]],
            cell_anchor: vec2 = Anchor.C, width: Optional[float] = None, height: Optional[float] = None, spacing: int = 10, margin: Optional[int] = None, invert_x: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        
        layout = self.horizontal_layout(position, width, height, 0, inf, invert_x, style, rotation, scale, layer, anchor, cache)
        
        for item in objects:
            obj, span_y = self._unpack_stack_item(item)
            layout.stack_x(obj, span_y=span_y, anchor=cell_anchor)
            
        if margin is None:
            layout.set_constant_padding(spacing)
        else:
            layout.set_cell_padding(spacing/2)
            if margin-spacing/2 > 0:
                layout.set_outer_padding(margin-spacing/2)
        
        return layout
    