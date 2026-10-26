"""
Factories for creating layout objects and populating them with objects.
"""

from typing import Any, Callable, Iterable, Optional

from .sub_object_factory import SubObjectFactory
from ..custom import FitMode, LayoutMode, LayoutObject
from ..object import PygameObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2


class LayoutObjectFactory(SubObjectFactory):
    """
    Create layout objects and arrange child objects in rows, columns, or grids.
    """

    def _create_layout[LT: LayoutObject](
            self, layout_type: type[LT], position: vec2, width: Optional[int] = None, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, *args
    ) -> LT:
        """
        Create a layout object and configure its sizing, modes, and background.

        :param layout_type: Layout class to instantiate.
        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :param args: Additional positional arguments passed to the layout constructor.
        :return: The created layout object.
        """
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

        if reorderable:
            obj.make_reorderable()

        if no_bg:
            obj.skip_rendering()

        return obj


    def grid_layout(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a grid layout with the given size, modes, and optional background.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """
        return self._create_layout(LayoutObject, position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

    def stack_in_row(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[PygameObject]] = None, cell_anchor: vec2 = Anchor.C,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a layout and add each object to the next cell in a row.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param objects: Objects to add in order.
        :param cell_anchor: Anchor used to place each object within its cell.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        if objects is not None:
            for obj in objects:
                layout.stack_x(obj, anchor=cell_anchor)

        return layout

    def stack_in_col(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[PygameObject]] = None, cell_anchor: vec2 = Anchor.C,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a layout and add each object to the next cell in a column.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param objects: Objects to add in order.
        :param cell_anchor: Anchor used to place each object within its cell.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        if objects is not None:
            for obj in objects:
                layout.stack_y(obj, anchor=cell_anchor)

        return layout

    def stack_in_grid(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a layout and place a two-dimensional iterable of objects into grid cells.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param objects: Rows of objects to place into grid cells.
        :param cell_anchor: Anchor used to place each object within its cell.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        if objects is not None:
            for y, row in enumerate(objects):
                for x, obj in enumerate(row):
                    layout.set_object_in_cell(obj, x, y, anchor=cell_anchor)

        layout.set_mode(mode)

        return layout

    def stack_in_cols(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
            fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a column-oriented grid layout from a two-dimensional iterable of objects.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param objects: Rows of objects to place into grid cells.
        :param cell_anchor: Anchor used to place each object within its cell.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """
        layout = self.stack_in_grid(position, width, height, objects, cell_anchor, LayoutObject.COL_MODE, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)
        return layout

    def stack_in_rows(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None, objects: Optional[Iterable[Iterable[PygameObject]]] = None, cell_anchor: vec2 = Anchor.C,
            fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a row-oriented grid layout from a two-dimensional iterable of objects.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param objects: Rows of objects to place into grid cells.
        :param cell_anchor: Anchor used to place each object within its cell.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """
        layout = self.stack_in_grid(position, width, height, objects, cell_anchor, LayoutObject.ROW_MODE, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)
        return layout

    def create_in_row(
            self, position: vec2, values: list[tuple[Any, vec2, tuple[Any, ...]]], constructors: dict[str, Callable[[Any, ...], PygameObject]],
            width: Optional[int] = None, height: Optional[int] = None, mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C, reorderable: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a layout and construct objects into consecutive columns using constructor callables.

        :param position: World-space position of the object.
        :param values: Tuples of object type, cell anchor, and constructor arguments.
        :param constructors: Mapping from object type keys to constructor callables.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        for x, (object_type, cell_anchor, args) in enumerate(values):
            constructor = constructors[object_type]
            layout.set_object_in_cell(constructor(*args), x, 0, anchor=cell_anchor)

        return layout

    def create_in_column(
            self, position: vec2, values: list[tuple[Any, vec2, tuple[Any, ...]]], constructors: dict[str, Callable[[Any, ...], PygameObject]],
            width: Optional[int] = None, height: Optional[int] = None, mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C, reorderable: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a layout and construct objects into consecutive rows using constructor callables.

        :param position: World-space position of the object.
        :param values: Tuples of object type, cell anchor, and constructor arguments.
        :param constructors: Mapping from object type keys to constructor callables.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        for y, (object_type, cell_anchor, args) in enumerate(values):
            constructor = constructors[object_type]
            layout.set_object_in_cell(constructor(*args), 0, y, anchor=cell_anchor)

        return layout

    def create_in_grid(
            self, position: vec2, grid_values: list[list[tuple[Any, vec2, tuple[Any, ...]]]], constructors: dict[str, Callable[[Any, ...], PygameObject]],
            width: Optional[int] = None, height: Optional[int] = None, mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C, reorderable: bool = False, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a layout and construct objects into a two-dimensional grid using constructor callables.

        :param position: World-space position of the object.
        :param grid_values: Rows of object type, cell anchor, and constructor argument tuples.
        :param constructors: Mapping from object type keys to constructor callables.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """

        layout = self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)

        for y, row in enumerate(grid_values):
            for x, (object_type, cell_anchor, args) in enumerate(row):
                constructor = constructors[object_type]
                layout.set_object_in_cell(constructor(*args), x, y, anchor=cell_anchor)

        return layout

    def __call__(
            self, position: vec2, width: Optional[int] = None, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.STRETCH_MODE, justification: vec2 = Anchor.C, reorderable: bool = False,
            style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LayoutObject:
        """
        Create a grid layout; alias for :meth:`grid_layout`.

        :param position: World-space position of the object.
        :param width: Fixed width of the layout.
        :param height: Fixed height of the layout.
        :param mode: Layout mode controlling cell arrangement.
        :param fit_mode: Fit mode used to size cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the layout.
        :param reorderable: Whether child objects can be reordered by dragging.
        :param style: Rectangle style or registered style name; the layout skips rendering when omitted.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created layout object.
        """
        return self.grid_layout(position, width, height, mode, fit_mode, overflow_mode, justification, reorderable, style, rotation, scale, layer, anchor, cache)