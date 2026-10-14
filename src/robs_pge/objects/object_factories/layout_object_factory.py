from typing import Any, Callable, Iterable, Literal, Optional, cast

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject
from ..object import PygameObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2


class LayoutObjectFactory(SubObjectFactory):
    
    def create_layout[LT: LayoutObject](
            self, layout_type: type[LT], position: vec2, width: Optional[int] = None, height: Optional[int] = None,
            mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, *args
    ) -> LT:
        no_bg = style is None

        style = self._get_resource(style, RectStyle)
        obj = self._create_object(layout_type, position, rotation, scale, RectRenderer(vec2(), style, cache), layer, anchor, *args)

        if width is not None:
            obj.set_fixed_width(width)
        if height is not None:
            obj.set_fixed_height(height)

        obj.mode = mode
        obj.fit_mode = fit_mode
        obj.overflow_mode = overflow_mode
        obj.justification = justification

        if no_bg:
            obj.skip_rendering()

        return obj


    def grid_layout(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None,
            mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        return self.create_layout(LayoutObject, position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

    def stack_in_row(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[PygameObject]] = None, cell_anchor: vec2 = Anchor.C,
            mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        if objects is not None:
            for obj in objects:
                layout.stack_x(obj, anchor=cell_anchor)

        return layout

    def stack_in_col(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[PygameObject]] = None, cell_anchor: vec2 = Anchor.C, style: StyleOrName[RectStyle] = None,
            mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        if objects is not None:
            for obj in objects:
                layout.stack_y(obj, anchor=cell_anchor)

        return layout

    def stack_in_grid(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
            mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        if objects is not None:
            for y, row in enumerate(objects):
                for x, obj in enumerate(row):
                    layout.set_object_in_cell(obj, x, y, anchor=cell_anchor)

        layout.set_mode(mode)

        return layout

    def stack_in_cols(
        self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
        fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
        overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
        style: StyleOrName[RectStyle] = None,
        rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        layout = self.stack_in_grid(position, width, height, objects, cell_anchor, LayoutObject.COL_MODE, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)
        return layout

    def stack_in_rows(
        self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
        fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
        overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
        style: StyleOrName[RectStyle] = None,
        rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        layout = self.stack_in_grid(position, width, height, objects, cell_anchor, LayoutObject.GRID_MODE, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)
        return layout

    def create_in_row(
            self, position: vec2, values: list[tuple[Any, vec2, tuple[Any, ...]]], constructors: dict[str, Callable[[Any, ...], PygameObject]],
            width: Optional[int] = None, height: Optional[int] = None, mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C, reorderable: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        for x, (object_type, cell_anchor, args) in enumerate(values):
            constructor = constructors[object_type]
            layout.set_object_in_cell(constructor(*args), x, 0, anchor=cell_anchor)

        return layout

    def create_in_column(
            self, position: vec2, values: list[tuple[Any, vec2, tuple[Any, ...]]], constructors: dict[str, Callable[[Any, ...], PygameObject]],
            width: Optional[int] = None, height: Optional[int] = None, mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C, reorderable: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        for y, (object_type, cell_anchor, args) in enumerate(values):
            constructor = constructors[object_type]
            layout.set_object_in_cell(constructor(*args), 0, y, anchor=cell_anchor)

        return layout

    def create_in_grid(
            self, position: vec2, grid_values: list[list[tuple[Any, vec2, tuple[Any, ...]]]], constructors: dict[str, Callable[[Any, ...], PygameObject]],
            width: Optional[int] = None, height: Optional[int] = None, mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C, reorderable: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        for y, row in enumerate(grid_values):
            for x, (object_type, cell_anchor, args) in enumerate(row):
                constructor = constructors[object_type]
                layout.set_object_in_cell(constructor(*args), x, y, anchor=cell_anchor)

        return layout

    def __call__(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None,
            mode: LayoutObject.Mode = LayoutObject.GRID_MODE, fit_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: LayoutObject.FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        return self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)