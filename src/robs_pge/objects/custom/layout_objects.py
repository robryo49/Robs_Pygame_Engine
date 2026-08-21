from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from .primitive_objects import RectObject
from ..behaviors import *
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, vec2

CellPos = tuple[int, int]
FitMode = Literal["stretch", "preserve"]
LayoutMode = Literal["grid", "columns", "rows"]

@dataclass
class SizeConstraint:
    min: Optional[int] = None
    max: Optional[int] = None
    fixed: Optional[int] = None
    
    def apply(self, value: int) -> int:
        if self.fixed is not None:
            return self.fixed
        if self.min is not None and value < self.min:
            return self.min
        if self.max is not None and value > self.max:
            return self.max
        return value
    
    def __iter__(self):
        return iter([self.min, self.max, self.fixed])
    
    def copy(self):
        return SizeConstraint(self.min, self.max, self.fixed)


class LayoutObject(RectObject):
    Mode = LayoutMode
    FitMode = FitMode
    
    GRID_MODE: Literal["grid"] = "grid"
    COL_MODE: Literal["columns"] = "columns"
    ROW_MODE: Literal["rows"] = "rows"
    
    STRETCH_MODE: Literal["stretch"] = "stretch"
    PRESERVE_MODE: Literal["preserve"] = "preserve"
    
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection,
                 sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
        
        # obj -> top-left cell
        self._object_placements: dict[PygameObject, CellPos] = {}
        # obj -> (span_x, span_y)
        self._object_spans: dict[PygameObject, tuple[int, int]] = {}
        
        self._dirty = False
        self._dirty_checking = True
        self._dirty_checking_values: dict[PygameObject, tuple[vec2, vec2, vec2]] = {}
        
        self._max_col = 0
        self._max_cols: dict[int, int] = {}
        self._next_cols: dict[int, int] = {}
        self._max_row = 0
        self._max_rows: dict[int, int] = {}
        self._next_rows: dict[int, int] = {}
        
        self._mode: LayoutMode = self.GRID_MODE
        self._justification = Anchor.C
        
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
        
        self._calculated_width = 0
        self._calculated_height = 0
        self._calculated_col_widths: dict[int, int] = {}
        self._calculated_row_heights: dict[int, int] = {}
        self._row_mode_calculated_col_widths: dict[int, dict[int, int]] = {}
        self._col_mode_calculated_row_heights: dict[int, dict[int, int]] = {}
        
        self._calculated_col_offsets: dict[int, int] = {}
        self._calculated_row_offsets: dict[int, int] = {}
        self._row_mode_calculated_col_offsets: dict[int, dict[int, int]] = {}
        self._col_mode_calculated_row_offsets: dict[int, dict[int, int]] = {}
        
        self._calculated_row_widths = 0
        self._calculated_col_heights = 0
        self._row_mode_calculated_row_widths: dict[int, int] = {}
        self._col_mode_calculated_col_heights: dict[int, int] = {}
    
    # ------------------------------------------------------------------ properties
    
    @property
    def dirty(self) -> bool:
        return self._dirty
    
    @property
    def max_col(self) -> int:
        return self._max_col
    
    @property
    def max_cols(self) -> dict[int, int]:
        return dict(self._max_cols)
    
    @property
    def max_row(self) -> int:
        return self._max_row
    
    @property
    def max_rows(self) -> dict[int, int]:
        return dict(self._max_rows)
    
    @property
    def object_spans(self) -> dict[PygameObject, tuple[int, int]]:
        return dict(self._object_spans)
    
    @property
    def outer_padding(self) -> vec2:
        return self._outer_padding
    
    @outer_padding.setter
    def outer_padding(self, value: vec2 | int):
        self._outer_padding = vec2(value)
        self.mark_dirty()
    
    @property
    def cell_spacing(self) -> vec2:
        return self._cell_spacing
    
    @cell_spacing.setter
    def cell_spacing(self, value: vec2 | int):
        self._cell_spacing = vec2(value)
        self.mark_dirty()
    
    @property
    def cell_padding(self) -> vec2:
        return self._cell_padding
    
    @cell_padding.setter
    def cell_padding(self, value: vec2 | int):
        self._cell_padding = vec2(value)
        self.mark_dirty()
    
    @property
    def mode(self) -> Literal["grid", "columns", "rows"]:
        return cast(Literal["grid", "columns", "rows"], self._mode)
    
    @mode.setter
    def mode(self, value: Literal["grid", "columns", "rows"]):
        self._mode = value
        self.mark_dirty()
    
    @property
    def fit_mode(self) -> FitMode:
        return cast(FitMode, self._fit_mode)
    
    @fit_mode.setter
    def fit_mode(self, value: FitMode):
        self._fit_mode = value
        self.mark_dirty()
    
    @property
    def overflow_mode(self) -> FitMode:
        return cast(FitMode, self._overflow_mode)
    
    @overflow_mode.setter
    def overflow_mode(self, value: FitMode):
        self._overflow_mode = value
        self.mark_dirty()
    
    @property
    def horizontal_fit_mode(self) -> FitMode:
        return cast(FitMode, self._horizontal_fit_mode or self._fit_mode)
    
    @horizontal_fit_mode.setter
    def horizontal_fit_mode(self, value: Optional[FitMode]):
        self._horizontal_fit_mode = value
        self.mark_dirty()
    
    @property
    def vertical_fit_mode(self) -> FitMode:
        return cast(FitMode, self._vertical_fit_mode or self._fit_mode)
    
    @vertical_fit_mode.setter
    def vertical_fit_mode(self, value: Optional[FitMode]):
        self._vertical_fit_mode = value
        self.mark_dirty()
    
    @property
    def horizontal_overflow_mode(self) -> FitMode:
        return cast(FitMode, self._horizontal_overflow_mode or self._overflow_mode)
    
    @horizontal_overflow_mode.setter
    def horizontal_overflow_mode(self, value: Optional[FitMode]):
        self._horizontal_overflow_mode = value
        self.mark_dirty()
    
    @property
    def vertical_overflow_mode(self) -> FitMode:
        return cast(FitMode, self._vertical_overflow_mode or self._overflow_mode)
    
    @vertical_overflow_mode.setter
    def vertical_overflow_mode(self, value: Optional[FitMode]):
        self._vertical_overflow_mode = value
        self.mark_dirty()
    
    @property
    def justification(self) -> vec2:
        return self._justification
    
    @justification.setter
    def justification(self, value: vec2):
        self._justification = value
        self.mark_dirty()
    
    @property
    def content_offset(self) -> vec2:
        return vec2(self._content_offset)
    
    @content_offset.setter
    def content_offset(self, value: vec2):
        self._content_offset = value
        self.mark_dirty()
    
    @property
    def content_offset_x(self) -> float:
        return self._content_offset.x
    
    @content_offset_x.setter
    def content_offset_x(self, value: float):
        self._content_offset.x = value
        self.mark_dirty()
    
    @property
    def content_offset_y(self) -> float:
        return self._content_offset.y
    
    @content_offset_y.setter
    def content_offset_y(self, value: float):
        self._content_offset.y = value
        self.mark_dirty()
    
    # ------------------------------------------------------------------ helpers
    
    def _get_cell_padding(self, cell: Optional[CellPos] = None) -> vec2:
        return self._cell_paddings.get(cell, self._cell_padding) if cell is not None else self._cell_padding
    
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
    
    def _calculate_cell_dims(self, obj: PygameObject, cell: CellPos) -> tuple[int, int]:
        pad = self._get_cell_padding(cell)
        return round(obj.dims.x + 2 * pad.x), round(obj.dims.y + 2 * pad.y)
    
    def _get_span(self, obj: PygameObject) -> tuple[int, int]:
        return self._object_spans.get(obj, (1, 1))
    
    def _validate_span(self, span: tuple[int, int]) -> tuple[int, int]:
        sx, sy = span
        if sx < 1 or sy < 1:
            raise ValueError("span_x and span_y must both be >= 1")
        return int(sx), int(sy)
    
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
    
    @staticmethod
    def _indices_between(start: int, span: int) -> list[int]:
        return list(range(start, start + span))
    
    def _ensure_span_requirement(self, dimensions: dict[int, int], indices: list[int], required_size: int, spacing: int,
                                 constraints: dict[int, SizeConstraint], default_constraint: SizeConstraint) -> None:
        current = sum(dimensions.get(i, 0) for i in indices) + spacing * max(0, len(indices) - 1)
        if current >= required_size:
            return
        tmp = {i: dimensions.get(i, 0) for i in indices}
        self._fit_dimensions(tmp, required_size, spacing, constraints, default_constraint, True, set(indices))
        dimensions.update(tmp)
    
    # ------------------------------------------------------------------ dimensions / span resolution
    
    def _collect_tracks(self) -> tuple[set[int], set[int]]:
        cols: set[int] = set()
        rows: set[int] = set()
        for obj, (x, y) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            cols.update(range(x, x + sx))
            rows.update(range(y, y + sy))
        return cols, rows
    
    def _calculate_col_and_row_dims(self) -> None:
        self._calculated_col_widths.clear()
        self._calculated_row_heights.clear()
        self._row_mode_calculated_col_widths.clear()
        self._col_mode_calculated_row_heights.clear()
        
        cols, rows = self._collect_tracks()
        for col in cols:
            self._calculated_col_widths[col] = 0
        for row in rows:
            self._calculated_row_heights[row] = 0
        
        for obj, (col, row) in self._object_placements.items():
            sx, sy = self._get_span(obj)
            cell_w, cell_h = self._calculate_cell_dims(obj, (col, row))
            
            if self._mode == self.GRID_MODE:
                if sx == 1:
                    self._calculated_col_widths[col] = max(self._calculated_col_widths.get(col, 0), cell_w)
                if sy == 1:
                    self._calculated_row_heights[row] = max(self._calculated_row_heights.get(row, 0), cell_h)
            
            elif self._mode == self.ROW_MODE:
                for r in self._indices_between(row, sy):
                    row_widths = self._row_mode_calculated_col_widths.setdefault(r, {})
                    if r == row:
                        for c in self._indices_between(col, sx):
                            row_widths.setdefault(c, 0)
                        if sx == 1:
                            row_widths[col] = max(row_widths.get(col, 0), cell_w)
                if sy == 1:
                    self._calculated_row_heights[row] = max(self._calculated_row_heights.get(row, 0), cell_h)
            
            elif self._mode == self.COL_MODE:
                self._calculated_col_widths[col] = max(self._calculated_col_widths.get(col, 0), cell_w if sx == 1 else 0)
                for c in self._indices_between(col, sx):
                    col_heights = self._col_mode_calculated_row_heights.setdefault(c, {})
                    if c == col:
                        for r in self._indices_between(row, sy):
                            col_heights.setdefault(r, 0)
                        if sy == 1:
                            col_heights[row] = max(col_heights.get(row, 0), cell_h)
        
        for col in sorted(cols):
            self._calculated_col_widths[col] = self._apply_col_width_constraints(col, self._calculated_col_widths.get(col, 0))
        for row in sorted(rows):
            self._calculated_row_heights[row] = self._apply_row_height_constraints(row, self._calculated_row_heights.get(row, 0))
        
        for row, widths in self._row_mode_calculated_col_widths.items():
            for col in list(widths):
                widths[col] = self._apply_col_width_constraints(col, widths[col])
        
        for col, heights in self._col_mode_calculated_row_heights.items():
            for row in list(heights):
                heights[row] = self._apply_row_height_constraints(row, heights[row])
        
        for _ in range(16):
            changed = False
            before = self._snapshot_dimensions()
            
            for obj, (col, row) in self._object_placements.items():
                sx, sy = self._get_span(obj)
                req_w, req_h = self._calculate_cell_dims(obj, (col, row))
                cols = self._indices_between(col, sx)
                rows = self._indices_between(row, sy)
                
                if self._mode == self.GRID_MODE:
                    self._ensure_span_requirement(self._calculated_col_widths, cols, req_w, round(self._cell_spacing.x),
                                                  self._col_widths_constraints, self._col_width_constraint)
                    self._ensure_span_requirement(self._calculated_row_heights, rows, req_h, round(self._cell_spacing.y),
                                                  self._row_heights_constraints, self._row_height_constraint)
                
                elif self._mode == self.ROW_MODE:
                    anchor_widths = self._row_mode_calculated_col_widths.setdefault(row, {})
                    for c in cols:
                        anchor_widths.setdefault(c, 0)
                    self._ensure_span_requirement(anchor_widths, cols, req_w, round(self._cell_spacing.x),
                                                  self._col_widths_constraints, self._col_width_constraint)
                    self._ensure_span_requirement(self._calculated_row_heights, rows, req_h, round(self._cell_spacing.y),
                                                  self._row_heights_constraints, self._row_height_constraint)
                
                elif self._mode == self.COL_MODE:
                    self._ensure_span_requirement(self._calculated_col_widths, cols, req_w, round(self._cell_spacing.x),
                                                  self._col_widths_constraints, self._col_width_constraint)
                    anchor_heights = self._col_mode_calculated_row_heights.setdefault(col, {})
                    for r in rows:
                        anchor_heights.setdefault(r, 0)
                    self._ensure_span_requirement(anchor_heights, rows, req_h, round(self._cell_spacing.y),
                                                  self._row_heights_constraints, self._row_height_constraint)
            
            after = self._snapshot_dimensions()
            changed = before != after
            if not changed:
                break
    
    def _snapshot_dimensions(self):
        return (
            tuple(sorted(self._calculated_col_widths.items())),
            tuple(sorted(self._calculated_row_heights.items())),
            tuple((r, tuple(sorted(v.items()))) for r, v in sorted(self._row_mode_calculated_col_widths.items())),
            tuple((c, tuple(sorted(v.items()))) for c, v in sorted(self._col_mode_calculated_row_heights.items())),
        )
    
    # ------------------------------------------------------------------ size / fitting
    
    def _calculate_dims(self):
        outer_pad_x = round(self._outer_padding.x)
        outer_pad_y = round(self._outer_padding.y)
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        if self._mode == self.GRID_MODE:
            self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        elif self._mode == self.ROW_MODE:
            self._row_mode_calculated_row_widths = {
                row: self._calculate_total_size(widths, spacing_x)
                for row, widths in self._row_mode_calculated_col_widths.items()
            }
            self._calculated_row_widths = max(self._row_mode_calculated_row_widths.values(), default=0)
            self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        else:
            self._col_mode_calculated_col_heights = {
                col: self._calculate_total_size(heights, spacing_y)
                for col, heights in self._col_mode_calculated_row_heights.items()
            }
            self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            self._calculated_col_heights = max(self._col_mode_calculated_col_heights.values(), default=0)
        
        self._calculated_width = self._width_constraint.apply(self._calculated_row_widths + 2 * outer_pad_x)
        self._calculated_height = self._height_constraint.apply(self._calculated_col_heights + 2 * outer_pad_y)
    
    def _fit_col_and_row_dims(self):
        outer_pad_x = round(self._outer_padding.x)
        outer_pad_y = round(self._outer_padding.y)
        available_width = max(0, self._calculated_width - 2 * outer_pad_x)
        available_height = max(0, self._calculated_height - 2 * outer_pad_y)
        
        if self._mode == self.GRID_MODE:
            current_width = self._calculate_total_size(self._calculated_col_widths, round(self._cell_spacing.x))
            current_height = self._calculate_total_size(self._calculated_row_heights, round(self._cell_spacing.y))
            if ((current_width < available_width and self._get_fit_mode(True) == self.STRETCH_MODE) or
                    (current_width > available_width and self._get_overflow_mode(True) == self.STRETCH_MODE)):
                self._fit_col_dimensions(self._calculated_col_widths, available_width)
            if ((current_height < available_height and self._get_fit_mode(False) == self.STRETCH_MODE) or
                    (current_height > available_height and self._get_overflow_mode(False) == self.STRETCH_MODE)):
                self._fit_row_dimensions(self._calculated_row_heights, available_height)
        
        elif self._mode == self.ROW_MODE:
            for row, widths in self._row_mode_calculated_col_widths.items():
                current = self._calculate_total_size(widths, round(self._cell_spacing.x))
                if ((current < available_width and self._get_fit_mode(True) == self.STRETCH_MODE) or
                        (current > available_width and self._get_overflow_mode(True) == self.STRETCH_MODE)):
                    self._fit_local_col_dimensions(row, widths, available_width)
            current_height = self._calculate_total_size(self._calculated_row_heights, round(self._cell_spacing.y))
            if ((current_height < available_height and self._get_fit_mode(False) == self.STRETCH_MODE) or
                    (current_height > available_height and self._get_overflow_mode(False) == self.STRETCH_MODE)):
                self._fit_row_dimensions(self._calculated_row_heights, available_height)
        
        else:
            current_width = self._calculate_total_size(self._calculated_col_widths, round(self._cell_spacing.x))
            if ((current_width < available_width and self._get_fit_mode(True) == self.STRETCH_MODE) or
                    (current_width > available_width and self._get_overflow_mode(True) == self.STRETCH_MODE)):
                self._fit_col_dimensions(self._calculated_col_widths, available_width)
            for col, heights in self._col_mode_calculated_row_heights.items():
                current = self._calculate_total_size(heights, round(self._cell_spacing.y))
                if ((current < available_height and self._get_fit_mode(False) == self.STRETCH_MODE) or
                        (current > available_height and self._get_overflow_mode(False) == self.STRETCH_MODE)):
                    self._fit_local_row_dimensions(col, heights, available_height)
    
    # ------------------------------------------------------------------ spanning cuts
    
    def _build_col_mode_cuts(self) -> dict[int, list[tuple[int, int, int, int, PygameObject]]]:
        """For each column, return (start_row, end_row, start_y, end_y, object) barriers."""
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
        """For each row, return (start_col, end_col, start_x, end_x, object) barriers."""
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
                left = {c: widths[c] for c in ordered_cols if c < start_col and c >= previous_col}
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
    
    def _calculate_row_and_col_offsets(self):
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        self._calculated_col_offsets.clear()
        self._calculated_row_offsets.clear()
        self._row_mode_calculated_col_offsets.clear()
        self._col_mode_calculated_row_offsets.clear()
        
        if self._mode == self.GRID_MODE:
            self._calculated_col_offsets = self._calculate_offsets(self._calculated_col_widths, spacing_x)
            self._calculated_row_offsets = self._calculate_offsets(self._calculated_row_heights, spacing_y)
            self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
            return
        
        if self._mode == self.ROW_MODE:
            cuts = self._build_row_mode_cuts()
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
            return
        
        cuts = self._build_col_mode_cuts()
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
    
    # ------------------------------------------------------------------ cells / positioning
    
    def _get_cell_anchor(self, cell: CellPos) -> vec2:
        return self._cell_anchors.get(cell, self._cell_anchor)
    
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
        outer_pad_x = round(self._outer_padding.x)
        outer_pad_y = round(self._outer_padding.y)
        justify_x, justify_y = self._justification
        layout_w, layout_h = self._calculated_width, self._calculated_height
        
        if self._mode == self.GRID_MODE:
            content_w = self._calculate_total_size(self._calculated_col_widths, round(self._cell_spacing.x))
            content_h = self._calculate_total_size(self._calculated_row_heights, round(self._cell_spacing.y))
        elif self._mode == self.ROW_MODE:
            content_w = max(self._row_mode_calculated_row_widths.values(), default=0)
            content_h = self._calculate_total_size(self._calculated_row_heights, round(self._cell_spacing.y))
        else:
            content_w = self._calculate_total_size(self._calculated_col_widths, round(self._cell_spacing.x))
            content_h = max(self._col_mode_calculated_col_heights.values(), default=0)
        
        start_x = round(outer_pad_x + (layout_w - 2 * outer_pad_x - content_w) * justify_x)
        start_y = round(outer_pad_y + (layout_h - 2 * outer_pad_y - content_h) * justify_y)
        
        for obj, cell in self._object_placements.items():
            cell_anchor_x, cell_anchor_y = self._get_cell_anchor(cell)
            cell_offset_x, cell_offset_y = self._get_object_cell_offset(obj, cell)
            cell_w, cell_h = self._span_dimensions(obj, cell)
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
            
            obj.x_pos = round(obj_x)
            obj.y_pos = round(obj_y)
            self._dirty_checking_values[obj] = (obj.pos, obj.dims, obj.anchor)
    
    # ------------------------------------------------------------------ setters / public API
    
    def set_width_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                             fixed_value: Optional[int] = None) -> "LayoutObject":
        self._width_constraint.min = min_value
        self._width_constraint.max = max_value
        self._width_constraint.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_width(self, value: int) -> "LayoutObject":
        self._width_constraint.fixed = value; self.mark_dirty(); return self
    
    def set_min_width(self, value: int) -> "LayoutObject":
        self._width_constraint.min = value; self.mark_dirty(); return self
    
    def set_max_width(self, value: int) -> "LayoutObject":
        self._width_constraint.max = value; self.mark_dirty(); return self
    
    def set_height_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                              fixed_value: Optional[int] = None) -> "LayoutObject":
        self._height_constraint.min = min_value
        self._height_constraint.max = max_value
        self._height_constraint.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_height(self, value: int) -> "LayoutObject":
        self._height_constraint.fixed = value; self.mark_dirty(); return self
    
    def set_min_height(self, value: int) -> "LayoutObject":
        self._height_constraint.min = value; self.mark_dirty(); return self
    
    def set_max_height(self, value: int) -> "LayoutObject":
        self._height_constraint.max = value; self.mark_dirty(); return self
    
    def set_col_width_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                                 fixed_value: Optional[int] = None, col: Optional[int] = None) -> "LayoutObject":
        c = self._get_col_constraint(col); c.min = min_value; c.max = max_value; c.fixed = fixed_value
        self.mark_dirty(); return self
    
    def set_fixed_col_width(self, value: int, col: Optional[int] = None) -> "LayoutObject":
        self._get_col_constraint(col).fixed = value; self.mark_dirty(); return self
    
    def set_min_col_width(self, value: int, col: Optional[int] = None) -> "LayoutObject":
        self._get_col_constraint(col).min = value; self.mark_dirty(); return self
    
    def set_max_col_width(self, value: int, col: Optional[int] = None) -> "LayoutObject":
        self._get_col_constraint(col).max = value; self.mark_dirty(); return self
    
    def set_row_height_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None,
                                  fixed_value: Optional[int] = None, row: Optional[int] = None) -> "LayoutObject":
        c = self._get_row_constraint(row); c.min = min_value; c.max = max_value; c.fixed = fixed_value
        self.mark_dirty(); return self
    
    def set_fixed_row_height(self, value: int, row: Optional[int] = None) -> "LayoutObject":
        self._get_row_constraint(row).fixed = value; self.mark_dirty(); return self
    
    def set_min_row_height(self, value: int, row: Optional[int] = None) -> "LayoutObject":
        self._get_row_constraint(row).min = value; self.mark_dirty(); return self
    
    def set_max_row_height(self, value: int, row: Optional[int] = None) -> "LayoutObject":
        self._get_row_constraint(row).max = value; self.mark_dirty(); return self
    
    def set_outer_padding(self, value: int | vec2) -> "LayoutObject":
        self.outer_padding = value; return self
    
    def set_cell_spacing(self, value: int | vec2) -> "LayoutObject":
        self.cell_spacing = value; return self
    
    def set_cell_padding(self, value: int | vec2, cell: Optional[CellPos] = None) -> "LayoutObject":
        if cell is None: self._cell_padding = vec2(value)
        else: self._cell_paddings[cell] = vec2(value)
        self.mark_dirty(); return self
    
    def set_constant_padding(self, value: int | vec2) -> "LayoutObject":
        return self.set_outer_padding(value).set_cell_spacing(value)
    
    def set_cell_anchor(self, value: vec2, cell: Optional[CellPos] = None) -> "LayoutObject":
        if cell is None: self._cell_anchor = vec2(value)
        else: self._cell_anchors[cell] = vec2(value)
        self.mark_dirty(); return self
    
    def set_content_offset(self, value: vec2) -> "LayoutObject":
        self.content_offset = value; return self
    
    def set_content_offset_x(self, value: float) -> "LayoutObject":
        self.content_offset_x = value; return self
    
    def set_content_offset_y(self, value: float) -> "LayoutObject":
        self.content_offset_y = value; return self
    
    def set_mode(self, mode: Literal["grid", "rows", "columns"]) -> "LayoutObject":
        self.mode = mode; return self
    
    def set_fit_mode(self, mode: FitMode) -> "LayoutObject":
        self.fit_mode = mode; return self
    
    def set_horizontal_fit_mode(self, mode: FitMode, col: Optional[int] = None) -> "LayoutObject":
        if col is None: self._horizontal_fit_mode = mode
        else: self._col_horizontal_fit_modes[col] = mode
        self.mark_dirty(); return self
    
    def set_vertical_fit_mode(self, mode: FitMode, row: Optional[int] = None) -> "LayoutObject":
        if row is None: self._vertical_fit_mode = mode
        else: self._row_vertical_fit_modes[row] = mode
        self.mark_dirty(); return self
    
    def set_overflow_mode(self, mode: FitMode) -> "LayoutObject":
        self.overflow_mode = mode; return self
    
    def set_horizontal_overflow_mode(self, mode: FitMode, col: Optional[int] = None) -> "LayoutObject":
        if col is None: self._horizontal_overflow_mode = mode
        else: self._col_horizontal_overflow_modes[col] = mode
        self.mark_dirty(); return self
    
    def set_vertical_overflow_mode(self, mode: FitMode, row: Optional[int] = None) -> "LayoutObject":
        if row is None: self._vertical_overflow_mode = mode
        else: self._row_vertical_overflow_modes[row] = mode
        self.mark_dirty(); return self
    
    def set_justify(self, value: vec2) -> "LayoutObject":
        self.justification = value; return self
    
    def add(self, obj: PygameObject, x: int, y: int, anchor: Optional[vec2] = None,
            span: tuple[int, int] = (1, 1)):
        span = self._validate_span(span)
        sx, sy = span
        
        new_cells = {(cx, cy) for cx in range(x, x + sx) for cy in range(y, y + sy)}
        for other, (ox, oy) in self._object_placements.items():
            if other is obj:
                continue
            osx, osy = self._get_span(other)
            old_cells = {(cx, cy) for cx in range(ox, ox + osx) for cy in range(oy, oy + osy)}
            if new_cells & old_cells:
                raise ValueError(f"Object {obj!r} overlaps existing object {other!r}")
        
        self._max_col = max(self._max_col, x + sx - 1)
        self._max_row = max(self._max_row, y + sy - 1)
        self._max_cols[y] = max(self._max_cols.get(y, -1), x + sx - 1)
        self._max_rows[x] = max(self._max_rows.get(x, -1), y + sy - 1)
        self._next_cols[y] = max(self._next_cols.get(y, 0), x + sx)
        self._next_rows[x] = max(self._next_rows.get(x, 0), y + sy)
        
        self._object_placements[obj] = (x, y)
        self._object_spans[obj] = span
        if anchor is not None:
            self.set_cell_anchor(anchor, (x, y))
        self.add_child(obj, Anchor.TL)
        self.mark_dirty()
        return self
    
    def set_span(self, obj: PygameObject, span_x: int = 1, span_y: int = 1) -> "LayoutObject":
        if obj not in self._object_placements:
            raise KeyError("Object is not part of this layout")
        
        old_span = self._object_spans.get(obj, (1, 1))
        self._object_spans[obj] = self._validate_span((span_x, span_y))
        
        try:
            occupied: dict[tuple[int, int], PygameObject] = {}
            for other, (x, y) in self._object_placements.items():
                sx, sy = self._get_span(other)
                for cx in range(x, x + sx):
                    for cy in range(y, y + sy):
                        previous = occupied.get((cx, cy))
                        if previous is not None and previous is not other:
                            raise ValueError(f"Object {other!r} overlaps existing object {previous!r}")
                        occupied[(cx, cy)] = other
        except Exception:
            self._object_spans[obj] = old_span
            raise
        
        x, y = self._object_placements[obj]
        sx, sy = self._get_span(obj)
        self._max_col = max(self._max_col, x + sx - 1)
        self._max_row = max(self._max_row, y + sy - 1)
        self._next_cols[y] = max(self._next_cols.get(y, 0), x + sx)
        self._next_rows[x] = max(self._next_rows.get(x, 0), y + sy)
        self.mark_dirty()
        return self
    
    def stack_x(self, obj: PygameObject, y: int = 0, anchor: vec2 = Anchor.C,
                span: tuple[int, int] = (1, 1)):
        sx, _ = self._validate_span(span)
        self.add(obj, self._next_cols.get(y, 0), y, anchor, span)
        self._next_cols[y] = self._object_placements[obj][0] + sx
        return self
    
    def stack_y(self, obj: PygameObject, x: int = 0, anchor: vec2 = Anchor.C,
                span: tuple[int, int] = (1, 1)):
        _, sy = self._validate_span(span)
        self.add(obj, x, self._next_rows.get(x, 0), anchor, span)
        self._next_rows[x] = self._object_placements[obj][1] + sy
        return self
    
    # ------------------------------------------------------------------ update
    
    def mark_dirty(self):
        self._dirty = True
    
    def _dirty_check(self):
        for obj in self._object_placements:
            pos, dims, anchor = self._dirty_checking_values.get(obj, (None, None, None))
            if obj.pos != pos or obj.dims != dims or obj.anchor != anchor:
                self._dirty = True
                return
    
    def _update_self(self, dt: float) -> PygameObject:
        super()._update_self(dt)
        if self._dirty_checking:
            self._dirty_check()
        if self._dirty:
            self._calculate_col_and_row_dims()
            self._calculate_dims()
            self._fit_col_and_row_dims()
            self._calculate_row_and_col_offsets()
            self._position_objects()
            self.width = self._calculated_width
            self.height = self._calculated_height
            self._dirty = False
        return self
    
    def __repr__(self) -> str:
        return f"LayoutObject({id(self)})"
