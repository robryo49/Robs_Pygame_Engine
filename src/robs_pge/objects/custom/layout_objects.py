from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast
from .primitive_objects import RectObject
from ..behaviors import *
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, clamp, vec2


CellPos = tuple[int, int]

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
        


class LayoutObject(RectObject):
    GRID_MODE: Literal["grid"] = "grid"
    COL_MODE: Literal["columns"] = "columns"
    ROW_MODE: Literal["rows"] = "rows"
    
    STRETCH_MODE: Literal["stretch"] = "stretch"
    PRESERVE_MODE: Literal["preserve"] = "preserve"

    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
        
        # obj -> cell_x, cell_y, cell_anchor
        self._object_placements: dict[PygameObject, tuple[CellPos, vec2]] = {}
        
        self._dirty: bool = False
        self._dirty_checking: bool = True
        self._dirty_checking_values: dict[PygameObject, tuple[vec2, vec2, vec2]] = {}
        
        self._max_col = 0
        self._max_cols = {}
        self._max_row = 0
        self._max_rows = {}
        
        self._mode: Literal["grid", "columns", "rows"] = self.GRID_MODE
        self._fit_mode: Literal["stretch", "preserve"] = self.STRETCH_MODE
        self._overflow_mode: Literal["stretch", "preserve"] = self.STRETCH_MODE
        self._justification: vec2 = Anchor.C
        
        self._content_offset = vec2()
        
        self._width_constraint: SizeConstraint = SizeConstraint()
        self._height_constraint: SizeConstraint = SizeConstraint()
        
        self._col_width_constraint: SizeConstraint = SizeConstraint()
        self._col_widths_constraints: dict[int, SizeConstraint] = {}
        
        self._row_height_constraint: SizeConstraint = SizeConstraint()
        self._row_heights_constraints: dict[int, SizeConstraint] = {}
        
        self._outer_padding: vec2 = vec2()
        self._cell_spacing: vec2 = vec2()
        self._cell_padding: vec2 = vec2()
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
        
    # region PROPERTIES
    
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
    
    # region mode
    @property
    def mode(self) -> Literal["grid", "columns", "rows"]:
        return cast(Literal["grid", "columns", "rows"], self._mode)
    
    @mode.setter
    def mode(self, value: Literal["grid", "columns", "rows"]):
        self._mode = value
        self.mark_dirty()
    # endregion
    
    # region fit_mode
    @property
    def fit_mode(self) -> Literal["stretch", "preserve"]:
        return cast(Literal["stretch", "preserve"], self._fit_mode)
    
    @fit_mode.setter
    def fit_mode(self, value: Literal["stretch", "preserve"]):
        self._fit_mode = value
        self.mark_dirty()
    # endregion
    
    # region overflow_mode
    @property
    def overflow_mode(self) -> Literal["stretch", "preserve"]:
        return cast(Literal["stretch", "preserve"], self._overflow_mode)
    
    @overflow_mode.setter
    def overflow_mode(self, value: Literal["stretch", "preserve"]):
        self._overflow_mode = value
        self.mark_dirty()
    # endregion
    
    # region justification
    @property
    def justification(self) -> vec2:
        return self._justification
    
    @justification.setter
    def justification(self, value: vec2):
        self._justification = value
        self.mark_dirty()
    # endregion
    
    # region content_offset
    @property
    def content_offset(self) -> vec2:
        return vec2(self._content_offset)
    
    @content_offset.setter
    def content_offset(self, value: vec2):
        self._content_offset = value
        self.mark_dirty()
    # endregion
    
    # region content_offset_y
    @property
    def content_offset_y(self) -> float:
        return self._content_offset.y
    
    @content_offset_y.setter
    def content_offset_y(self, value: float):
        self._content_offset.y = value
        self.mark_dirty()
    # endregion
    
    # region content_offset_x
    @property
    def content_offset_x(self) -> float:
        return self._content_offset.x
    
    @content_offset_x.setter
    def content_offset_x(self, value: float):
        self._content_offset.x = value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def _get_cell_padding(self, cell: Optional[CellPos] = None) -> vec2:
        return self._cell_paddings.get(cell, self._cell_padding) if cell is not None else self._cell_padding
    
    def _apply_col_width_constraints(self, col: int, width: int) -> int:
        constraint = self._col_widths_constraints.get(col)
        if constraint is not None:
            return constraint.apply(width)
        return self._col_width_constraint.apply(width)
    
    def _apply_row_height_constraints(self, row: int, height: int) -> int:
        constraint = self._row_heights_constraints.get(row)
        if constraint is not None:
            return constraint.apply(height)
        return self._row_height_constraint.apply(height)
    
    def _calculate_cell_dim(self, obj: PygameObject, cell: CellPos):
        return obj.dims + 2 * self._get_cell_padding(cell)
    
    def _calculate_col_and_row_dims(self) -> None:
        self._calculated_col_widths.clear()
        self._calculated_row_heights.clear()
        self._row_mode_calculated_col_widths.clear()
        self._col_mode_calculated_row_heights.clear()
        
        for obj, (cell, _) in self._object_placements.items():
            col, row = cell
            cell_width, cell_height = self._calculate_cell_dim(obj, cell)
            cell_width = round(cell_width)
            cell_height = round(cell_height)
            
            if self._mode == self.GRID_MODE:
                self._calculated_col_widths[col] = max(self._calculated_col_widths.get(col, 0), cell_width)
                self._calculated_row_heights[row] = max(self._calculated_row_heights.get(row, 0), cell_height)
            
            elif self._mode == self.ROW_MODE:
                calculated_col_widths = self._row_mode_calculated_col_widths.setdefault(row, {})
                calculated_col_widths[col] = max(calculated_col_widths.get(col, 0), cell_width)
                self._calculated_row_heights[row] = max(self._calculated_row_heights.get(row, 0), cell_height)
            
            elif self._mode == self.COL_MODE:
                self._calculated_col_widths[col] = max(self._calculated_col_widths.get(col, 0), cell_width)
                calculated_row_heights = self._col_mode_calculated_row_heights.setdefault(col, {})
                calculated_row_heights[row] = max(calculated_row_heights.get(row, 0), cell_height)
        
        for col, width in self._calculated_col_widths.items():
            self._calculated_col_widths[col] = self._apply_col_width_constraints(col, width)
        
        for row, height in self._calculated_row_heights.items():
            self._calculated_row_heights[row] = self._apply_row_height_constraints(row, height)
        
        for row, calculated_col_widths in self._row_mode_calculated_col_widths.items():
            for col, width in calculated_col_widths.items():
                calculated_col_widths[col] = self._apply_col_width_constraints(col, width)
        
        for col, calculated_row_heights in self._col_mode_calculated_row_heights.items():
            for row, height in calculated_row_heights.items():
                calculated_row_heights[row] = self._apply_row_height_constraints(row, height)
    
    @staticmethod
    def _calculate_offsets(dimensions: dict[int, int], spacing: int) -> dict[int, int]:
        offsets: dict[int, int] = {}
        
        offset = 0
        for index in sorted(dimensions.keys()):
            offsets[index] = offset
            offset += dimensions[index] + spacing
        
        return offsets
    
    @staticmethod
    def _calculate_total_size(dimensions: dict[int, int], spacing: int) -> int:
        if not dimensions:
            return 0
        
        return sum(dimensions.values()) + spacing * (len(dimensions) - 1)
    
    @staticmethod
    def _fit_dimensions(dimensions: dict[int, int], target_size: int, spacing: int, constraints: dict[int, SizeConstraint], default_constraint: SizeConstraint, stretch: bool) -> None:
        if not dimensions:
            return
        
        target_size = max(0, target_size - spacing * (len(dimensions) - 1))
        indices = sorted(dimensions.keys())
        
        if not stretch:
            return
        
        current_size = sum(dimensions.values())
        
        if current_size == target_size:
            return
        
        if current_size <= 0:
            share = target_size / len(indices)
            for index in indices:
                dimensions[index] = round(share)
            
            return
        
        if target_size > current_size:
            remaining = target_size - current_size
            active = set(indices)
            
            while remaining > 0 and active:
                total_weight = sum(dimensions[index] for index in active)
                
                if total_weight <= 0:
                    break
                
                changes: dict[int, int] = {}
                consumed = 0
                constrained = set()
                
                for index in active:
                    old_size = dimensions[index]
                    ideal = remaining * old_size / total_weight
                    proposed = old_size + ideal
                    
                    constraint = constraints.get(index, default_constraint)
                    constrained_size = constraint.apply(round(proposed))
                    
                    delta = constrained_size - old_size
                    
                    if delta < 0:
                        delta = 0
                    
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
            active = set(indices)
            
            while remaining > 0 and active:
                total_weight = sum(dimensions[index] for index in active)
                
                if total_weight <= 0:
                    break
                
                changes: dict[int, int] = {}
                consumed = 0
                constrained = set()
                
                for index in active:
                    old_size = dimensions[index]
                    ideal = remaining * old_size / total_weight
                    proposed = old_size - ideal
                    
                    constraint = constraints.get(index, default_constraint)
                    constrained_size = constraint.apply(round(proposed))
                    
                    delta = old_size - constrained_size
                    
                    if delta < 0:
                        delta = 0
                    
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
        self._fit_dimensions(
            dimensions, target_size, round(self._cell_spacing.x), self._col_widths_constraints, self._col_width_constraint,
            self._fit_mode == self.STRETCH_MODE or self._overflow_mode == self.STRETCH_MODE
        )
    
    def _fit_row_dimensions(self, dimensions: dict[int, int], target_size: int) -> None:
        self._fit_dimensions(
            dimensions, target_size, round(self._cell_spacing.y), self._row_heights_constraints, self._row_height_constraint,
            self._fit_mode == self.STRETCH_MODE or self._overflow_mode == self.STRETCH_MODE
        )
    
    def _calculate_dims(self):
        outer_pad_x, outer_pad_y = self._outer_padding
        outer_pad_x = round(outer_pad_x)
        outer_pad_y = round(outer_pad_y)
        
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        if self._mode == self.GRID_MODE:
            self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        elif self._mode == self.ROW_MODE:
            self._row_mode_calculated_row_widths = {
                row: self._calculate_total_size(calculated_col_widths, spacing_x)
                for row, calculated_col_widths in self._row_mode_calculated_col_widths.items()
            }
            
            self._calculated_row_widths = max(self._row_mode_calculated_row_widths.values(), default=0)
            self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        elif self._mode == self.COL_MODE:
            self._calculated_col_mode_col_heights = {
                col: self._calculate_total_size(calculated_row_heights, spacing_y)
                for col, calculated_row_heights in self._col_mode_calculated_row_heights.items()
            }
            
            self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            self._calculated_col_heights = max(self._calculated_col_mode_col_heights.values(), default=0)
        
        self._calculated_width = self._width_constraint.apply(self._calculated_row_widths + 2 * outer_pad_x)
        self._calculated_height = self._height_constraint.apply(self._calculated_col_heights + 2 * outer_pad_y)
    
    def _fit_col_and_row_dims(self):
        outer_pad_x, outer_pad_y = self._outer_padding
        outer_pad_x = round(outer_pad_x)
        outer_pad_y = round(outer_pad_y)
        
        available_width = max(0, self._calculated_width - 2 * outer_pad_x)
        available_height = max(0, self._calculated_height - 2 * outer_pad_y)
        
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        if self._mode == self.GRID_MODE:
            current_width = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            current_height = self._calculate_total_size(self._calculated_row_heights, spacing_y)
            
            if current_width < available_width and self._fit_mode == self.STRETCH_MODE:
                    self._fit_col_dimensions(self._calculated_col_widths, available_width)
            
            elif current_width > available_width and self._overflow_mode == self.STRETCH_MODE:
                    self._fit_col_dimensions(self._calculated_col_widths, available_width)
            
            if current_height < available_height and self._fit_mode == self.STRETCH_MODE:
                    self._fit_row_dimensions(self._calculated_row_heights, available_height)
            
            elif current_height > available_height and self._overflow_mode == self.STRETCH_MODE:
                    self._fit_row_dimensions(self._calculated_row_heights, available_height)
        
        elif self._mode == self.ROW_MODE:
            for row, calculated_col_widths in self._row_mode_calculated_col_widths.items():
                current_width = self._calculate_total_size(calculated_col_widths, spacing_x)
                
                if current_width < available_width and self._fit_mode == self.STRETCH_MODE:
                        self._fit_col_dimensions(calculated_col_widths, available_width)
                
                elif current_width > available_width and self._overflow_mode == self.STRETCH_MODE:
                        self._fit_col_dimensions(calculated_col_widths, available_width)
            
            current_height = self._calculate_total_size(self._calculated_row_heights, spacing_y)
            
            if current_height < available_height and self._fit_mode == self.STRETCH_MODE:
                    self._fit_row_dimensions(self._calculated_row_heights, available_height)
            
            elif current_height > available_height and self._overflow_mode == self.STRETCH_MODE:
                    self._fit_row_dimensions(self._calculated_row_heights, available_height)
        
        elif self._mode == self.COL_MODE:
            current_width = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            
            if current_width < available_width and self._fit_mode == self.STRETCH_MODE:
                self._fit_col_dimensions(self._calculated_col_widths, available_width)
            
            elif current_width > available_width and self._overflow_mode == self.STRETCH_MODE:
                self._fit_col_dimensions(self._calculated_col_widths, available_width)
            
            for col, calculated_row_heights in self._col_mode_calculated_row_heights.items():
                current_height = self._calculate_total_size(calculated_row_heights, spacing_y)
                
                if current_height < available_height and self._fit_mode == self.STRETCH_MODE:
                    self._fit_row_dimensions(calculated_row_heights, available_height)
                
                elif current_height > available_height and self._overflow_mode == self.STRETCH_MODE:
                    self._fit_row_dimensions(calculated_row_heights, available_height)
    
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
        
        elif self._mode == self.ROW_MODE:
            self._row_mode_calculated_col_offsets = {
                row: self._calculate_offsets(calculated_col_widths, spacing_x)
                for row, calculated_col_widths in self._row_mode_calculated_col_widths.items()
            }
            
            self._calculated_row_offsets = self._calculate_offsets(self._calculated_row_heights, spacing_y)
            
            self._row_mode_calculated_row_widths = {
                row: self._calculate_total_size(calculated_col_widths, spacing_x)
                for row, calculated_col_widths in self._row_mode_calculated_col_widths.items()
            }
            
            self._calculated_col_heights = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        elif self._mode == self.COL_MODE:
            self._calculated_col_offsets = self._calculate_offsets(self._calculated_col_widths, spacing_x)
            
            self._col_mode_calculated_row_offsets = {
                col: self._calculate_offsets(calculated_row_heights, spacing_y)
                for col, calculated_row_heights in self._col_mode_calculated_row_heights.items()
            }
            
            self._calculated_row_widths = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            
            self._col_mode_calculated_col_heights = {
                col: self._calculate_total_size(calculated_row_heights, spacing_y)
                for col, calculated_row_heights in self._col_mode_calculated_row_heights.items()
            }
            
            self._calculated_col_heights = max(self._col_mode_calculated_col_heights.values(), default=0)
    
    def _get_cell_offset(self, cell: CellPos):
        col, row = cell
        
        if self._mode == self.GRID_MODE:
            return self._calculated_col_offsets.get(col, 0), self._calculated_row_offsets.get(row, 0)
        
        if self._mode == self.ROW_MODE:
            return self._row_mode_calculated_col_offsets.get(row, {}).get(col, 0), self._calculated_row_offsets.get(row, 0)
        
        if self._mode == self.COL_MODE:
            return self._calculated_col_offsets.get(col, 0), self._col_mode_calculated_row_offsets.get(col, {}).get(row, 0)
        
        return 0, 0
    
    def _get_cell_size(self, cell: CellPos):
        col, row = cell
        
        if self._mode == self.GRID_MODE:
            return self._calculated_col_widths.get(col, 0), self._calculated_row_heights.get(row, 0)
        
        if self._mode == self.ROW_MODE:
            return self._row_mode_calculated_col_widths.get(row, {}).get(col, 0), self._calculated_row_heights.get(row, 0)
        
        if self._mode == self.COL_MODE:
            return self._calculated_col_widths.get(col, 0), self._col_mode_calculated_row_heights.get(col, {}).get(row, 0)
        
        return 0, 0
    
    def _position_objects(self):
        outer_pad_x, outer_pad_y = self._outer_padding
        outer_pad_x = round(outer_pad_x)
        outer_pad_y = round(outer_pad_y)
        
        justify_x, justify_y = self._justification
        
        spacing_x = round(self._cell_spacing.x)
        spacing_y = round(self._cell_spacing.y)
        
        layout_w, layout_h = self._calculated_width, self._calculated_height
        
        if self._mode == self.GRID_MODE:
            content_w = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            content_h = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        elif self._mode == self.ROW_MODE:
            content_w = max(self._row_mode_calculated_row_widths.values(), default=0)
            content_h = self._calculate_total_size(self._calculated_row_heights, spacing_y)
        
        elif self._mode == self.COL_MODE:
            content_w = self._calculate_total_size(self._calculated_col_widths, spacing_x)
            content_h = max(self._col_mode_calculated_col_heights.values(), default=0)
        
        else:
            content_w = 0
            content_h = 0
        
        start_x = round(outer_pad_x + (layout_w - 2 * outer_pad_x - content_w) * justify_x)
        start_y = round(outer_pad_y + (layout_h - 2 * outer_pad_y - content_h) * justify_y)
        
        content_offset_x = self._content_offset.x
        content_offset_y = self._content_offset.y
        
        for obj, (cell, (cell_anchor_x, cell_anchor_y)) in self._object_placements.items():
            cell_offset_x, cell_offset_y = self._get_cell_offset(cell)
            cell_w, cell_h = self._get_cell_size(cell)
            
            cell_pad_x, cell_pad_y = self._get_cell_padding(cell)
            
            obj_w, obj_h = round(obj.dims.x), round(obj.dims.y)
            obj_anchor_x, obj_anchor_y = obj.anchor
            
            cell_x = start_x + cell_offset_x
            cell_y = start_y + cell_offset_y
            
            anchor_x = cell_x + cell_w * cell_anchor_x
            anchor_y = cell_y + cell_h * cell_anchor_y
            
            anchor_x += cell_pad_x * (1 - 2 * cell_anchor_x)
            anchor_y += cell_pad_y * (1 - 2 * cell_anchor_y)
            
            obj_x = anchor_x + obj_w * (obj_anchor_x - cell_anchor_x) + content_offset_x
            obj_y = anchor_y + obj_h * (obj_anchor_y - cell_anchor_y) + content_offset_y
            
            obj.x_pos = round(obj_x)
            obj.y_pos = round(obj_y)
            
            self._dirty_checking_values[obj] = (obj.pos, obj.dims, obj.anchor)
    
    
    
    def set_width_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None, fixed_value: Optional[int] = None) -> LayoutObject:
        self._width_constraint.min = min_value
        self._width_constraint.max = max_value
        self._width_constraint.fixed = fixed_value
        self.mark_dirty()
        return self
        
    def set_fixed_width(self, value: int) -> LayoutObject:
        self._width_constraint.fixed = value
        self.mark_dirty()
        return self
    
    def set_min_width(self, value: int) -> LayoutObject:
        self._width_constraint.min = value
        self.mark_dirty()
        return self
        
    def set_max_width(self, value: int) -> LayoutObject:
        self._width_constraint.max = value
        self.mark_dirty()
        return self
        
        
    def set_height_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None, fixed_value: Optional[int] = None) -> LayoutObject:
        self._height_constraint.min = min_value
        self._height_constraint.max = max_value
        self._height_constraint.fixed = fixed_value
        self.mark_dirty()
        return self
        
    def set_fixed_height(self, value: int) -> LayoutObject:
        self._height_constraint.fixed = value
        self.mark_dirty()
        return self
    
    def set_min_height(self, value: int) -> LayoutObject:
        self._height_constraint.min = value
        self.mark_dirty()
        return self
        
    def set_max_height(self, value: int) -> LayoutObject:
        self._height_constraint.max = value
        self.mark_dirty()
        return self
    
    
    def _get_col_constraint(self, col: Optional[int]) -> SizeConstraint:
        if col is None:
            return self._col_width_constraint
        return self._col_widths_constraints.setdefault(col, SizeConstraint())
    
    def _get_row_constraint(self, row: Optional[int]) -> SizeConstraint:
        if row is None:
            return self._row_height_constraint
        return self._row_heights_constraints.setdefault(row, SizeConstraint())
    
    # --- Column Constraints ---
    
    def set_col_width_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None, fixed_value: Optional[int] = None, col: Optional[int] = None) -> LayoutObject:
        constraint = self._get_col_constraint(col)
        constraint.min = min_value
        constraint.max = max_value
        constraint.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_col_width(self, value: int, col: Optional[int] = None) -> LayoutObject:
        self._get_col_constraint(col).fixed = value
        self.mark_dirty()
        return self
    
    def set_min_col_width(self, value: int, col: Optional[int] = None) -> LayoutObject:
        self._get_col_constraint(col).min = value
        self.mark_dirty()
        return self
    
    def set_max_col_width(self, value: int, col: Optional[int] = None) -> LayoutObject:
        self._get_col_constraint(col).max = value
        self.mark_dirty()
        return self
    
    # --- Row Constraints ---
    
    def set_row_height_constraint(self, min_value: Optional[int] = None, max_value: Optional[int] = None, fixed_value: Optional[int] = None, row: Optional[int] = None) -> LayoutObject:
        constraint = self._get_row_constraint(row)
        constraint.min = min_value
        constraint.max = max_value
        constraint.fixed = fixed_value
        self.mark_dirty()
        return self
    
    def set_fixed_row_height(self, value: int, row: Optional[int] = None) -> LayoutObject:
        self._get_row_constraint(row).fixed = value
        self.mark_dirty()
        return self
    
    def set_min_row_height(self, value: int, row: Optional[int] = None) -> LayoutObject:
        self._get_row_constraint(row).min = value
        self.mark_dirty()
        return self
    
    def set_max_row_height(self, value: int, row: Optional[int] = None) -> LayoutObject:
        self._get_row_constraint(row).max = value
        self.mark_dirty()
        return self
        
    
    def set_outer_padding(self, value: int | vec2) -> LayoutObject:
        self._outer_padding = vec2(value)
        self.mark_dirty()
        return self
    
    def set_cell_spacing(self, value: int | vec2) -> LayoutObject:
        self._cell_spacing = vec2(value)
        self.mark_dirty()
        return self
        
    def set_cell_padding(self, value: int | vec2, cell: Optional[CellPos] = None) -> LayoutObject:
        if cell is None:
            self._cell_padding = vec2(value)
        else:
            self._cell_paddings[cell] = vec2(value)
        self.mark_dirty()
        return self
            
    def set_constant_padding(self, value: int | vec2) -> LayoutObject:
        self.set_outer_padding(value)
        self.set_cell_spacing(value)
        return self
    
    
    def set_content_offset(self, value: vec2) -> LayoutObject:
        self._content_offset = value
        self.mark_dirty()
        return self
    
    def set_content_offset_x(self, value: float) -> LayoutObject:
        self._content_offset.x = value
        self.mark_dirty()
        return self
    
    def set_content_offset_y(self, value: float) -> LayoutObject:
        self._content_offset.y = value
        self.mark_dirty()
        return self
    
    
    def set_mode(self, mode: Literal["grid", "rows", "columns"]) -> LayoutObject:
        self._mode = mode
        self.mark_dirty()
        return self
    
    def set_fit_mode(self, mode: Literal["stretch", "preserve"]) -> LayoutObject:
        self._fit_mode = mode
        self.mark_dirty()
        return self
    
    def set_overflow_mode(self, mode: Literal["stretch", "preserve"]) -> LayoutObject:
        self._overflow_mode = mode
        self.mark_dirty()
        return self
    
    def set_justify(self, value: vec2) -> LayoutObject:
        self._justification = value
        self.mark_dirty()
        return self
    
    
    def mark_dirty(self):
        self._dirty = True
    
    def add(self, obj: PygameObject, x: int, y: int, anchor: vec2 = Anchor.C):
        
        self._max_col = max(self._max_col, x)
        self._max_cols[y] = max(self._max_cols.get(y, 0), x)
        self._max_row = max(self._max_row, y)
        self._max_rows[x] = max(self._max_rows.get(x, 0), y)
        
        self._object_placements[obj] = ((x, y), anchor)
        self.add_child(obj, Anchor.TL)
        self.mark_dirty()
        
    def stack_x(self, obj: PygameObject, y: int = 0, anchor: vec2 = Anchor.C):
        self.add(obj, self._max_cols.get(y, 0) + 1, y, anchor)
        
    def stack_y(self, obj: PygameObject, x: int = 0, anchor: vec2 = Anchor.C):
        self.add(obj, x, self._max_rows.get(x, 0) + 1, anchor)
        
        
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
