"""Grid, row, and column layout object with configurable sizing, spacing, anchors, and placement operations."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Literal, Optional, TYPE_CHECKING, cast

from .shape_objects import RectObject
from ..behaviors import ReorderableLayoutBehavior, LayoutBehaviorManager
from ..object import PygameObject
from ...rendering import RectRenderer, RectStyle
from ...utils import Anchor, Transform, vec2

if TYPE_CHECKING:
    from ...core import ServicesCollection

CellPos = tuple[int, int]
FitMode = Literal["stretch", "preserve"]
LayoutMode = Literal["grid", "columns", "rows"]
LayeringPriority = Optional[Literal[
    "left_right_top_bottom", "left_right_bottom_top", "right_left_top_bottom", "right_left_bottom_top",
    "top_bottom_left_right", "top_bottom_right_left", "bottom_top_left_right", "bottom_top_right_left"
]]

@dataclass
class SizeConstraint:
    """Minimum, maximum, and fixed bounds applied to a single size value."""
    min: Optional[int] = None
    max: Optional[int] = None
    fixed: Optional[int] = None
    
    def apply(self, value: int) -> int:
        """
        Return the value after applying the fixed, minimum, or maximum bound.

        :param value: Size value to constrain.
        :return: The constrained size value.
        """
        if self.fixed is not None:
            return self.fixed
        if self.min is not None and value < self.min:
            return self.min
        if self.max is not None and value > self.max:
            return self.max
        return value
    
    def __iter__(self):
        """
        Iterate over the minimum, maximum, and fixed bounds in that order.

        :return: An iterator over the three bound values.
        """
        return iter([self.min, self.max, self.fixed])
    
    def copy(self):
        """
        Return a copy of the constraint.

        :return: A new constraint with the same bounds.
        """
        return SizeConstraint(self.min, self.max, self.fixed)


class LayoutObject(RectObject):
    """Layout container that arranges child objects in grid, row, or column tracks."""
    GRID_MODE: Literal["grid"] = "grid"
    COL_MODE: Literal["columns"] = "columns"
    ROW_MODE: Literal["rows"] = "rows"
    
    STRETCH_MODE: Literal["stretch"] = "stretch"
    PRESERVE_MODE: Literal["preserve"] = "preserve"

    LAYER_PRIORITY_LEFT_RIGHT_TOP_BOTTOM: Literal["left_right_top_bottom"] = "left_right_top_bottom"
    LAYER_PRIORITY_LEFT_RIGHT_BOTTOM_TOP: Literal["left_right_bottom_top"] = "left_right_bottom_top"
    LAYER_PRIORITY_RIGHT_LEFT_TOP_BOTTOM: Literal["right_left_top_bottom"] = "right_left_top_bottom"
    LAYER_PRIORITY_RIGHT_LEFT_BOTTOM_TOP: Literal["right_left_bottom_top"] = "right_left_bottom_top"
    LAYER_PRIORITY_TOP_BOTTOM_LEFT_RIGHT: Literal["top_bottom_left_right"] = "top_bottom_left_right"
    LAYER_PRIORITY_TOP_BOTTOM_RIGHT_LEFT: Literal["top_bottom_right_left"] = "top_bottom_right_left"
    LAYER_PRIORITY_BOTTOM_TOP_LEFT_RIGHT: Literal["bottom_top_left_right"] = "bottom_top_left_right"
    LAYER_PRIORITY_BOTTOM_TOP_RIGHT_LEFT: Literal["bottom_top_right_left"] = "bottom_top_right_left"

    # Layout capabilities - override in subclasses to customize behavior
    _supports_spans: bool = True
    _supports_spanning_cuts: bool = True
    _max_span_resolution_iterations: int = 16

    # region INIT / STATE
    
    def __init__(self, transform: Transform, renderer: RectRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the layout and all of its track and constraint state.

        :param transform: Transform applied to the layout.
        :param renderer: Rectangle renderer used by the layout.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the layout.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
        
        self._object_placements: dict[PygameObject, CellPos] = {}
        self._object_spans: dict[PygameObject, tuple[int, int]] = {}
        self._cells_objects: dict[CellPos, PygameObject] = {}
        
        self._dirty = False
        self._dirty_checking = True
        self._dirty_checking_values: dict[PygameObject, tuple[vec2, vec2, vec2]] = {}
        self._dirty_checking_blacklist: set[PygameObject] = set()
        self._object_positioning_blacklist: set[PygameObject] = set()
        
        self._max_col = 0
        self._max_cols: dict[int, int] = {}
        self._next_cols: dict[int, int] = {}
        self._max_row = 0
        self._max_rows: dict[int, int] = {}
        self._next_rows: dict[int, int] = {}
        
        self._mode: LayoutMode = self.GRID_MODE
        self._justification = Anchor.C
        self._layering_priority: LayeringPriority = None
        
        self._fit_mode: FitMode = self.STRETCH_MODE
        self._horizontal_fit_mode: Optional[FitMode] = None
        self._vertical_fit_mode: Optional[FitMode] = None
        self._col_horizontal_fit_modes: dict[int, FitMode] = {}
        self._row_vertical_fit_modes: dict[int, FitMode] = {}
        
        self._overflow_mode: FitMode = self.STRETCH_MODE
        self._horizontal_overflow_mode: Optional[FitMode] = None
        self._vertical_overflow_mode: Optional[FitMode] = None
        self._col_horizontal_overflow_modes: dict[int, FitMode] = {}
        self._row_vertical_overflow_modes: dict[int, FitMode] = {}
        
        self._cell_anchor: vec2 = Anchor.C
        self._cell_anchors: dict[CellPos, vec2] = {}
        
        self._content_offset = vec2()
        
        self._width_constraint = SizeConstraint()
        self._height_constraint = SizeConstraint()
        self._col_width_constraint = SizeConstraint()
        self._col_widths_constraints: dict[int, SizeConstraint] = {}
        self._row_height_constraint = SizeConstraint()
        self._row_heights_constraints: dict[int, SizeConstraint] = {}
        
        self._outer_padding = vec2()
        self._cell_spacing = vec2()
        self._cell_padding = vec2()
        self._cell_paddings: dict[CellPos, vec2] = {}
        
        self._calculated_width: int = 0
        self._calculated_height: int = 0
        self._calculated_col_widths: dict[int, int] = {}
        self._calculated_row_heights: dict[int, int] = {}
        self._row_mode_calculated_col_widths: dict[int, dict[int, int]] = {}
        self._col_mode_calculated_row_heights: dict[int, dict[int, int]] = {}
        
        self._calculated_col_offsets: dict[int, int] = {}
        self._calculated_row_offsets: dict[int, int] = {}
        self._row_mode_calculated_col_offsets: dict[int, dict[int, int]] = {}
        self._col_mode_calculated_row_offsets: dict[int, dict[int, int]] = {}
        
        self._calculated_row_widths: int = 0
        self._calculated_col_heights: int = 0
        self._row_mode_calculated_row_widths: dict[int, int] = {}
        self._col_mode_calculated_col_heights: dict[int, int] = {}
    
    def _create_behavior_manager(self) -> LayoutBehaviorManager:
        return LayoutBehaviorManager(self)
    
    # endregion
    
    # region PROPERTIES
    
    @property
    def dirty(self) -> bool:
        """Return whether the layout needs to be recalculated."""
        return self._dirty

    @property
    def width_constraint(self) -> SizeConstraint:
        """Return a copy of the width size constraint."""
        return self._width_constraint.copy()

    @property
    def height_constraint(self) -> SizeConstraint:
        """Return a copy of the height size constraint."""
        return self._height_constraint.copy()
    
    @property
    def mode(self) -> Literal["grid", "columns", "rows"]:
        """Return the current layout mode."""
        return cast(Literal["grid", "columns", "rows"], self._mode)
    
    @mode.setter
    def mode(self, value: Literal["grid", "columns", "rows"]):
        """
        Set the layout mode and mark the layout dirty.

        :param value: The new value.
        """
        self._mode = value
        self.mark_dirty()
    
    @property
    def behaviors(self) -> LayoutBehaviorManager:
        """Return the layout behavior manager."""
        return self._behaviors
    
    @property
    def justification(self) -> vec2:
        """Return the content justification vector."""
        return vec2(self._justification)
    
    @justification.setter
    def justification(self, value: vec2 | int):
        """
        Set the content justification vector and mark the layout dirty.

        :param value: The new value.
        """
        self._justification = vec2(value)
        self.mark_dirty()
    
    @property
    def outer_padding(self) -> vec2:
        """Return the outer padding vector."""
        return vec2(self._outer_padding)
    
    @outer_padding.setter
    def outer_padding(self, value: vec2 | int):
        """
        Set the outer padding vector and mark the layout dirty.

        :param value: The new value.
        """
        self._outer_padding = vec2(value)
        self.mark_dirty()
    
    @property
    def cell_spacing(self) -> vec2:
        """Return the spacing between cells."""
        return vec2(self._cell_spacing)
    
    @cell_spacing.setter
    def cell_spacing(self, value: vec2 | int):
        """
        Set the spacing between cells and mark the layout dirty.

        :param value: The new value.
        """
        self._cell_spacing = vec2(value)
        self.mark_dirty()
    
    @property
    def cell_padding(self) -> vec2:
        """Return the padding inside cells."""
        return vec2(self._cell_padding)
    
    @cell_padding.setter
    def cell_padding(self, value: vec2 | int):
        """
        Set the padding inside cells and mark the layout dirty.

        :param value: The new value.
        """
        self._cell_padding = vec2(value)
        self.mark_dirty()
    
    @property
    def content_offset(self) -> vec2:
        """Return the content offset vector."""
        return vec2(self._content_offset)
    
    @content_offset.setter
    def content_offset(self, value: vec2 | int):
        """
        Set the content offset vector and mark the layout dirty.

        :param value: The new value.
        """
        self._content_offset = vec2(value)
        self.mark_dirty()
    
    @property
    def content_offset_x(self) -> float:
        """Return the horizontal content offset."""
        return self._content_offset.x
    
    @content_offset_x.setter
    def content_offset_x(self, value: float):
        """
        Set the horizontal content offset and mark the layout dirty.

        :param value: The new value.
        """
        self._content_offset.x = value
        self.mark_dirty()
    
    @property
    def content_offset_y(self) -> float:
        """Return the vertical content offset."""
        return self._content_offset.y
    
    @content_offset_y.setter
    def content_offset_y(self, value: float):
        """
        Set the vertical content offset and mark the layout dirty.

        :param value: The new value.
        """
        self._content_offset.y = value
        self.mark_dirty()
    
    @property
    def fit_mode(self) -> FitMode:
        """Return the mode used when content is smaller than the layout."""
        return cast(FitMode, self._fit_mode)
    
    @fit_mode.setter
    def fit_mode(self, value: FitMode):
        """
        Set the fit mode and mark the layout dirty.

        :param value: The new value.
        """
        self._fit_mode = value
        self.mark_dirty()
    
    @property
    def overflow_mode(self) -> FitMode:
        """Return the mode used when content is larger than the layout."""
        return cast(FitMode, self._overflow_mode)
    
    @overflow_mode.setter
    def overflow_mode(self, value: FitMode):
        """
        Set the overflow mode and mark the layout dirty.

        :param value: The new value.
        """
        self._overflow_mode = value
        self.mark_dirty()
    
    @property
    def horizontal_fit_mode(self) -> FitMode:
        """Return the effective horizontal fit mode."""
        return cast(FitMode, self._horizontal_fit_mode or self._fit_mode)
    
    @horizontal_fit_mode.setter
    def horizontal_fit_mode(self, value: Optional[FitMode]):
        """
        Set the horizontal fit mode and mark the layout dirty.

        :param value: The new value.
        """
        self._horizontal_fit_mode = value
        self.mark_dirty()
    
    @property
    def vertical_fit_mode(self) -> FitMode:
        """Return the effective vertical fit mode."""
        return cast(FitMode, self._vertical_fit_mode or self._fit_mode)
    
    @vertical_fit_mode.setter
    def vertical_fit_mode(self, value: Optional[FitMode]):
        """
        Set the vertical fit mode and mark the layout dirty.

        :param value: The new value.
        """
        self._vertical_fit_mode = value
        self.mark_dirty()
    
    @property
    def horizontal_overflow_mode(self) -> FitMode:
        """Return the effective horizontal overflow mode."""
        return cast(FitMode, self._horizontal_overflow_mode or self._overflow_mode)
    
    @horizontal_overflow_mode.setter
    def horizontal_overflow_mode(self, value: Optional[FitMode]):
        """
        Set the horizontal overflow mode and mark the layout dirty.

        :param value: The new value.
        """
        self._horizontal_overflow_mode = value
        self.mark_dirty()
    
    @property
    def vertical_overflow_mode(self) -> FitMode:
        """Return the effective vertical overflow mode."""
        return cast(FitMode, self._vertical_overflow_mode or self._overflow_mode)
    
    @vertical_overflow_mode.setter
    def vertical_overflow_mode(self, value: Optional[FitMode]):
        """
        Set the vertical overflow mode and mark the layout dirty.

        :param value: The new value.
        """
        self._vertical_overflow_mode = value
        self.mark_dirty()
    
    @property
    def max_col(self) -> int:
        """Return the highest occupied column index."""
        return self._max_col
    
    @property
    def max_cols(self) -> dict[int, int]:
        """Return a copy of the maximum column index per row."""
        return dict(self._max_cols)
    
    @property
    def max_row(self) -> int:
        """Return the highest occupied row index."""
        return self._max_row
    
    @property
    def max_rows(self) -> dict[int, int]:
        """Return a copy of the maximum row index per column."""
        return dict(self._max_rows)
    
    @property
    def object_spans(self) -> dict[PygameObject, tuple[int, int]]:
        """Return a copy of the span of every placed object."""
        return dict(self._object_spans)
    
    @property
    def objects(self) -> tuple[PygameObject, ...]:
        """Return the placed objects as a tuple."""
        return tuple(self._object_placements)

    @property
    def placed_objects(self) -> tuple[PygameObject, ...]:
        """Return the placed objects as a tuple (alias for clarity in subclasses)."""
        return tuple(self._object_placements)

    @property
    def layout_mode(self) -> LayoutMode:
        """Return the current layout mode (alias for clarity in subclasses)."""
        return self.mode
    
    # endregion
    
    # region HELPERS
    
    # region cell / span lookups
    
    def _get_cell_padding(self, cell: Optional[CellPos] = None) -> vec2:
        return self._cell_paddings.get(cell, self._cell_padding) if cell is not None else self._cell_padding
    
    def _get_cell_anchor(self, cell: CellPos) -> vec2:
        return self._cell_anchors.get(cell, self._cell_anchor)
    
    def _get_span(self, obj: PygameObject) -> tuple[int, int]:
        return self._object_spans.get(obj, (1, 1))

    @staticmethod
    def _validate_span(span: tuple[int, int]) -> tuple[int, int]:
        sx, sy = span
        if sx < 1 or sy < 1:
            raise ValueError("span_x and span_y must both be >= 1")
        return int(sx), int(sy)
    
    @staticmethod
    def _indices_between(start: int, span: int) -> list[int]:
        return list(range(start, start + span))

    def _span_cells(self, cell: CellPos, span: tuple[int, int]) -> list[CellPos]:
        col, row = cell
        sx, sy = span
        return [(col + i, row + j) for j in range(sy) for i in range(sx)]
    
    def _object_cells(self, obj: PygameObject) -> list[CellPos]:
        return self._span_cells(self._object_placements[obj], self._get_span(obj))
    
    def _calculate_cell_dims(self, obj: PygameObject, cell: CellPos) -> tuple[int, int]:
        pad = self._get_cell_padding(cell)
        return round(obj.dims.x + 2 * pad.x), round(obj.dims.y + 2 * pad.y)
    
    # endregion
    
    # region fit / overflow mode resolution
    
    def _get_fit_mode(self, horizontal: bool) -> FitMode:
        if horizontal:
            if self._horizontal_fit_mode is not None:
                return cast(FitMode, self._horizontal_fit_mode)
        else:
            if self._vertical_fit_mode is not None:
                return cast(FitMode, self._vertical_fit_mode)
        return cast(FitMode, self._fit_mode)
    
    def _get_overflow_mode(self, horizontal: bool) -> FitMode:
        if horizontal:
            if self._horizontal_overflow_mode is not None:
                return cast(FitMode, self._horizontal_overflow_mode)
        else:
            if self._vertical_overflow_mode is not None:
                return cast(FitMode, self._vertical_overflow_mode)
        return cast(FitMode, self._overflow_mode)
    
    def _get_col_fit_mode(self, col: int) -> FitMode:
        return self._col_horizontal_fit_modes.get(col, self._get_fit_mode(True))
    
    def _get_row_fit_mode(self, row: int) -> FitMode:
        return self._row_vertical_fit_modes.get(row, self._get_fit_mode(False))
    
    def _get_col_overflow_mode(self, col: int) -> FitMode:
        return self._col_horizontal_overflow_modes.get(col, self._get_overflow_mode(True))
    
    def _get_row_overflow_mode(self, row: int) -> FitMode:
        return self._row_vertical_overflow_modes.get(row, self._get_overflow_mode(False))
    
    def _should_stretch(self, col: int, row: int) -> bool:
        return (self._get_col_fit_mode(col) == self.STRETCH_MODE or self._get_col_overflow_mode(col) == self.STRETCH_MODE or
                self._get_row_fit_mode(row) == self.STRETCH_MODE or self._get_row_overflow_mode(row) == self.STRETCH_MODE)
    
    # endregion
    
    # region size constraints
    
    def _apply_col_width_constraints(self, col: int, width: int) -> int:
        constraint = self._col_widths_constraints.get(col)
        return constraint.apply(width) if constraint is not None else self._col_width_constraint.apply(width)
    
    def _apply_row_height_constraints(self, row: int, height: int) -> int:
        constraint = self._row_heights_constraints.get(row)
        return constraint.apply(height) if constraint is not None else self._row_height_constraint.apply(height)
    
    def _get_col_constraint(self, col: Optional[int]) -> SizeConstraint:
        if col is None:
            return self._col_width_constraint
        return self._col_widths_constraints.setdefault(col, SizeConstraint())
    
    def _get_row_constraint(self, row: Optional[int]) -> SizeConstraint:
        if row is None:
            return self._row_height_constraint
        return self._row_heights_constraints.setdefault(row, SizeConstraint())
    
    # endregion
    
    # region fitting math
    
    @staticmethod
    def _calculate_offsets(dimensions: dict[int, int], spacing: int) -> dict[int, int]:
        offsets: dict[int, int] = {}
        offset = 0
        for index in sorted(dimensions):
            offsets[index] = offset
            offset += dimensions[index] + spacing
        return offsets
    
    @staticmethod
    def _calculate_total_size(dimensions: dict[int, int], spacing: int) -> int:
        if not dimensions:
            return 0
        return sum(dimensions.values()) + spacing * (len(dimensions) - 1)
    
    @staticmethod
    def _fit_dimensions(dimensions: dict[int, int], target_size: int, spacing: int, constraints: dict[int, SizeConstraint], default_constraint: SizeConstraint,
                        stretch: bool, stretch_indices: Optional[set[int]] = None) -> None:
        return LayoutObject._distribute_track_space(dimensions, target_size, spacing, constraints, default_constraint, stretch, stretch_indices)

    @staticmethod
    def _distribute_track_space(dimensions: dict[int, int], target_size: int, spacing: int, constraints: dict[int, SizeConstraint], default_constraint: SizeConstraint,
                                stretch: bool, stretch_indices: Optional[set[int]] = None) -> None:
        if not dimensions or not stretch:
            return

        target_size = max(0, target_size - spacing * (len(dimensions) - 1))
        indices = sorted(dimensions)
        active = set(indices) if stretch_indices is None else set(indices) & set(stretch_indices)
        if not active:
            return

        current_size = sum(dimensions.values())
        if current_size == target_size:
            return

        if target_size > current_size:
            remaining = target_size - current_size
            while remaining > 0 and active:
                total_weight = sum(max(dimensions[i], 1) for i in active)
                if total_weight <= 0:
                    break

                changes: dict[int, int] = {}
                consumed = 0
                constrained: set[int] = set()

                for index in active:
                    old_size = dimensions[index]
                    ideal = remaining * max(old_size, 1) / total_weight
                    proposed = old_size + ideal
                    constraint = constraints.get(index, default_constraint)
                    constrained_size = constraint.apply(round(proposed))
                    delta = max(0, constrained_size - old_size)
                    changes[index] = delta
                    if constrained_size < round(proposed):
                        constrained.add(index)

                for index, delta in changes.items():
                    dimensions[index] += delta
                    consumed += delta

                if consumed <= 0:
                    break
                remaining -= consumed
                active -= constrained
        else:
            remaining = current_size - target_size
            while remaining > 0 and active:
                total_weight = sum(max(dimensions[i], 1) for i in active)
                if total_weight <= 0:
                    break

                changes: dict[int, int] = {}
                consumed = 0
                constrained: set[int] = set()

                for index in active:
                    old_size = dimensions[index]
                    ideal = remaining * max(old_size, 1) / total_weight
                    proposed = old_size - ideal
                    constraint = constraints.get(index, default_constraint)
                    constrained_size = constraint.apply(round(proposed))
                    delta = max(0, old_size - constrained_size)
                    changes[index] = delta
                    if constrained_size > round(proposed):
                        constrained.add(index)

                for index, delta in changes.items():
                    dimensions[index] -= delta
                    consumed += delta

                if consumed <= 0:
                    break
                remaining -= consumed
                active -= constrained

    _stretch_tracks = _distribute_track_space
    _distribute_space = _distribute_track_space
    
    def _fit_col_dimensions(self, dimensions: dict[int, int], target_size: int) -> None:
        stretch = self._get_fit_mode(True) == self.STRETCH_MODE or self._get_overflow_mode(True) == self.STRETCH_MODE
        active = {i for i in dimensions if self._get_col_fit_mode(i) == self.STRETCH_MODE or self._get_col_overflow_mode(i) == self.STRETCH_MODE}
        self._fit_dimensions(dimensions, target_size, round(self._cell_spacing.x), self._col_widths_constraints,
                             self._col_width_constraint, stretch, active)
    
    def _fit_row_dimensions(self, dimensions: dict[int, int], target_size: int) -> None:
        stretch = self._get_fit_mode(False) == self.STRETCH_MODE or self._get_overflow_mode(False) == self.STRETCH_MODE
        active = {i for i in dimensions if self._get_row_fit_mode(i) == self.STRETCH_MODE or self._get_row_overflow_mode(i) == self.STRETCH_MODE}
        self._fit_dimensions(dimensions, target_size, round(self._cell_spacing.y), self._row_heights_constraints,
                             self._row_height_constraint, stretch, active)
    
    def _fit_local_col_dimensions(self, row: int, dimensions: dict[int, int], target_size: int) -> None:
        active = {i for i in dimensions if self._get_col_fit_mode(i) == self.STRETCH_MODE or self._get_col_overflow_mode(i) == self.STRETCH_MODE}
        self._fit_dimensions(dimensions, target_size, round(self._cell_spacing.x), self._col_widths_constraints,
                             self._col_width_constraint, bool(active), active)
    
    def _fit_local_row_dimensions(self, col: int, dimensions: dict[int, int], target_size: int) -> None:
        active = {i for i in dimensions if self._get_row_fit_mode(i) == self.STRETCH_MODE or self._get_row_overflow_mode(i) == self.STRETCH_MODE}
        self._fit_dimensions(dimensions, target_size, round(self._cell_spacing.y), self._row_heights_constraints,
                             self._row_height_constraint, bool(active), active)
    
    def _ensure_span_requirement(self, dimensions: dict[int, int], indices: list[int], required_size: int, spacing: int,
                                 constraints: dict[int, SizeConstraint], default_constraint: SizeConstraint) -> None:
        current = sum(dimensions.get(i, 0) for i in indices) + spacing * max(0, len(indices) - 1)
        if current >= required_size:
            return
        tmp = {i: dimensions.get(i, 0) for i in indices}
        self._fit_dimensions(tmp, required_size, spacing, constraints, default_constraint, True, set(indices))
        dimensions.update(tmp)
    
    # endregion
    
    # endregion
    
    # region DIMENSIONS / SPAN RESOLUTION
    
    def _collect_tracks(self) -> tuple[set[int], set[int]]:
        cols: set[int] = set()
        rows: set[int] = set()
        for obj, (x, y) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            cols.update(range(x, x + sx))
            rows.update(range(y, y + sy))
        return cols, rows
    
    def _calculate_col_and_row_dims(self) -> None:
        self._reset_track_size_caches()
        cols, rows = self._collect_layout_tracks()
        self._initialize_track_sizes(cols, rows)
        self._size_tracks_from_children()
        self._apply_track_constraints()
        self._resolve_spans_iteratively()

    def _reset_track_size_caches(self) -> None:
        """Clear cached track sizes for a fresh calculation."""
        self._calculated_col_widths.clear()
        self._calculated_row_heights.clear()
        self._row_mode_calculated_col_widths.clear()
        self._col_mode_calculated_row_heights.clear()

    def _collect_layout_tracks(self) -> tuple[set[int], set[int]]:
        """Collect all column/row tracks used by placed children."""
        return self._collect_tracks()

    _gather_tracks = _collect_layout_tracks

    def _initialize_track_sizes(self, cols: set[int], rows: set[int]) -> None:
        """Initialize track size maps for collected tracks."""
        for col in cols:
            self._calculated_col_widths[col] = 0
        for row in rows:
            self._calculated_row_heights[row] = 0

    _init_track_sizes = _initialize_track_sizes

    def _size_tracks_from_children(self) -> None:
        """Compute initial track sizes based on children and layout mode."""
        for obj, (col, row) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            cell_w, cell_h = self._calculate_child_cell_size(obj, (col, row))

            if self._mode == self.GRID_MODE:
                self._size_tracks_for_grid_mode((col, row), sx, sy, cell_w, cell_h)
            elif self._mode == self.ROW_MODE:
                self._size_tracks_for_row_mode((col, row), sx, sy, cell_w, cell_h)
            elif self._mode == self.COL_MODE:
                self._size_tracks_for_column_mode((col, row), sx, sy, cell_w, cell_h)

    def _calculate_child_cell_size(self, obj: PygameObject, cell: CellPos) -> tuple[int, int]:
        """Calculate the size a child requires in its cell."""
        return self._calculate_cell_dims(obj, cell)

    _get_child_required_size = _calculate_child_cell_size

    def _size_tracks_for_grid_mode(self, cell: CellPos, sx: int, sy: int, cell_w: int, cell_h: int) -> None:
        col, row = cell
        if sx == 1:
            self._calculated_col_widths[col] = max(self._calculated_col_widths.get(col, 0), cell_w)
        if sy == 1:
            self._calculated_row_heights[row] = max(self._calculated_row_heights.get(row, 0), cell_h)

    def _size_tracks_for_row_mode(self, cell: CellPos, sx: int, sy: int, cell_w: int, cell_h: int) -> None:
        col, row = cell
        for r in self._indices_between(row, sy):
            row_widths = self._row_mode_calculated_col_widths.setdefault(r, {})
            if r == row:
                for c in self._indices_between(col, sx):
                    row_widths.setdefault(c, 0)
                if sx == 1:
                    row_widths[col] = max(row_widths.get(col, 0), cell_w)
        if sy == 1:
            self._calculated_row_heights[row] = max(self._calculated_row_heights.get(row, 0), cell_h)

    def _size_tracks_for_column_mode(self, cell: CellPos, sx: int, sy: int, cell_w: int, cell_h: int) -> None:
        col, row = cell
        self._calculated_col_widths[col] = max(self._calculated_col_widths.get(col, 0), cell_w if sx == 1 else 0)
        for c in self._indices_between(col, sx):
            col_heights = self._col_mode_calculated_row_heights.setdefault(c, {})
            if c == col:
                for r in self._indices_between(row, sy):
                    col_heights.setdefault(r, 0)
                if sy == 1:
                    col_heights[row] = max(col_heights.get(row, 0), cell_h)

    def _apply_track_constraints(self) -> None:
        """Apply width/height constraints to all tracks."""
        for col in sorted(self._calculated_col_widths):
            self._calculated_col_widths[col] = self._apply_col_width_constraints(col, self._calculated_col_widths.get(col, 0))
        for row in sorted(self._calculated_row_heights):
            self._calculated_row_heights[row] = self._apply_row_height_constraints(row, self._calculated_row_heights.get(row, 0))

        for row, widths in self._row_mode_calculated_col_widths.items():
            for col in list(widths):
                widths[col] = self._apply_col_width_constraints(col, widths[col])

        for col, heights in self._col_mode_calculated_row_heights.items():
            for row in list(heights):
                heights[row] = self._apply_row_height_constraints(row, heights[row])

    _constrain_tracks = _apply_track_constraints

    def _resolve_spans_iteratively(self) -> None:
        """Iteratively resolve spanning requirements until stable."""
        if not self._supports_spans:
            return
        iterations = max(0, self._max_span_resolution_iterations)
        for _ in range(iterations):
            before = self._snapshot_dimensions()
            self._resolve_span_requirements_pass()
            after = self._snapshot_dimensions()
            if before == after:
                break

    _expand_tracks_for_spans = _resolve_spans_iteratively

    def _resolve_span_requirements_pass(self) -> None:
        """Single pass of span requirement resolution."""
        for obj, (col, row) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            if sx <= 1 and sy <= 1 and self._should_skip_single_cell_span():
                continue
            req_w, req_h = self._calculate_child_cell_size(obj, (col, row))
            cols = self._indices_between(col, sx)
            rows = self._indices_between(row, sy)

            if self._mode == self.GRID_MODE:
                self._resolve_span_requirements_grid(cols, rows, req_w, req_h)
            elif self._mode == self.ROW_MODE:
                self._resolve_span_requirements_row(cols, rows, req_w, req_h, row)
            elif self._mode == self.COL_MODE:
                self._resolve_span_requirements_column(cols, rows, req_w, req_h, col)

    @staticmethod
    def _should_skip_single_cell_span() -> bool:
        """Whether to skip single-cell span resolution (can be overridden)."""
        return False

    def _resolve_span_requirements_grid(self, cols: list[int], rows: list[int], req_w: int, req_h: int) -> None:
        self._ensure_span_requirement(self._calculated_col_widths, cols, req_w, round(self._cell_spacing.x),
                                      self._col_widths_constraints, self._col_width_constraint)
        self._ensure_span_requirement(self._calculated_row_heights, rows, req_h, round(self._cell_spacing.y),
                                      self._row_heights_constraints, self._row_height_constraint)

    def _resolve_span_requirements_row(self, cols: list[int], rows: list[int], req_w: int, req_h: int, anchor_row: int) -> None:
        anchor_widths = self._row_mode_calculated_col_widths.setdefault(anchor_row, {})
        for c in cols:
            anchor_widths.setdefault(c, 0)
        self._ensure_span_requirement(anchor_widths, cols, req_w, round(self._cell_spacing.x),
                                      self._col_widths_constraints, self._col_width_constraint)
        self._ensure_span_requirement(self._calculated_row_heights, rows, req_h, round(self._cell_spacing.y),
                                      self._row_heights_constraints, self._row_height_constraint)

    def _resolve_span_requirements_column(self, cols: list[int], rows: list[int], req_w: int, req_h: int, anchor_col: int) -> None:
        self._ensure_span_requirement(self._calculated_col_widths, cols, req_w, round(self._cell_spacing.x),
                                      self._col_widths_constraints, self._col_width_constraint)
        anchor_heights = self._col_mode_calculated_row_heights.setdefault(anchor_col, {})
        for r in rows:
            anchor_heights.setdefault(r, 0)
        self._ensure_span_requirement(anchor_heights, rows, req_h, round(self._cell_spacing.y),
                                      self._row_heights_constraints, self._row_height_constraint)
    
    def _snapshot_dimensions(self):
        return (
            tuple(sorted(self._calculated_col_widths.items())),
            tuple(sorted(self._calculated_row_heights.items())),
            tuple((r, tuple(sorted(v.items()))) for r, v in sorted(self._row_mode_calculated_col_widths.items())),
            tuple((c, tuple(sorted(v.items()))) for c, v in sorted(self._col_mode_calculated_row_heights.items())),
        )
    
    # endregion
    
    # region SIZE / FITTING
    
    def _calculate_dims(self):
        self._compute_layout_bounds()

    def _compute_layout_bounds(self):
        outer_pad_x = round(self._outer_padding.x)
        outer_pad_y = round(self._outer_padding.y)
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)

        if self._mode == self.GRID_MODE:
            self._compute_bounds_for_grid_mode(spacing_x, spacing_y)
        elif self._mode == self.ROW_MODE:
            self._compute_bounds_for_row_mode(spacing_x, spacing_y)
        else:
            self._compute_bounds_for_column_mode(spacing_x, spacing_y)

        self._calculated_width = self._apply_layout_width_constraint(self._calculated_row_widths + 2 * outer_pad_x)
        self._calculated_height = self._apply_layout_height_constraint(self._calculated_col_heights + 2 * outer_pad_y)

    def _apply_layout_width_constraint(self, width: int) -> int:
        return self._width_constraint.apply(width)

    def _apply_layout_height_constraint(self, height: int) -> int:
        return self._height_constraint.apply(height)

    def _compute_bounds_for_grid_mode(self, spacing_x: int, spacing_y: int) -> None:
        self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
        self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)

    def _compute_bounds_for_row_mode(self, spacing_x: int, spacing_y: int) -> None:
        self._row_mode_calculated_row_widths = {
            row: self._calculate_total_size(widths, spacing_x)
            for row, widths in self._row_mode_calculated_col_widths.items()
        }
        self._calculated_row_widths = max(self._row_mode_calculated_row_widths.values(), default=0)
        self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)

    def _compute_bounds_for_column_mode(self, spacing_x: int, spacing_y: int) -> None:
        self._col_mode_calculated_col_heights = {
            col: self._calculate_total_size(heights, spacing_y)
            for col, heights in self._col_mode_calculated_row_heights.items()
        }
        self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
        self._calculated_col_heights = max(self._col_mode_calculated_col_heights.values(), default=0)

    _compute_content_bounds = _compute_layout_bounds
    
    def _content_size(self) -> tuple[int, int]:
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        if self._mode == self.GRID_MODE:
            content_w = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            content_h = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        elif self._mode == self.ROW_MODE:
            content_w = max(self._row_mode_calculated_row_widths.values(), default=0)
            content_h = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        else:
            content_w = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            content_h = max(self._col_mode_calculated_col_heights.values(), default=0)
        
        return content_w, content_h
    
    def _fit_col_and_row_dims(self):
        self._fit_tracks_to_available_space()

    def _fit_tracks_to_available_space(self) -> None:
        outer_pad_x = round(self._outer_padding.x)
        outer_pad_y = round(self._outer_padding.y)
        available_width = max(0, self._calculated_width - 2 * outer_pad_x)
        available_height = max(0, self._calculated_height - 2 * outer_pad_y)

        if self._mode == self.GRID_MODE:
            self._fit_tracks_grid_mode(available_width, available_height)
        elif self._mode == self.ROW_MODE:
            self._fit_tracks_row_mode(available_width, available_height)
        elif self._mode == self.COL_MODE:
            self._fit_tracks_column_mode(available_width, available_height)

    def _fit_tracks_grid_mode(self, available_width: int, available_height: int) -> None:
        current_width = self._calculate_total_size(self._calculated_col_widths, round(self._cell_spacing.x))
        current_height = self._calculate_total_size(self._calculated_row_heights, round(self._cell_spacing.y))
        if ((current_width < available_width and self._get_fit_mode(True) == self.STRETCH_MODE) or
                (current_width > available_width and self._get_overflow_mode(True) == self.STRETCH_MODE)):
            self._fit_col_dimensions(self._calculated_col_widths, available_width)
        if ((current_height < available_height and self._get_fit_mode(False) == self.STRETCH_MODE) or
                (current_height > available_height and self._get_overflow_mode(False) == self.STRETCH_MODE)):
            self._fit_row_dimensions(self._calculated_row_heights, available_height)

    def _fit_tracks_row_mode(self, available_width: int, available_height: int) -> None:
        for row, widths in self._row_mode_calculated_col_widths.items():
            current = self._calculate_total_size(widths, round(self._cell_spacing.x))
            if ((current < available_width and self._get_fit_mode(True) == self.STRETCH_MODE) or
                    (current > available_width and self._get_overflow_mode(True) == self.STRETCH_MODE)):
                self._fit_local_col_dimensions(row, widths, available_width)
        current_height = self._calculate_total_size(self._calculated_row_heights, round(self._cell_spacing.y))
        if ((current_height < available_height and self._get_fit_mode(False) == self.STRETCH_MODE) or
                (current_height > available_height and self._get_overflow_mode(False) == self.STRETCH_MODE)):
            self._fit_row_dimensions(self._calculated_row_heights, available_height)

    def _fit_tracks_column_mode(self, available_width: int, available_height: int) -> None:
        current_width = self._calculate_total_size(self._calculated_col_widths, round(self._cell_spacing.x))
        if ((current_width < available_width and self._get_fit_mode(True) == self.STRETCH_MODE) or
                (current_width > available_width and self._get_overflow_mode(True) == self.STRETCH_MODE)):
            self._fit_col_dimensions(self._calculated_col_widths, available_width)
        for col, heights in self._col_mode_calculated_row_heights.items():
            current = self._calculate_total_size(heights, round(self._cell_spacing.y))
            if ((current < available_height and self._get_fit_mode(False) == self.STRETCH_MODE) or
                    (current > available_height and self._get_overflow_mode(False) == self.STRETCH_MODE)):
                self._fit_local_row_dimensions(col, heights, available_height)
    
    # endregion
    
    # region SPANNING CUTS
    
    def _build_col_mode_cuts(self) -> dict[int, list[tuple[int, int, int, int, PygameObject]]]:
        """
        Return, per column, the row barriers created by spanning objects.

        :return: Mapping of column index to (start_row, end_row, start_y, end_y, object) barriers.
        """
        cuts: dict[int, list[tuple[int, int, int, int, PygameObject]]] = {}
        offsets = {
            col: self._calculate_offsets(heights, round(self._cell_spacing.y))
            for col, heights in self._col_mode_calculated_row_heights.items()
        }
        for obj, (col, row) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            if sx <= 1:
                continue
            heights = self._col_mode_calculated_row_heights.get(col, {})
            off = offsets.get(col, {})
            start_y = off.get(row, 0)
            span_rows = self._indices_between(row, sy)
            span_h = self._calculate_total_size({r: heights.get(r, 0) for r in span_rows}, round(self._cell_spacing.y))
            end_y = start_y + span_h
            for c in self._indices_between(col, sx):
                cuts.setdefault(c, []).append((row, row + sy, start_y, end_y, obj))
        return cuts
    
    def _build_row_mode_cuts(self) -> dict[int, list[tuple[int, int, int, int, PygameObject]]]:
        """
        Return, per row, the column barriers created by spanning objects.

        :return: Mapping of row index to (start_col, end_col, start_x, end_x, object) barriers.
        """
        cuts: dict[int, list[tuple[int, int, int, int, PygameObject]]] = {}
        offsets = {
            row: self._calculate_offsets(widths, round(self._cell_spacing.x))
            for row, widths in self._row_mode_calculated_col_widths.items()
        }
        for obj, (col, row) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            if sy <= 1:
                continue
            widths = self._row_mode_calculated_col_widths.get(row, {})
            off = offsets.get(row, {})
            start_x = off.get(col, 0)
            span_cols = self._indices_between(col, sx)
            span_w = self._calculate_total_size({c: widths.get(c, 0) for c in span_cols}, round(self._cell_spacing.x))
            end_x = start_x + span_w
            for r in self._indices_between(row, sy):
                cuts.setdefault(r, []).append((col, col + sx, start_x, end_x, obj))
        return cuts
    
    @staticmethod
    def _validate_cuts(cuts: dict[int, list[tuple[int, int, int, int, PygameObject]]]):
        for lane, lane_cuts in cuts.items():
            lane_cuts.sort(key=lambda cut: (cut[0], cut[1]))
            for i in range(1, len(lane_cuts)):
                prev = lane_cuts[i - 1]
                cur = lane_cuts[i]
                if cur[0] < prev[1]:
                    raise ValueError(
                        f"Overlapping spanning objects in lane {lane}: {prev[4]!r} and {cur[4]!r}"
                    )
    
    def _fit_col_mode_segments(self, cuts: dict[int, list[tuple[int, int, int, int, PygameObject]]]):
        spacing = round(self._cell_spacing.y)
        self._validate_cuts(cuts)
        
        for col, heights in self._col_mode_calculated_row_heights.items():
            lane_cuts = sorted(cuts.get(col, []), key=lambda cut: cut[2])
            if not lane_cuts:
                continue
            
            ordered_rows = sorted(heights)
            previous_row = ordered_rows[0] if ordered_rows else 0
            previous_end_y = 0
            
            for i, (start_row, end_row, start_y, end_y, _) in enumerate(lane_cuts):
                before = {r: heights[r] for r in ordered_rows if start_row > r >= previous_row}
                if before:
                    target = max(0, start_y - previous_end_y)
                    self._fit_local_row_dimensions(col, before, target)
                    heights.update(before)
                    self._apply_segment_justification(before, target, previous_end_y, self._col_mode_calculated_row_offsets.setdefault(col, {}), spacing, vertical=True)
                
                previous_row = end_row
                previous_end_y = end_y
            
            after = {r: heights[r] for r in ordered_rows if r >= previous_row}
            if after:
                lane_extent = self._calculate_total_size(heights, spacing)
                target = max(0, lane_extent - previous_end_y)
                self._fit_local_row_dimensions(col, after, target)
                heights.update(after)
    
    def _fit_row_mode_segments(self, cuts: dict[int, list[tuple[int, int, int, int, PygameObject]]]):
        spacing = round(self._cell_spacing.x)
        self._validate_cuts(cuts)
        
        for row, widths in self._row_mode_calculated_col_widths.items():
            lane_cuts = sorted(cuts.get(row, []), key=lambda cut: cut[2])
            if not lane_cuts:
                continue
            
            ordered_cols = sorted(widths)
            previous_col = ordered_cols[0] if ordered_cols else 0
            previous_end_x = 0
            
            for start_col, end_col, start_x, end_x, _ in lane_cuts:
                left = {c: widths[c] for c in ordered_cols if start_col > c >= previous_col}
                if left:
                    target = max(0, start_x - previous_end_x)
                    self._fit_local_col_dimensions(row, left, target)
                    widths.update(left)
                    self._apply_segment_justification(left, target, previous_end_x, self._row_mode_calculated_col_offsets.setdefault(row, {}), spacing, vertical=False)
                
                previous_col = end_col
                previous_end_x = end_x
            
            right = {c: widths[c] for c in ordered_cols if c >= previous_col}
            if right:
                lane_extent = self._calculate_total_size(widths, spacing)
                target = max(0, lane_extent - previous_end_x)
                self._fit_local_col_dimensions(row, right, target)
                widths.update(right)
    
    def _apply_segment_justification(
            self,
            dimensions: dict[int, int],
            target_size: int,
            segment_start: int,
            offsets: dict[int, int],
            spacing: int,
            vertical: bool,
    ) -> None:
        if not dimensions:
            return
        
        used = self._calculate_total_size(dimensions, spacing)
        justify = self._justification.y if vertical else self._justification.x
        shift = round((target_size - used) * justify)
        cursor = segment_start + shift
        for index in sorted(dimensions):
            offsets[index] = cursor
            cursor += dimensions[index] + spacing
    
    def _calculate_cut_offsets(
            self,
            dimensions: dict[int, int],
            cuts: list[tuple[int, int, int, int, PygameObject]],
            spacing: int,
            horizontal: bool,
    ) -> dict[int, int]:
        if not cuts:
            return self._calculate_offsets(dimensions, spacing)
        
        result: dict[int, int] = {}
        ordered = sorted(dimensions)
        sorted_cuts = sorted(cuts, key=lambda cut: cut[2])
        previous_index = ordered[0] if ordered else 0
        previous_end = 0
        
        for start_index, end_index, start_pos, end_pos, _ in sorted_cuts:
            group = {i: dimensions[i] for i in ordered if previous_index <= i < start_index}
            if group:
                target = max(0, start_pos - previous_end)
                used = self._calculate_total_size(group, spacing)
                justify = self._justification.x if horizontal else self._justification.y
                cursor = previous_end + round((target - used) * justify)
                for i in sorted(group):
                    result[i] = cursor
                    cursor += dimensions[i] + spacing
            
            previous_index = end_index
            previous_end = end_pos
        
        group = {i: dimensions[i] for i in ordered if i >= previous_index}
        if group:
            lane_extent = self._calculate_total_size(dimensions, spacing)
            target = max(0, lane_extent - previous_end)
            used = self._calculate_total_size(group, spacing)
            justify = self._justification.x if horizontal else self._justification.y
            cursor = previous_end + round((target - used) * justify)
            for i in sorted(group):
                result[i] = cursor
                cursor += dimensions[i] + spacing
        
        return result

    def _compute_track_offsets(self):
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)

        self._clear_offset_caches()

        if self._mode == self.GRID_MODE:
            self._compute_offsets_for_grid_mode(spacing_x, spacing_y)
            return

        if self._mode == self.ROW_MODE:
            self._compute_offsets_for_row_mode(spacing_x, spacing_y)
            return

        self._compute_offsets_for_column_mode(spacing_x, spacing_y)

    def _clear_offset_caches(self) -> None:
        self._calculated_col_offsets.clear()
        self._calculated_row_offsets.clear()
        self._row_mode_calculated_col_offsets.clear()
        self._col_mode_calculated_row_offsets.clear()

    def _compute_offsets_for_grid_mode(self, spacing_x: int, spacing_y: int) -> None:
        self._calculated_col_offsets = self._calculate_offsets(self._calculated_col_widths, spacing_x)
        self._calculated_row_offsets = self._calculate_offsets(self._calculated_row_heights, spacing_y)
        self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
        self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)

    def _compute_offsets_for_row_mode(self, spacing_x: int, spacing_y: int) -> None:
        cuts = self._build_row_mode_cuts() if self._supports_spanning_cuts else {}
        self._fit_row_mode_segments(cuts)
        self._row_mode_calculated_row_widths = {
            row: self._calculate_total_size(widths, spacing_x)
            for row, widths in self._row_mode_calculated_col_widths.items()
        }
        self._row_mode_calculated_col_offsets = {
            row: self._calculate_offsets(widths, spacing_x)
            for row, widths in self._row_mode_calculated_col_widths.items()
        }
        self._calculated_row_offsets = self._calculate_offsets(self._calculated_row_heights, spacing_y)
        self._calculated_row_widths = max(self._row_mode_calculated_row_widths.values(), default=0)
        self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        if self._supports_spanning_cuts:
            self._apply_row_mode_spanning_cuts(cuts, spacing_x)

    def _apply_row_mode_spanning_cuts(self, cuts: dict, spacing_x: int) -> None:
        for row, row_cuts in cuts.items():
            widths = self._row_mode_calculated_col_widths.get(row, {})
            self._row_mode_calculated_col_offsets[row] = self._calculate_cut_offsets(
                widths, row_cuts, spacing_x, horizontal=True
            )
        for row, row_cuts in cuts.items():
            row_offsets = self._row_mode_calculated_col_offsets.setdefault(row, {})
            for start_col, end_col, start_x, end_x, obj in row_cuts:
                anchor_row = self._object_placements[obj][1]
                if row == anchor_row:
                    row_offsets[start_col] = start_x
                else:
                    anchor_offsets = self._row_mode_calculated_col_offsets.get(anchor_row, {})
                    row_offsets[start_col] = anchor_offsets.get(start_col, start_x)

    def _compute_offsets_for_column_mode(self, spacing_x: int, spacing_y: int) -> None:
        cuts = self._build_col_mode_cuts() if self._supports_spanning_cuts else {}
        self._fit_col_mode_segments(cuts)
        self._calculated_col_offsets = self._calculate_offsets(self._calculated_col_widths, spacing_x)
        self._col_mode_calculated_row_offsets = {
            col: self._calculate_offsets(heights, spacing_y)
            for col, heights in self._col_mode_calculated_row_heights.items()
        }
        self._col_mode_calculated_col_heights = {
            col: self._calculate_total_size(heights, spacing_y)
            for col, heights in self._col_mode_calculated_row_heights.items()
        }
        self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
        self._calculated_col_heights = max(self._col_mode_calculated_col_heights.values(), default=0)

        if self._supports_spanning_cuts:
            self._apply_col_mode_spanning_cuts(cuts, spacing_y)

    def _apply_col_mode_spanning_cuts(self, cuts: dict, spacing_y: int) -> None:
        for col, col_cuts in cuts.items():
            heights = self._col_mode_calculated_row_heights.get(col, {})
            self._col_mode_calculated_row_offsets[col] = self._calculate_cut_offsets(
                heights, col_cuts, spacing_y, horizontal=False
            )
        for col, col_cuts in cuts.items():
            col_offsets = self._col_mode_calculated_row_offsets.setdefault(col, {})
            for start_row, end_row, start_y, end_y, obj in col_cuts:
                anchor_col = self._object_placements[obj][0]
                if col == anchor_col:
                    col_offsets[start_row] = start_y
                else:
                    anchor_offsets = self._col_mode_calculated_row_offsets.get(anchor_col, {})
                    col_offsets[start_row] = anchor_offsets.get(start_row, start_y)
    
    # endregion
    
    # region CELLS / POSITIONING
    
    def _span_dimensions(self, obj: PygameObject, cell: CellPos) -> tuple[int, int]:
        col, row = cell
        sx, sy = self._get_span(obj)
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        if self._mode == self.GRID_MODE:
            widths = {c: self._calculated_col_widths.get(c, 0) for c in self._indices_between(col, sx)}
            heights = {r: self._calculated_row_heights.get(r, 0) for r in self._indices_between(row, sy)}
        elif self._mode == self.ROW_MODE:
            widths = {c: self._row_mode_calculated_col_widths.get(row, {}).get(c, 0) for c in self._indices_between(col, sx)}
            heights = {r: self._calculated_row_heights.get(r, 0) for r in self._indices_between(row, sy)}
        else:
            widths = {c: self._calculated_col_widths.get(c, 0) for c in self._indices_between(col, sx)}
            heights = {r: self._col_mode_calculated_row_heights.get(col, {}).get(r, 0) for r in self._indices_between(row, sy)}
        
        return (
            self._calculate_total_size(widths, spacing_x),
            self._calculate_total_size(heights, spacing_y),
        )
    
    def _get_object_cell_offset(self, obj: PygameObject, cell: CellPos) -> tuple[int, int]:
        col, row = cell
        if self._mode == self.GRID_MODE:
            return self._calculated_col_offsets.get(col, 0), self._calculated_row_offsets.get(row, 0)
        if self._mode == self.ROW_MODE:
            return self._row_mode_calculated_col_offsets.get(row, {}).get(col, 0), self._calculated_row_offsets.get(row, 0)
        return self._calculated_col_offsets.get(col, 0), self._col_mode_calculated_row_offsets.get(col, {}).get(row, 0)
    
    def _position_objects(self):
        self._apply_child_positions()

    def _apply_child_positions(self):
        outer_pad_x = round(self._outer_padding.x)
        outer_pad_y = round(self._outer_padding.y)
        justify_x, justify_y = self._justification
        layout_w, layout_h = self._calculated_width, self._calculated_height
        content_w, content_h = self._get_content_size()

        start_x = round(outer_pad_x + (layout_w - 2 * outer_pad_x - content_w) * justify_x)
        start_y = round(outer_pad_y + (layout_h - 2 * outer_pad_y - content_h) * justify_y)

        for obj, cell in self._object_placements.items():
            pos = self._compute_child_position(obj, cell, start_x, start_y)
            obj.x_pos = round(pos[0])
            obj.y_pos = round(pos[1])
            self._dirty_checking_values[obj] = (vec2(obj.pos), vec2(obj.dims), vec2(obj.anchor))

    def _compute_child_position(self, obj: PygameObject, cell: CellPos, start_x: int, start_y: int) -> tuple[float, float]:
        cell_anchor_x, cell_anchor_y = self._get_cell_anchor(cell)
        cell_offset_x, cell_offset_y = self._get_object_cell_offset(obj, cell)
        cell_w, cell_h = self._get_cell_size_for_object(obj, cell)
        pad = self._get_cell_padding(cell)

        obj_w, obj_h = round(obj.dims.x), round(obj.dims.y)
        obj_anchor_x, obj_anchor_y = obj.anchor
        cell_x = start_x + cell_offset_x
        cell_y = start_y + cell_offset_y

        anchor_x = cell_x + cell_w * cell_anchor_x
        anchor_y = cell_y + cell_h * cell_anchor_y
        anchor_x += pad.x * (1 - 2 * cell_anchor_x)
        anchor_y += pad.y * (1 - 2 * cell_anchor_y)

        obj_x = anchor_x + obj_w * (obj_anchor_x - cell_anchor_x) + self._content_offset.x
        obj_y = anchor_y + obj_h * (obj_anchor_y - cell_anchor_y) + self._content_offset.y
        return obj_x, obj_y

    def _get_cell_size_for_object(self, obj: PygameObject, cell: CellPos) -> tuple[int, int]:
        return self._span_dimensions(obj, cell)

    _get_object_cell_dimensions = _get_cell_size_for_object

    def _get_content_size(self) -> tuple[int, int]:
        return self._content_size()
    
    # endregion
    
    # region TRACK BOOKKEEPING
    
    def _clear_max_col_and_rows(self) -> None:
        self._max_col = 0
        self._max_row = 0
        self._max_cols.clear()
        self._max_rows.clear()
        self._next_cols.clear()
        self._next_rows.clear()
    
    def _update_max_col_and_rows(self, x: int, y: int, sx: int, sy: int) -> None:
        self._max_col = max(self._max_col, x + sx - 1)
        self._max_row = max(self._max_row, y + sy - 1)
        self._max_cols[y] = max(self._max_cols.get(y, -1), x + sx - 1)
        self._max_rows[x] = max(self._max_rows.get(x, -1), y + sy - 1)
        self._next_cols[y] = max(self._next_cols.get(y, 0), x + sx)
        self._next_rows[x] = max(self._next_rows.get(x, 0), y + sy)
    
    def _recompute_max_col_and_rows(self) -> None:
        """Rebuild every track maximum from scratch so stale maxima can shrink."""
        self._clear_max_col_and_rows()
        for placed, (x, y) in self._object_placements.items():
            sx, sy = self._get_span(placed)
            self._update_max_col_and_rows(x, y, sx, sy)
    
    # endregion
    
    # region OBJECT REGISTRATION (internal)
    
    def _find_occupant(self, cell: CellPos, span: tuple[int, int], ignore: Optional[PygameObject] = None) -> Optional[PygameObject]:
        """
        Return the first object covering a cell's span, skipping an optional object.

        :param cell: Anchor cell of the queried span.
        :param span: Column and row span to check.
        :param ignore: Optional object to skip during the search.
        :return: The occupying object, or None when the span is free.
        """
        return self._find_foreign_occupant(cell, span, () if ignore is None else (ignore, ))
    
    def _find_foreign_occupant(self, cell: CellPos, span: tuple[int, int], moving: tuple[PygameObject, ...]) -> Optional[PygameObject]:
        """
        Return the first object covering a cell's span that is not one of the moving objects.

        :param cell: Anchor cell of the queried span.
        :param span: Column and row span to check.
        :param moving: Objects that should be ignored because they are being moved.
        :return: The occupying object, or None when the span is free.
        """
        for candidate in self._span_cells(cell, self._validate_span(span)):
            other = self._cells_objects.get(candidate)
            if other is not None and other not in moving:
                return other
        return None
    
    def _attach_object(self, obj: PygameObject, cell: CellPos, span: tuple[int, int] = (1, 1), anchor: Optional[vec2] = None) -> None:
        """
        Register an object at a cell without firing the addition hook.

        :param obj: Object to register.
        :param cell: Anchor cell for the object.
        :param span: Column and row span covered by the object.
        :param anchor: Optional anchor stored for the cell.
        """
        span = self._validate_span(span)
        
        for candidate in self._span_cells(cell, span):
            self._cells_objects[candidate] = obj
        
        self._object_placements[obj] = cell
        self._object_spans[obj] = span
        if anchor is not None:
            self._cell_anchors[cell] = vec2(anchor)
        
        self.add_child(obj, Anchor.TL)
        self.mark_dirty()
    
    def _detach_object(self, obj: PygameObject) -> CellPos:
        """
        Unregister an object from every cell it occupies without firing the removal hook.

        :param obj: Object to unregister.
        :return: The anchor cell the object occupied.
        """
        cell = self._object_placements.pop(obj)
        span = self._object_spans.pop(obj, (1, 1))
        
        for candidate in self._span_cells(cell, span):
            if self._cells_objects.get(candidate) is obj:
                del self._cells_objects[candidate]
        
        self.remove_child(obj)
        self._dirty_checking_values.pop(obj, None)
        
        return cell
    
    def _forget_object(self, obj: PygameObject) -> CellPos:
        """
        Detach an object and drop its per-object blacklist entries.

        :param obj: Object to forget.
        :return: The anchor cell the object occupied.
        """
        cell = self._detach_object(obj)
        self._dirty_checking_blacklist.discard(obj)
        self._object_positioning_blacklist.discard(obj)
        return cell
    
    def _validate_relocation(self, moves: list[tuple[PygameObject, CellPos, tuple[int, int]]]) -> None:
        """
        Check a planned relocation and raise before changing any state if it overlaps.

        :param moves: Planned (object, new_anchor_cell, new_span) moves.
        :raises ValueError: A moved object would land on an occupied cell or another mover's cell.
        """
        occupied = dict(self._cells_objects)
        moving = {id(o) for o, _, _ in moves}
        
        for o, _, _ in moves:
            if self.has_object(o):
                for cell in self._object_cells(o):
                    occupied.pop(cell, None)
        
        claimed: dict[CellPos, PygameObject] = {}
        for o, cell, span in moves:
            for candidate in self._span_cells(cell, self._validate_span(span)):
                other = occupied.get(candidate)
                if other is not None and id(other) not in moving:
                    raise ValueError(f"Object {o!r} cannot move to {cell}: {other!r} already occupies {candidate}")
                if (clash := claimed.get(candidate)) is not None:
                    raise ValueError(f"Object {o!r} cannot move to {cell}: {clash!r} already claims {candidate}")
                claimed[candidate] = o
    
    def _apply_relocation(self, moves: list[tuple[PygameObject, CellPos, tuple[int, int]]]) -> None:
        """
        Apply a relocation plan that has already been validated.

        :param moves: Validated (object, new_anchor_cell, new_span) moves.
        """
        for o, _, _ in moves:
            if self.has_object(o):
                self._detach_object(o)
        for o, cell, span in moves:
            self._attach_object(o, cell, span)
        
        if moves:
            self._recompute_max_col_and_rows()
            self.mark_dirty()
    
    def _plan_lane_insert(self, horizontal: bool, lane: int, start: int, new: PygameObject,
                          new_span: tuple[int, int]) -> list[tuple[PygameObject, CellPos, tuple[int, int]]]:
        """
        Plan how every object moves when an insertion pushes a lane back.

        :param horizontal: Whether the insertion pushes along a row.
        :param lane: Row or column index that receives the insertion.
        :param start: Column or row index where the new object is inserted.
        :param new: Object being inserted.
        :param new_span: Column and row span of the new object.
        :return: The validated move plan including the new object.
        :raises ValueError: The planned moves would overlap existing objects.
        """
        moves: list[tuple[PygameObject, CellPos, tuple[int, int]]] = [
            (new, (start, lane) if horizontal else (lane, start), new_span)
        ]
        
        for o, (px, py) in self._object_placements.items():
            if o is new:
                continue
            sx, sy = self._get_span(o)
            in_lane = lane in range(py, py + sy) if horizontal else lane in range(px, px + sx)
            ahead = px >= start if horizontal else py >= start
            if in_lane and ahead:
                moves.append((o, (px + 1, py) if horizontal else (px, py + 1), (sx, sy)))
        
        self._validate_relocation(moves)
        return moves
    
    def _clear_objects(self, ignore_callbacks: bool = True) -> None:
        """
        Remove every placed object, firing removal hooks unless ignored.

        :param ignore_callbacks: Whether to suppress removal hooks for every object.
        """
        removed = list(self._object_placements)
        for obj in removed:
            self._forget_object(obj)
        self._recompute_max_col_and_rows()
        self.mark_dirty()
        
        if not ignore_callbacks:
            for obj in removed:
                self.on_object_removal(obj)
    
    # endregion
    
    # region OBJECT QUERIES
    
    def __len__(self) -> int:
        """
        Return the number of placed objects.

        :return: The number of placed objects.
        """
        return len(self._object_placements)
    
    def __iter__(self) -> Iterator[PygameObject]:
        """
        Iterate over the placed objects in insertion order.

        :return: An iterator over the placed objects.
        """
        return iter(self._object_placements)
    
    def has_object(self, obj: PygameObject) -> bool:
        """
        Return whether an object is placed in this layout.

        :param obj: Object to look up.
        :return: True when the object is placed in the layout.
        """
        return obj in self._object_placements
    
    def get_object_column(self, obj: PygameObject) -> int:
        """
        Return the anchor column of an object.

        :param obj: Placed object to query.
        :return: The object's anchor column index.
        """
        return self._object_placements[obj][0]
    
    def get_object_row(self, obj: PygameObject) -> int:
        """
        Return the anchor row of an object.

        :param obj: Placed object to query.
        :return: The object's anchor row index.
        """
        return self._object_placements[obj][1]
    
    def get_object_placement(self, obj: PygameObject) -> CellPos:
        """
        Return the anchor cell of an object.

        :param obj: Placed object to query.
        :return: The (column, row) anchor cell.
        """
        return self._object_placements[obj]
    
    def get_object_span(self, obj: PygameObject) -> tuple[int, int]:
        """
        Return the column and row span of an object.

        :param obj: Placed object to query.
        :return: The (column, row) span.
        """
        return self._get_span(obj)
    
    def get_object_in_cell(self, x: int, y: int) -> PygameObject:
        """
        Return the object occupying a cell.

        :param x: Column index.
        :param y: Row index.
        :return: The object occupying the cell.
        """
        return self._cells_objects[(x, y)]
    
    def find_object_in_cell(self, x: int, y: int) -> Optional[PygameObject]:
        """
        Return the object occupying a cell, or None when it is empty.

        :param x: Column index.
        :param y: Row index.
        :return: The occupying object or None.
        """
        return self._cells_objects.get((x, y))
    
    # endregion
    
    # region TRACK QUERIES
    
    def get_col_width(self, col: int, row: Optional[int] = None) -> int:
        """
        Return the calculated width of a column, optionally for one row.

        :param col: Column index.
        :param row: Row index used in row mode.
        :return: The calculated column width.
        """
        if self.mode == self.GRID_MODE or self.mode == self.COL_MODE:
            return self._calculated_col_widths.get(col, 0)
        if self.mode == self.ROW_MODE and row is not None:
            return self._row_mode_calculated_col_widths.get(row, {}).get(col, 0)
        return 0
    
    def get_col_height(self, col: int) -> int:
        """
        Return the calculated height of a column.

        :param col: Column index.
        :return: The calculated column height.
        """
        if self.mode == self.GRID_MODE or self.mode == self.ROW_MODE:
            return self._calculated_col_heights
        if self.mode == self.COL_MODE:
            return self._col_mode_calculated_col_heights.get(col, 0)
        return 0
    
    def get_row_width(self, row: int) -> int:
        """
        Return the calculated width of a row.

        :param row: Row index.
        :return: The calculated row width.
        """
        if self.mode == self.GRID_MODE or self.mode == self.COL_MODE:
            return self._calculated_row_widths
        if self.mode == self.ROW_MODE:
            return self._row_mode_calculated_row_widths.get(row, 0)
        return 0
    
    def get_row_height(self, row: int, col: Optional[int] = None) -> int:
        """
        Return the calculated height of a row, optionally for one column.

        :param row: Row index.
        :param col: Column index used in column mode.
        :return: The calculated row height.
        """
        if self.mode == self.GRID_MODE or self.mode == self.ROW_MODE:
            return self._calculated_row_heights.get(row, 0)
        if self.mode == self.COL_MODE and col is not None:
            return self._col_mode_calculated_row_heights.get(col, {}).get(row, 0)
        return 0
    
    def get_max_col_in_row(self, row: int) -> int:
        """
        Return the highest occupied column index in a row.

        :param row: Row index.
        :return: The highest occupied column index.
        """
        return self._max_cols.get(row, 0)
    
    def get_max_row_in_col(self, col: int) -> int:
        """
        Return the highest occupied row index in a column.

        :param col: Column index.
        :return: The highest occupied row index.
        """
        return self._max_rows.get(col, 0)
    
    def get_next_col(self, row: int) -> int:
        """
        Return the next free column index in a row.

        :param row: Row index.
        :return: The next free column index.
        """
        return self._next_cols.get(row, 0)
    
    def get_next_row(self, col: int) -> int:
        """
        Return the next free row index in a column.

        :param col: Column index.
        :return: The next free row index.
        """
        return self._next_rows.get(col, 0)
    
    def get_content_size(self) -> tuple[int, int]:
        """
        Return the laid out content size, excluding outer padding.

        :return: The (width, height) content size.
        """
        return self._content_size()

    def get_layout_content_size(self) -> tuple[int, int]:
        """Return the laid out content size, excluding outer padding."""
        return self._content_size()
    
    # endregion
    
    # region LAYOUT SETTERS
    
    def set_mode(self, mode: Literal["grid", "rows", "columns"]) -> "LayoutObject":
        """
        Set the layout mode.

        :param mode: Layout mode to use.
        :return: This layout, allowing chained calls.
        """
        self.mode = mode
        return self
    
    def set_justify(self, value: vec2) -> "LayoutObject":
        """
        Set the content justification.

        :param value: Justification vector.
        :return: This layout, allowing chained calls.
        """
        self.justification = value
        return self
    
    def set_fit_mode(self, mode: FitMode) -> "LayoutObject":
        """
        Set the fit mode used when content is smaller than the layout.

        :param mode: Fit mode to use.
        :return: This layout, allowing chained calls.
        """
        self.fit_mode = mode
        return self
    
    def set_overflow_mode(self, mode: FitMode) -> "LayoutObject":
        """
        Set the mode used when content is larger than the layout.

        :param mode: Overflow mode to use.
        :return: This layout, allowing chained calls.
        """
        self.overflow_mode = mode
        return self
    
    def set_horizontal_fit_mode(self, mode: FitMode, col: Optional[int] = None) -> "LayoutObject":
        """
        Set the horizontal fit mode globally or for one column.

        :param mode: Fit mode to use.
        :param col: Optional column index; None applies the mode globally.
        :return: This layout, allowing chained calls.
        """
        if col is None:
            self.horizontal_fit_mode = mode
        else:
            self._col_horizontal_fit_modes[col] = mode
            self.mark_dirty()
        return self
    
    def set_vertical_fit_mode(self, mode: FitMode, row: Optional[int] = None) -> "LayoutObject":
        """
        Set the vertical fit mode globally or for one row.

        :param mode: Fit mode to use.
        :param row: Optional row index; None applies the mode globally.
        :return: This layout, allowing chained calls.
        """
        if row is None:
            self.vertical_fit_mode = mode
        else:
            self._row_vertical_fit_modes[row] = mode
            self.mark_dirty()
        return self
    
    def set_horizontal_overflow_mode(self, mode: FitMode, col: Optional[int] = None) -> "LayoutObject":
        """
        Set the horizontal overflow mode globally or for one column.

        :param mode: Overflow mode to use.
        :param col: Optional column index; None applies the mode globally.
        :return: This layout, allowing chained calls.
        """
        if col is None:
            self.horizontal_overflow_mode = mode
        else:
            self._col_horizontal_overflow_modes[col] = mode
            self.mark_dirty()
        return self
    
    def set_vertical_overflow_mode(self, mode: FitMode, row: Optional[int] = None) -> "LayoutObject":
        """
        Set the vertical overflow mode globally or for one row.

        :param mode: Overflow mode to use.
        :param row: Optional row index; None applies the mode globally.
        :return: This layout, allowing chained calls.
        """
        if row is None:
            self.vertical_overflow_mode = mode
        else:
            self._row_vertical_overflow_modes[row] = mode
            self.mark_dirty()
        return self
    
    def set_padding(self, value: int | vec2, cell: Optional[CellPos] = None) -> "LayoutObject":
        """
        Set outer padding globally or cell padding when a cell is given.

        :param value: Padding value.
        :param cell: Optional cell whose padding is set.
        :return: This layout, allowing chained calls.
        """
        if cell is None:
            self.outer_padding = value
        else:
            self.set_cell_padding(value, cell)
        return self
    
    def set_cell_padding(self, value: int | vec2, cell: Optional[CellPos] = None) -> "LayoutObject":
        """
        Set cell padding globally or for one cell.

        :param value: Padding value.
        :param cell: Optional cell whose padding is set.
        :return: This layout, allowing chained calls.
        """
        if cell is None:
            self.cell_padding = value
        else:
            self._cell_paddings[cell] = vec2(value)
            self.mark_dirty()
        return self
    
    def set_cell_spacing(self, value: int | vec2, outer: bool = False) -> "LayoutObject":
        """
        Set cell spacing, optionally applying the same value as outer padding.

        :param value: Spacing value.
        :param outer: Whether to also use the value as outer padding.
        :return: This layout, allowing chained calls.
        """
        self.cell_spacing = value
        return self.set_padding(value) if outer else self
    
    def set_cell_anchor(self, value: vec2, cell: Optional[CellPos] = None) -> "LayoutObject":
        """
        Set the content anchor globally or for one cell.

        :param value: Anchor vector.
        :param cell: Optional cell whose anchor is set.
        :return: This layout, allowing chained calls.
        """
        if cell is None:
            self._cell_anchor = vec2(value)
        else:
            self._cell_anchors[cell] = vec2(value)
        self.mark_dirty()
        return self
    
    def set_content_offset(self, value: vec2) -> "LayoutObject":
        """
        Set the content offset.

        :param value: Content offset vector.
        :return: This layout, allowing chained calls.
        """
        self.content_offset = value
        return self
    
    def set_content_offset_x(self, value: float) -> "LayoutObject":
        """
        Set the horizontal content offset.

        :param value: Horizontal offset.
        :return: This layout, allowing chained calls.
        """
        self.content_offset_x = value
        return self
    
    def set_content_offset_y(self, value: float) -> "LayoutObject":
        """
        Set the vertical content offset.

        :param value: Vertical offset.
        :return: This layout, allowing chained calls.
        """
        self.content_offset_y = value
        return self
    
    def set_layering_priority(self, priority: LayeringPriority) -> "LayoutObject":
        """
        Set the z-ordering rule applied on every relayout.

        :param priority: Layering priority rule, or None to disable automatic layering.
        :return: This layout, allowing chained calls.
        """
        self._layering_priority = priority
        self.mark_dirty()
        return self
    
    # endregion
    
    # region SIZE CONSTRAINT SETTERS
    
    def set_width_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                             fixed_value: Optional[int] = None) -> "LayoutObject":
        """
        Set the minimum, maximum, and fixed width bounds.

        :param min_value: Minimum width.
        :param max_value: Maximum width.
        :param fixed_value: Fixed width that overrides the other bounds.
        :return: This layout, allowing chained calls.
        """
        self._width_constraint.min = min_value
        self._width_constraint.max = max_value
        self._width_constraint.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_width(self, value: int) -> "LayoutObject":
        """
        Set the fixed width.

        :param value: Fixed width.
        :return: This layout, allowing chained calls.
        """
        self._width_constraint.fixed = value
        self.mark_dirty()
        return self
    
    def set_min_width(self, value: int) -> "LayoutObject":
        """
        Set the minimum width.

        :param value: Minimum width.
        :return: This layout, allowing chained calls.
        """
        self._width_constraint.min = value
        self.mark_dirty()
        return self
    
    def set_max_width(self, value: int) -> "LayoutObject":
        """
        Set the maximum width.

        :param value: Maximum width.
        :return: This layout, allowing chained calls.
        """
        self._width_constraint.max = value
        self.mark_dirty()
        return self
    
    def set_height_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                              fixed_value: Optional[int] = None) -> "LayoutObject":
        """
        Set the minimum, maximum, and fixed height bounds.

        :param min_value: Minimum height.
        :param max_value: Maximum height.
        :param fixed_value: Fixed height that overrides the other bounds.
        :return: This layout, allowing chained calls.
        """
        self._height_constraint.min = min_value
        self._height_constraint.max = max_value
        self._height_constraint.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_height(self, value: int) -> "LayoutObject":
        """
        Set the fixed height.

        :param value: Fixed height.
        :return: This layout, allowing chained calls.
        """
        self._height_constraint.fixed = value
        self.mark_dirty()
        return self
    
    def set_min_height(self, value: int) -> "LayoutObject":
        """
        Set the minimum height.

        :param value: Minimum height.
        :return: This layout, allowing chained calls.
        """
        self._height_constraint.min = value
        self.mark_dirty()
        return self
    
    def set_max_height(self, value: int) -> "LayoutObject":
        """
        Set the maximum height.

        :param value: Maximum height.
        :return: This layout, allowing chained calls.
        """
        self._height_constraint.max = value
        self.mark_dirty()
        return self
    
    def set_col_width_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                                 fixed_value: Optional[int] = None, col: Optional[int] = None) -> "LayoutObject":
        """
        Set column width bounds globally or for one column.

        :param min_value: Minimum column width.
        :param max_value: Maximum column width.
        :param fixed_value: Fixed column width that overrides the other bounds.
        :param col: Optional column index; None applies to all columns.
        :return: This layout, allowing chained calls.
        """
        c = self._get_col_constraint(col)
        c.min = min_value
        c.max = max_value
        c.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_col_width(self, value: int, col: Optional[int] = None) -> "LayoutObject":
        """
        Set a fixed column width globally or for one column.

        :param value: Fixed column width.
        :param col: Optional column index; None applies to all columns.
        :return: This layout, allowing chained calls.
        """
        self._get_col_constraint(col).fixed = value
        self.mark_dirty()
        return self
    
    def set_min_col_width(self, value: int, col: Optional[int] = None) -> "LayoutObject":
        """
        Set a minimum column width globally or for one column.

        :param value: Minimum column width.
        :param col: Optional column index; None applies to all columns.
        :return: This layout, allowing chained calls.
        """
        self._get_col_constraint(col).min = value
        self.mark_dirty()
        return self
    
    def set_max_col_width(self, value: int, col: Optional[int] = None) -> "LayoutObject":
        """
        Set a maximum column width globally or for one column.

        :param value: Maximum column width.
        :param col: Optional column index; None applies to all columns.
        :return: This layout, allowing chained calls.
        """
        self._get_col_constraint(col).max = value
        self.mark_dirty()
        return self
    
    def set_row_height_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                                  fixed_value: Optional[int] = None, row: Optional[int] = None) -> "LayoutObject":
        """
        Set row height bounds globally or for one row.

        :param min_value: Minimum row height.
        :param max_value: Maximum row height.
        :param fixed_value: Fixed row height that overrides the other bounds.
        :param row: Optional row index; None applies to all rows.
        :return: This layout, allowing chained calls.
        """
        c = self._get_row_constraint(row)
        c.min = min_value
        c.max = max_value
        c.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_row_height(self, value: int, row: Optional[int] = None) -> "LayoutObject":
        """
        Set a fixed row height globally or for one row.

        :param value: Fixed row height.
        :param row: Optional row index; None applies to all rows.
        :return: This layout, allowing chained calls.
        """
        self._get_row_constraint(row).fixed = value
        self.mark_dirty()
        return self
    
    def set_min_row_height(self, value: int, row: Optional[int] = None) -> "LayoutObject":
        """
        Set a minimum row height globally or for one row.

        :param value: Minimum row height.
        :param row: Optional row index; None applies to all rows.
        :return: This layout, allowing chained calls.
        """
        self._get_row_constraint(row).min = value
        self.mark_dirty()
        return self
    
    def set_max_row_height(self, value: int, row: Optional[int] = None) -> "LayoutObject":
        """
        Set a maximum row height globally or for one row.

        :param value: Maximum row height.
        :param row: Optional row index; None applies to all rows.
        :return: This layout, allowing chained calls.
        """
        self._get_row_constraint(row).max = value
        self.mark_dirty()
        return self
    
    # endregion
    
    # region OBJECT PLACEMENT
    
    def on_object_addition(self, obj: PygameObject) -> None:
        """
        Forward an object-addition event to the layout behaviors.

        :param obj: Object that was added to the layout.
        """
        self.behaviors.on_object_addition(obj)
    
    def on_object_removal(self, obj: PygameObject) -> None:
        """
        Forward an object-removal event to the layout behaviors.

        :param obj: Object that was removed from the layout.
        """
        self.behaviors.on_object_removal(obj)
    
    def set_object_in_cell(self, obj: PygameObject, x: int, y: int, anchor: Optional[vec2] = None,
                           span_x: int = 1, span_y: int = 1, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Place an object at a cell and fire the addition hook for new objects.

        :param obj: Object to place.
        :param x: Target column index.
        :param y: Target row index.
        :param anchor: Optional anchor used inside the target cell.
        :param span_x: Number of columns covered by the object.
        :param span_y: Number of rows covered by the object.
        :param ignore_callbacks: Whether to suppress the addition hook when the object is new.
        :return: This layout, allowing chained calls.
        :raises ValueError: span_x or span_y is less than one, or the object overlaps an existing object.
        """
        span = self._validate_span((span_x, span_y))
        cell = (x, y)
        
        occupant = self._find_occupant(cell, span, ignore=obj)
        if occupant is not None:
            raise ValueError(f"Object {obj!r} overlaps existing object {occupant!r}")
        
        is_new = not self.has_object(obj)
        if not is_new:
            self._detach_object(obj)
        
        self._attach_object(obj, cell, span, anchor)
        self._recompute_max_col_and_rows()
        
        if is_new and not ignore_callbacks:
            self.on_object_addition(obj)
        
        return self
    
    def remove_object(self, obj: PygameObject, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Remove an object from the layout and fire the removal hook unless ignored.

        :param obj: Object to remove.
        :param ignore_callbacks: Whether to suppress the removal hook.
        :return: This layout, allowing chained calls.
        :raises KeyError: The object is not part of this layout.
        """
        if not self.has_object(obj):
            raise KeyError(f"Object {obj!r} is not part of this layout")
        
        self._forget_object(obj)
        self._recompute_max_col_and_rows()
        self.mark_dirty()
        
        if not ignore_callbacks:
            self.on_object_removal(obj)
        
        return self
    
    def remove_object_in_cell(self, x: int, y: int, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Remove the object occupying a cell.

        :param x: Column index.
        :param y: Row index.
        :param ignore_callbacks: Whether to suppress the removal hook.
        :return: This layout, allowing chained calls.
        """
        obj = self._cells_objects[(x, y)]
        return self.remove_object(obj, ignore_callbacks=ignore_callbacks)
    
    def clear(self, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Remove every object from the layout, firing removal hooks unless ignored.

        :param ignore_callbacks: Whether to suppress removal hooks for every object.
        :return: This layout, allowing chained calls.
        """
        self._clear_objects(ignore_callbacks)
        return self
    
    def replace_object(self, prev: PygameObject, new: Optional[PygameObject], ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Hand a placed object's cell over to a new object.

        :param prev: Object currently in the layout.
        :param new: Replacement object, or None to clear the cell.
        :param ignore_callbacks: Whether to suppress the removal and addition hooks.
        :return: This layout, allowing chained calls.
        :raises KeyError: prev is not part of this layout.
        :raises ValueError: The replacement overlaps another object.
        """
        if not self.has_object(prev):
            raise KeyError(f"Object {prev!r} is not part of this layout")
        
        if new is None:
            self.remove_object(prev, ignore_callbacks=ignore_callbacks)
        else:
            self.replace_object_in_cell(*self._object_placements[prev], new, ignore_callbacks=ignore_callbacks)
        
        return self
    
    def replace_object_in_cell(self, x: int, y: int, new: Optional[PygameObject], anchor: Optional[vec2] = None,
                               span: Optional[tuple[int, int]] = None, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Swap the object occupying a cell for a new object.

        :param x: Column index.
        :param y: Row index.
        :param new: Replacement object, or None to clear the cell.
        :param anchor: Optional anchor used for the replacement.
        :param span: Optional span for the replacement.
        :param ignore_callbacks: Whether to suppress the removal and addition hooks.
        :return: This layout, allowing chained calls.
        :raises ValueError: The replacement span is invalid or overlaps another object.
        """
        pos: CellPos = (x, y)
        prev = self._cells_objects.get(pos, None)

        if new is None:
            if prev is not None:
                self.remove_object(prev, ignore_callbacks=ignore_callbacks)
            return self

        new: PygameObject
        if new is prev:
            if span is not None:
                self.set_span(new, *span)
            if anchor is not None:
                self.set_cell_anchor(anchor, pos)
            return self

        prev_cell, prev_span = (self._object_placements[prev], self._get_span(prev)) if prev is not None else (pos, (1, 1))
        new_is_new = new is not None and not self.has_object(new)
        new_cell, new_old_span = (self._object_placements[new], self._get_span(new)) if not new_is_new else (pos, (1, 1))

        if span is not None:
            new_span = self._validate_span(span)
        elif not new_is_new:
            new_span = new_old_span
        else:
            new_span = prev_span

        if prev is not None:
            self._forget_object(prev)
        
        if new is not None:
            if not new_is_new:
                self._detach_object(new)
            
            occupant = self._find_occupant(pos, new_span)
            if occupant is not None:
                if not new_is_new:
                    self._attach_object(new, new_cell, new_old_span)
                if prev is not None:
                    self._attach_object(prev, prev_cell, prev_span)
                self._recompute_max_col_and_rows()
                raise ValueError(f"Object {new!r} overlaps existing object {occupant!r}")
            
            self._attach_object(new, pos, new_span, anchor)
        
        self._recompute_max_col_and_rows()
        self.mark_dirty()

        if ignore_callbacks:
            return self
        
        if prev is not None:
            self.on_object_removal(prev)
        if new_is_new:
            self.on_object_addition(new)
        
        return self
    
    def switch_object_positions(self, obj1: PygameObject, obj2: PygameObject) -> "LayoutObject":
        """
        Swap the anchor cells of two placed objects.

        :param obj1: First object to swap.
        :param obj2: Second object to swap.
        :return: This layout, allowing chained calls.
        :raises KeyError: Either object is not part of this layout.
        :raises ValueError: The swap would make the objects overlap.
        """
        if obj1 is obj2:
            return self
        if not self.has_object(obj1) or not self.has_object(obj2):
            raise KeyError("Both objects must be part of this layout")
        
        moves = [
            (obj1, self._object_placements[obj2], self._get_span(obj1)),
            (obj2, self._object_placements[obj1], self._get_span(obj2)),
        ]
        self._validate_relocation(moves)
        self._apply_relocation(moves)
        
        return self
    
    def switch_cells_content(self, x1: int, y1: int, x2: int, y2: int) -> "LayoutObject":
        """
        Swap two cells or move content when one of them is empty.

        :param x1: Column index of the first cell.
        :param y1: Row index of the first cell.
        :param x2: Column index of the second cell.
        :param y2: Row index of the second cell.
        :return: This layout, allowing chained calls.
        :raises ValueError: The move would make objects overlap.
        """
        cell1: CellPos = (x1, y1)
        cell2: CellPos = (x2, y2)
        if cell1 == cell2:
            return self
        
        obj1 = self._cells_objects.get(cell1, None)
        obj2 = self._cells_objects.get(cell2, None)
        
        if obj1 is not None and obj2 is not None:
            return self.switch_object_positions(obj1, obj2)
        
        moved, target = (obj1, cell2) if obj1 is not None else (obj2, cell1)
        if moved is None:
            return self
        
        moves = [(moved, target, self._get_span(moved))]
        self._validate_relocation(moves)
        self._apply_relocation(moves)
        
        return self
    
    def insert_object_in_col(self, obj: PygameObject, col: int, row: int, span_x: int = 1, span_y: int = 1, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Place an object and push later objects in the column one row down.

        :param obj: Object to insert.
        :param col: Target column index.
        :param row: Target row index.
        :param span_x: Number of columns covered by the object.
        :param span_y: Number of rows covered by the object.
        :param ignore_callbacks: Whether to suppress the addition hook.
        :return: This layout, allowing chained calls.
        :raises ValueError: The span is invalid or the insertion would make objects overlap.
        """
        moves = self._plan_lane_insert(False, col, row, obj, self._validate_span((span_x, span_y)))
        self._apply_relocation([m for m in moves if m[0] is not obj])
        return self.set_object_in_cell(obj, col, row, span_x=span_x, span_y=span_y, ignore_callbacks=ignore_callbacks)
    
    def insert_object_in_row(self, obj: PygameObject, col: int, row: int, span_x: int = 1, span_y: int = 1, ignore_callbacks: bool = False) -> "LayoutObject":
        """
        Place an object and push later objects in the row one column right.

        :param obj: Object to insert.
        :param col: Target column index.
        :param row: Target row index.
        :param span_x: Number of columns covered by the object.
        :param span_y: Number of rows covered by the object.
        :param ignore_callbacks: Whether to suppress the addition hook.
        :return: This layout, allowing chained calls.
        :raises ValueError: The span is invalid or the insertion would make objects overlap.
        """
        moves = self._plan_lane_insert(True, row, col, obj, self._validate_span((span_x, span_y)))
        self._apply_relocation([m for m in moves if m[0] is not obj])
        return self.set_object_in_cell(obj, col, row, span_x=span_x, span_y=span_y, ignore_callbacks=ignore_callbacks)
    
    def set_span(self, obj: PygameObject, span_x: int = 1, span_y: int = 1) -> "LayoutObject":
        """
        Resize the span of a placed object while keeping its anchor cell.

        :param obj: Placed object to resize.
        :param span_x: Number of columns covered by the object.
        :param span_y: Number of rows covered by the object.
        :return: This layout, allowing chained calls.
        :raises KeyError: The object is not part of this layout.
        :raises ValueError: The span is invalid or overlaps another object.
        """
        if not self.has_object(obj):
            raise KeyError("Object is not part of this layout")
        
        span = self._validate_span((span_x, span_y))
        cell = self._object_placements[obj]
        
        occupant = self._find_occupant(cell, span, ignore=obj)
        if occupant is not None:
            raise ValueError(f"Object {obj!r} span overlaps existing object {occupant!r}")
        
        self._detach_object(obj)
        self._attach_object(obj, cell, span)
        self._recompute_max_col_and_rows()
        
        return self
    
    def stack_x(self, obj: PygameObject, y: int = 0, anchor: Optional[vec2] = None,
                span_x: int = 1, span_y: int = 1) -> "LayoutObject":
        """
        Place an object at the next free column in a row.

        :param obj: Object to place.
        :param y: Row index to stack within.
        :param anchor: Optional anchor used inside the target cell.
        :param span_x: Number of columns covered by the object.
        :param span_y: Number of rows covered by the object.
        :return: This layout, allowing chained calls.
        """
        return self.set_object_in_cell(obj, self._next_cols.get(y, 0), y, anchor, span_x, span_y)
    
    def stack_y(self, obj: PygameObject, x: int = 0, anchor: Optional[vec2] = None,
                span_x: int = 1, span_y: int = 1) -> "LayoutObject":
        """
        Place an object at the next free row in a column.

        :param obj: Object to place.
        :param x: Column index to stack within.
        :param anchor: Optional anchor used inside the target cell.
        :param span_x: Number of columns covered by the object.
        :param span_y: Number of rows covered by the object.
        :return: This layout, allowing chained calls.
        """
        return self.set_object_in_cell(obj, x, self._next_rows.get(x, 0), anchor, span_x, span_y)
    
    # endregion
    
    # region DIRTY CHECKING
    
    def enable_dirty_checking(self) -> "LayoutObject":
        """
        Enable automatic dirty detection from child movement or resizing.

        :return: This layout, allowing chained calls.
        """
        self._dirty_checking = True
        return self

    def disable_dirty_checking(self) -> "LayoutObject":
        """
        Disable automatic dirty detection.

        :return: This layout, allowing chained calls.
        """
        self._dirty_checking = False
        return self
    
    def toggle_dirty_checking(self) -> "LayoutObject":
        """
        Toggle automatic dirty detection.

        :return: This layout, allowing chained calls.
        """
        self._dirty_checking = not self._dirty_checking
        return self
    
    def add_to_dirty_checking_blacklist(self, obj: PygameObject) -> "LayoutObject":
        """
        Exclude an object from automatic dirty detection.

        :param obj: Object to exclude.
        :return: This layout, allowing chained calls.
        """
        self._dirty_checking_blacklist.add(obj)
        return self
    
    def remove_from_dirty_checking_blacklist(self, obj: PygameObject) -> "LayoutObject":
        """
        Re-include an object in automatic dirty detection.

        :param obj: Object to re-include.
        :return: This layout, allowing chained calls.
        """
        self._dirty_checking_blacklist.discard(obj)
        return self
    
    def clear_dirty_checking_blacklist(self) -> "LayoutObject":
        """
        Clear the dirty-checking exclusion list.

        :return: This layout, allowing chained calls.
        """
        self._dirty_checking_blacklist.clear()
        return self

    def add_to_object_positioning_blacklist(self, obj: PygameObject) -> "LayoutObject":
        """
        Stop automatic dirty detection from reacting to an object's position changes.

        :param obj: Object whose position changes should be ignored.
        :return: This layout, allowing chained calls.
        """
        self._object_positioning_blacklist.add(obj)
        return self

    def remove_from_object_positioning_blacklist(self, obj: PygameObject) -> "LayoutObject":
        """
        Re-enable automatic dirty detection for an object's position changes.

        :param obj: Object to re-enable.
        :return: This layout, allowing chained calls.
        """
        self._object_positioning_blacklist.discard(obj)
        return self

    def clear_object_positioning_blacklist(self) -> "LayoutObject":
        """
        Clear the position-change exclusion list.

        :return: This layout, allowing chained calls.
        """
        self._object_positioning_blacklist.clear()
        return self
    
    def mark_dirty(self) -> "LayoutObject":
        """
        Flag the layout for recalculation on the next update.

        :return: This layout, allowing chained calls.
        """
        self._dirty = True
        return self

    def request_relayout(self) -> "LayoutObject":
        """Request a layout recalculation on the next update."""
        return self.mark_dirty()

    def invalidate_layout(self) -> "LayoutObject":
        """Invalidate the layout and request recalculation."""
        return self.mark_dirty()
    
    def _check_if_dirty(self) -> None:
        """Mark the layout dirty when a child moved, resized, or changed anchor."""
        self._detect_child_transform_changes()

    def _detect_child_transform_changes(self) -> None:
        """Check placed children for transform changes and mark dirty if needed."""
        for obj in self._object_placements:
            if obj in self._dirty_checking_blacklist:
                continue

            pos, dims, anchor = self._dirty_checking_values.get(obj, (None, None, None))
            moved = obj not in self._object_positioning_blacklist and obj.pos != pos
            if moved or obj.dims != dims or obj.anchor != anchor:
                self._dirty = True
                return

    _check_if_children_changed = _detect_child_transform_changes
    
    # endregion
    
    # region UPDATE
    
    def _update_layering(self) -> "LayoutObject":
        """
        Assign sub-layers to children according to the layering priority.

        :return: This layout, allowing chained calls.
        """
        return self._apply_layering_to_children()

    def _apply_layering_to_children(self) -> "LayoutObject":
        """Apply z-ordering to placed children based on layering priority."""
        if not self._layering_priority:
            return self

        priority = self._layering_priority.upper()
        vertical_first = "TOP_BOTTOM_" in priority or "BOTTOM_TOP_" in priority
        top_first = "TOP_BOTTOM" in priority
        left_first = "LEFT_RIGHT" in priority

        col_count = max(1, self.max_col + 1)
        row_count = max(1, self.max_row + 1)

        for obj, (x, y) in self._object_placements.items():
            layer_x = x if left_first else (col_count - 1 - x)
            layer_y = y if top_first else (row_count - 1 - y)

            if vertical_first:
                layer = layer_x + layer_y * col_count
            else:
                layer = layer_y + layer_x * row_count

            obj.sub_layer = layer

        return self

    _sort_children_by_priority = _apply_layering_to_children
    
    def _update_self(self, dt: float) -> "LayoutObject":
        """
        Recalculate tracks and positions when the layout is dirty.

        :param dt: Seconds elapsed since the previous update.
        :return: This layout after the update.
        """
        super()._update_self(dt)
        if self._dirty_checking and not self._dirty:
            self._check_for_layout_changes()
        if self._dirty:
            self._perform_layout_pass()
        return self

    def _check_for_layout_changes(self) -> None:
        """Detect child movement/resizing/anchor changes and mark layout dirty."""
        self._check_if_dirty()

    def _perform_layout_pass(self) -> "LayoutObject":
        """Run the full layout pipeline in phases."""
        self._on_before_layout()
        self._prepare_layout()
        self._compute_track_sizes()
        self._compute_layout_dimensions()
        self._fit_tracks_to_space()
        self._compute_track_offsets()
        self._position_children()
        self._apply_child_layering()
        self._finalize_layout()
        self._on_after_layout()
        return self

    def _on_before_layout(self) -> None:
        """Hook called before layout recalculation begins."""
        pass

    def _on_after_layout(self) -> None:
        """Hook called after layout recalculation completes."""
        pass

    def _prepare_layout(self) -> None:
        """Reset layout caches before computing new track sizes."""
        pass

    def _compute_track_sizes(self) -> None:
        """Compute initial track sizes from placed children."""
        self._calculate_col_and_row_dims()

    def _compute_layout_dimensions(self) -> None:
        """Compute total content and layout dimensions."""
        self._calculate_dims()

    def _fit_tracks_to_space(self) -> None:
        """Fit tracks to available space based on fit/overflow modes."""
        self._fit_col_and_row_dims()

    def _position_children(self) -> None:
        """Position all children within their cells."""
        self._position_objects()

    def _apply_child_layering(self) -> "LayoutObject":
        """Apply z-ordering to children based on layering priority."""
        return self._update_layering()

    def _finalize_layout(self) -> None:
        """Apply computed layout size and clear dirty flag."""
        self.width = self._calculated_width
        self.height = self._calculated_height
        self._dirty = False
    
    # endregion
    
    # region MISC
    
    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"LayoutObject({self._mode}, children={len(self._object_placements)}, dirty={self._dirty})"

    def make_reorderable(self, placeholder_style: Optional[RectStyle] = None) -> "LayoutObject":
        """
        Attach drag-and-drop reordering with an optional placeholder style.

        :param placeholder_style: Optional rectangle style for the drag placeholder.
        :return: This layout, allowing chained calls.
        """
        self.add_behavior(ReorderableLayoutBehavior(placeholder_style or RectStyle()))
        return self
    
    # endregion
