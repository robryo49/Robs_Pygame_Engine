from __future__ import annotations

from typing import Literal

from .primitive_objects import RectObject
from ..behaviors import *
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, clamp, vec2


class LayoutObject(RectObject):
    GRID_MODE = "grid"
    COL_MOD = "columns"
    ROW_MOD = "rows"

    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)

        # === Core data model ===
        # object → (col, row, span_x, span_y)
        self._placements: dict[PygameObject, tuple[int, int, int, int]] = {}

        # Column/row configuration: index → {"fixed": bool, "size": float, "min_size": float}
        self._cols: dict[int, dict[str, float | bool]] = {}
        self._rows: dict[int, dict[str, float | bool]] = {}

        # For columns mode: per-column row heights {col: {row: height}}
        self._col_row_heights: dict[int, dict[int, float]] = {}

        # For rows mode: per-row column widths {row: {col: width}}
        self._row_col_widths: dict[int, dict[int, float]] = {}

        # Spacing & padding
        self._spacing: vec2 = vec2(0, 0)
        self._padding: vec2 = vec2(0, 0)
        self._cells_padding: dict[tuple[int, int], vec2] = {}

        # Layout mode
        self._mode: str = self.GRID_MODE

        # Sizing behavior
        self._fixed_width: Optional[float] = None
        self._fixed_height: Optional[float] = None

        # Scroll
        self._scroll_offset: vec2 = vec2(0, 0)
        self._scroll_speed: float = 15.0

        # Flip
        self._flip_x: bool = False
        self._flip_y: bool = False

        # Dirty tracking via version counter
        self._layout_version: int = 0
        self._last_solved_version: int = -1

        # Precomputed data (solved each layout pass)
        self._solved_col_widths: dict[int, float] = {}
        self._solved_row_heights: dict[int, float] = {}
        self._col_offsets: dict[int, float] = {}
        self._row_offsets: dict[int, float] = {}
        self._col_row_offsets: dict[int, dict[int, float]] = {}
        self._content_size: vec2 = vec2(0, 0)

    # region PROPERTIES

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: Literal["grid", "columns", "rows"]) -> None:
        if value not in (self.GRID_MODE, self.COL_MOD, self.ROW_MOD):
            raise ValueError(f"Invalid layout mode '{value}'. Use 'grid', 'columns', or 'rows'.")
        self._mode = value
        self._mark_dirty()

    @property
    def spacing(self) -> vec2:
        return self._spacing

    @spacing.setter
    def spacing(self, value: vec2 | float) -> None:
        self._spacing = vec2(value)
        self._mark_dirty()

    def set_spacing(self, value: vec2 | float) -> LayoutObject:
        self._spacing = vec2(value)
        self._mark_dirty()
        return self

    @property
    def padding(self) -> vec2:
        return self._padding

    @padding.setter
    def padding(self, value: vec2 | float) -> None:
        self._padding = vec2(value)
        self._mark_dirty()

    def set_padding(self, value: vec2 | float) -> LayoutObject:
        self._padding = vec2(value)
        self._mark_dirty()
        return self

    @property
    def scroll_offset(self) -> vec2:
        return self._scroll_offset

    @scroll_offset.setter
    def scroll_offset(self, value: vec2) -> None:
        if value != self._scroll_offset:
            self._scroll_offset = value
            self._mark_dirty()

    @property
    def fixed_width(self) -> Optional[float]:
        return self._fixed_width

    @property
    def fixed_height(self) -> Optional[float]:
        return self._fixed_height

    @property
    def flip_x(self) -> bool:
        return self._flip_x

    @flip_x.setter
    def flip_x(self, value: bool) -> None:
        self._flip_x = value
        self._mark_dirty()

    @property
    def flip_y(self) -> bool:
        return self._flip_y

    @flip_y.setter
    def flip_y(self, value: bool) -> None:
        self._flip_y = value
        self._mark_dirty()

    # endregion

    # region COLUMN / ROW CONFIGURATION

    def set_column_fixed(self, col: int, size: Optional[float] = None, fixed: bool = True) -> LayoutObject:
        cfg = self._cols.setdefault(col, {"fixed": False, "size": 0.0, "min_size": 0.0})
        cfg["fixed"] = fixed
        if size is not None:
            cfg["size"] = size
        self._mark_dirty()
        return self

    def set_row_fixed(self, row: int, size: Optional[float] = None, fixed: bool = True) -> LayoutObject:
        cfg = self._rows.setdefault(row, {"fixed": False, "size": 0.0, "min_size": 0.0})
        cfg["fixed"] = fixed
        if size is not None:
            cfg["size"] = size
        self._mark_dirty()
        return self

    def set_column_min_size(self, col: int, min_size: float) -> LayoutObject:
        cfg = self._cols.setdefault(col, {"fixed": False, "size": 0.0, "min_size": 0.0})
        cfg["min_size"] = min_size
        self._mark_dirty()
        return self

    def set_row_min_size(self, row: int, min_size: float) -> LayoutObject:
        cfg = self._rows.setdefault(row, {"fixed": False, "size": 0.0, "min_size": 0.0})
        cfg["min_size"] = min_size
        self._mark_dirty()
        return self

    # endregion

    # region SIZING

    def set_fixed_width(self, width: Optional[float]) -> LayoutObject:
        self._fixed_width = width
        self._mark_dirty()
        return self

    def set_fixed_height(self, height: Optional[float]) -> LayoutObject:
        self._fixed_height = height
        self._mark_dirty()
        return self

    def fit_width(self) -> LayoutObject:
        self._fixed_width = None
        self._mark_dirty()
        return self

    def fit_height(self) -> LayoutObject:
        self._fixed_height = None
        self._mark_dirty()
        return self

    # endregion

    # region OBJECT MANAGEMENT

    def add(self, obj: PygameObject, col: int, row: int, span_x: int = 1, span_y: int = 1, anchor: vec2 = Anchor.C) -> LayoutObject:
        self.add_child(obj)
        self._placements[obj] = (col, row, span_x, span_y)
        obj.anchor = anchor
        self._mark_dirty()
        return self

    def stack_y(self, obj: PygameObject, col: int = 0, anchor: vec2 = Anchor.C) -> LayoutObject:
        max_row = -1
        for _, (c, r, _, _) in ((o, p) for o, p in self._placements.items() if p[0] == col):
            if r > max_row:
                max_row = r
        return self.add(obj, col, max_row + 1, 1, 1, anchor)

    def stack_x(self, obj: PygameObject, row: int = 0, anchor: vec2 = Anchor.C) -> LayoutObject:
        max_col = -1
        for _, (c, r, _, _) in ((o, p) for o, p in self._placements.items() if p[1] == row):
            if c > max_col:
                max_col = c
        return self.add(obj, max_col + 1, row, 1, 1, anchor)

    def remove(self, obj: PygameObject) -> LayoutObject:
        self.remove_child(obj)
        self._placements.pop(obj, None)
        self._mark_dirty()
        return self

    def clear(self) -> LayoutObject:
        for obj in list(self._placements.keys()):
            self.remove_child(obj)
        self._placements.clear()
        self._mark_dirty()
        return self

    # endregion

    # region SCROLL

    def enable_scroll(self, speed: float = 15.0) -> LayoutObject:
        self._scroll_speed = speed
        self.do_on_scroll(lambda o, scroll, pos: o.apply_scroll(scroll))
        return self

    def apply_scroll(self, scroll: int) -> None:
        max_offset = self.get_scroll_range_y()
        new_y = clamp(self._scroll_offset.y + scroll * self._scroll_speed, 0, max_offset)
        self._scroll_offset = vec2(self._scroll_offset.x, new_y)
        self._mark_dirty()

    def get_viewport_height(self) -> float:
        return self._fixed_height if self._fixed_height is not None else self.height

    def get_scroll_range_y(self) -> float:
        content_height = self._content_size.y
        return max(0.0, content_height - self.get_viewport_height())

    # endregion

    # region LAYOUT SOLVING

    def _mark_dirty(self) -> None:
        self._layout_version += 1

    def _solve_layout(self) -> None:
        if self._layout_version == self._last_solved_version:
            return

        self._solve_sizes()
        self._compute_offsets()
        self._apply_fit_sizing()

        # Update renderer dims before positioning (anchor offset depends on this)
        if self.renderer:
            self.renderer.dims = vec2(
                self._fixed_width if self._fixed_width is not None else self._content_size.x,
                self._fixed_height if self._fixed_height is not None else self._content_size.y
            )

        self._position_objects()

        self._last_solved_version = self._layout_version

    def _solve_sizes(self) -> None:
        self._solved_col_widths = {}
        self._solved_row_heights = {}
        self._col_row_heights = {}
        self._row_col_widths = {}

        if self._mode == self.GRID_MODE:
            self._solve_grid_sizes()
        elif self._mode == self.COL_MOD:
            self._solve_columns_mode_sizes()
        elif self._mode == self.ROW_MOD:
            self._solve_rows_mode_sizes()

    def _solve_grid_sizes(self) -> None:
        # Reset auto-sized columns/rows
        for col_idx, cfg in self._cols.items():
            if not cfg["fixed"]:
                cfg["size"] = 0.0
        for row_idx, cfg in self._rows.items():
            if not cfg["fixed"]:
                cfg["size"] = 0.0

        # Measure objects (cell size = object size + 2 * padding)
        for obj, (col, row, span_x, span_y) in self._placements.items():
            obj_w, obj_h = obj.dims
            if obj_w <= 0 or obj_h <= 0:
                continue

            pad = self.get_cell_padding((col, row))
            total_w = obj_w + 2 * pad.x
            total_h = obj_h + 2 * pad.y

            for i in range(span_x):
                ci = col + i
                cfg = self._cols.setdefault(ci, {"fixed": False, "size": 0.0, "min_size": 0.0})
                if not cfg["fixed"]:
                    cfg["size"] = max(cfg["size"], total_w / span_x)

            for i in range(span_y):
                ri = row + i
                cfg = self._rows.setdefault(ri, {"fixed": False, "size": 0.0, "min_size": 0.0})
                if not cfg["fixed"]:
                    cfg["size"] = max(cfg["size"], total_h / span_y)

        # Apply minimums and store solved sizes
        for col_idx, cfg in self._cols.items():
            self._solved_col_widths[col_idx] = max(cfg["size"], cfg.get("min_size", 0.0))
        for row_idx, cfg in self._rows.items():
            self._solved_row_heights[row_idx] = max(cfg["size"], cfg.get("min_size", 0.0))

    def _solve_columns_mode_sizes(self) -> None:
        # Each column is independent: widths per-column, row heights per-column
        for col_idx, cfg in self._cols.items():
            if not cfg["fixed"]:
                cfg["size"] = 0.0

        for obj, (col, row, span_x, span_y) in self._placements.items():
            obj_w, obj_h = obj.dims
            if obj_w <= 0 or obj_h <= 0:
                continue

            pad = self.get_cell_padding((col, row))
            total_w = obj_w + 2 * pad.x
            total_h = obj_h + 2 * pad.y

            # Column width = widest object + padding
            col_width = total_w / span_x if span_x > 0 else total_w
            cfg = self._cols.setdefault(col, {"fixed": False, "size": 0.0, "min_size": 0.0})
            if not cfg["fixed"]:
                cfg["size"] = max(cfg["size"], col_width)

            # Per-column row heights (with padding)
            row_heights = self._col_row_heights.setdefault(col, {})
            for i in range(span_y):
                ri = row + i
                row_heights[ri] = max(row_heights.get(ri, 0.0), total_h / span_y)

        for col_idx, cfg in self._cols.items():
            self._solved_col_widths[col_idx] = max(cfg["size"], cfg.get("min_size", 0.0))

    def _solve_rows_mode_sizes(self) -> None:
        # Each row is independent: heights per-row, column widths per-row
        for row_idx, cfg in self._rows.items():
            if not cfg["fixed"]:
                cfg["size"] = 0.0

        for obj, (col, row, span_x, span_y) in self._placements.items():
            obj_w, obj_h = obj.dims
            if obj_w <= 0 or obj_h <= 0:
                continue

            pad = self.get_cell_padding((col, row))
            total_w = obj_w + 2 * pad.x
            total_h = obj_h + 2 * pad.y

            # Row height = tallest object + padding
            row_height = total_h / span_y if span_y > 0 else total_h
            cfg = self._rows.setdefault(row, {"fixed": False, "size": 0.0, "min_size": 0.0})
            if not cfg["fixed"]:
                cfg["size"] = max(cfg["size"], row_height)

            # Per-row column widths (with padding)
            col_widths = self._row_col_widths.setdefault(row, {})
            for i in range(span_x):
                ci = col + i
                col_widths[ci] = max(col_widths.get(ci, 0.0), total_w / span_x)

        for row_idx, cfg in self._rows.items():
            self._solved_row_heights[row_idx] = max(cfg["size"], cfg.get("min_size", 0.0))

    def _compute_offsets(self) -> None:
        # Column offsets (same for all modes)
        offset = self._padding.x
        for col_idx in sorted(self._solved_col_widths):
            self._col_offsets[col_idx] = offset
            offset += self._solved_col_widths[col_idx] + self._spacing.x
        content_w = offset - self._spacing.x + self._padding.x if self._solved_col_widths else self._padding.x * 2

        # Row offsets depend on mode
        if self._mode == self.GRID_MODE:
            offset = self._padding.y
            for row_idx in sorted(self._solved_row_heights):
                self._row_offsets[row_idx] = offset
                offset += self._solved_row_heights[row_idx] + self._spacing.y
            content_h = offset - self._spacing.y + self._padding.y if self._solved_row_heights else self._padding.y * 2
        elif self._mode == self.COL_MOD:
            self._col_row_offsets = {}
            max_content_h = 0.0
            for col_idx, row_heights in self._col_row_heights.items():
                offsets = {}
                offset = self._padding.y
                for row_idx in sorted(row_heights):
                    offsets[row_idx] = offset
                    offset += row_heights[row_idx] + self._spacing.y
                self._col_row_offsets[col_idx] = offsets
                col_h = offset - self._spacing.y + self._padding.y if row_heights else self._padding.y * 2
                max_content_h = max(max_content_h, col_h)
            content_h = max_content_h
        elif self._mode == self.ROW_MOD:
            self._row_col_offsets = {}
            max_content_w = 0.0
            for row_idx, col_widths in self._row_col_widths.items():
                offsets = {}
                offset = self._padding.x
                for col_idx in sorted(col_widths):
                    offsets[col_idx] = offset
                    offset += col_widths[col_idx] + self._spacing.x
                self._row_col_offsets[row_idx] = offsets
                row_w = offset - self._spacing.x + self._padding.x if col_widths else self._padding.x * 2
                max_content_w = max(max_content_w, row_w)
            content_w = max_content_w

            offset = self._padding.y
            for row_idx in sorted(self._solved_row_heights):
                self._row_offsets[row_idx] = offset
                offset += self._solved_row_heights[row_idx] + self._spacing.y
            content_h = offset - self._spacing.y + self._padding.y if self._solved_row_heights else self._padding.y * 2

        self._content_size = vec2(content_w, content_h)

    def _apply_fit_sizing(self) -> None:
        # Distribute extra space to non-fixed columns/rows when size is fixed
        if self._fixed_width is not None and self._solved_col_widths:
            free_cols = [ci for ci in self._solved_col_widths if not self._cols.get(ci, {}).get("fixed", False)]
            if free_cols:
                current_total = sum(self._solved_col_widths.values())
                target = self._fixed_width - self._padding.x * 2
                missing = target - current_total
                if missing != 0:
                    per_col = missing / len(free_cols)
                    for ci in free_cols:
                        self._solved_col_widths[ci] = max(0, self._solved_col_widths[ci] + per_col)
                # Recompute offsets
                self._recompute_col_offsets()
                self._content_size.x = self._fixed_width

        if self._fixed_height is not None:
            if self._mode == self.GRID_MODE and self._solved_row_heights:
                free_rows = [ri for ri in self._solved_row_heights if not self._rows.get(ri, {}).get("fixed", False)]
                if free_rows:
                    current_total = sum(self._solved_row_heights.values())
                    target = self._fixed_height - self._padding.y * 2
                    missing = target - current_total
                    if missing != 0:
                        per_row = missing / len(free_rows)
                        for ri in free_rows:
                            self._solved_row_heights[ri] = max(0, self._solved_row_heights[ri] + per_row)
                    self._recompute_row_offsets()
                    self._content_size.y = self._fixed_height

    def _recompute_col_offsets(self) -> None:
        offset = self._padding.x
        for col_idx in sorted(self._solved_col_widths):
            self._col_offsets[col_idx] = offset
            offset += self._solved_col_widths[col_idx] + self._spacing.x

    def _recompute_row_offsets(self) -> None:
        offset = self._padding.y
        for row_idx in sorted(self._solved_row_heights):
            self._row_offsets[row_idx] = offset
            offset += self._solved_row_heights[row_idx] + self._spacing.y

    def _position_objects(self) -> None:
        for obj, (col, row, span_x, span_y) in self._placements.items():
            obj_w, obj_h = obj.dims

            if self._mode == self.ROW_MOD:
                # Per-row column offsets and widths
                x = self._row_col_offsets.get(row, {}).get(col, self._padding.x)
                y = self._row_offsets.get(row, self._padding.y)

                col_widths = self._row_col_widths.get(row, {})
                cell_w = sum(col_widths.get(col + i, 0.0) for i in range(span_x)) + self._spacing.x * (span_x - 1)
                cell_h = sum(self._solved_row_heights.get(row + i, 0.0) for i in range(span_y)) + self._spacing.y * (span_y - 1)
            elif self._mode == self.COL_MOD:
                # Per-column row offsets and heights
                x = self._col_offsets.get(col, self._padding.x)
                y = self._col_row_offsets.get(col, {}).get(row, self._padding.y)

                cell_w = sum(self._solved_col_widths.get(col + i, 0.0) for i in range(span_x)) + self._spacing.x * (span_x - 1)
                row_heights = self._col_row_heights.get(col, {})
                cell_h = sum(row_heights.get(row + i, 0.0) for i in range(span_y)) + self._spacing.y * (span_y - 1)
            else:
                # Grid mode (shared rows/cols)
                x = self._col_offsets.get(col, self._padding.x)
                y = self._row_offsets.get(row, self._padding.y)

                cell_w = sum(self._solved_col_widths.get(col + i, 0.0) for i in range(span_x)) + self._spacing.x * (span_x - 1)
                cell_h = sum(self._solved_row_heights.get(row + i, 0.0) for i in range(span_y)) + self._spacing.y * (span_y - 1)

            # Per-cell padding
            pad = self.get_cell_padding((col, row))

            # Anchor offset within cell (padding pushes object inward from edges)
            anchor_x = cell_w * obj.anchor.x + pad.x * (1 - 2 * obj.anchor.x)
            anchor_y = cell_h * obj.anchor.y + pad.y * (1 - 2 * obj.anchor.y)

            pos = vec2(x + anchor_x, y + anchor_y)

            # Flip transform
            if self._flip_x:
                pos.x = self._content_size.x - pos.x - obj_w
            if self._flip_y:
                pos.y = self._content_size.y - pos.y - obj_h

            # Scroll offset
            pos -= self._scroll_offset

            # Convert to local space
            pos -= self.get_anchor_offset(self.anchor)

            obj.pos = pos

    # endregion

    # region UPDATE

    def _update_self(self, dt: float) -> LayoutObject:
        self.behaviors.on_update(dt)
        self._solve_layout()
        if self.renderer:
            self.renderer.update(dt)
        return self

    # endregion

    # region LEGACY COMPATIBILITY

    def fix_col_width(self, col: int, width: Optional[float] = None) -> LayoutObject:
        return self.set_column_fixed(col, width)

    def fix_row_height(self, row: int, height: Optional[float] = None) -> LayoutObject:
        return self.set_row_fixed(row, height)

    def unfix_col_width(self, col: int) -> LayoutObject:
        return self.set_column_fixed(col, fixed=False)

    def unfix_row_height(self, row: int) -> LayoutObject:
        return self.set_row_fixed(row, fixed=False)

    def fix_width(self, width: Optional[float] = None) -> LayoutObject:
        return self.set_fixed_width(width or self.width)

    def fix_height(self, height: Optional[float] = None) -> LayoutObject:
        return self.set_fixed_height(height or self.height)

    def unfix_width(self) -> LayoutObject:
        return self.set_fixed_width(None)

    def unfix_height(self) -> LayoutObject:
        return self.set_fixed_height(None)

    def set_constant_padding(self, padding: vec2 | float) -> LayoutObject:
        p = vec2(padding)
        self._spacing = p
        self._padding = vec2(0, 0)
        self._mark_dirty()
        return self

    def set_cell_padding(self, padding: vec2 | float, cell: Optional[tuple[int, int]] = None) -> LayoutObject:
        if cell is not None:
            self._cells_padding[cell] = vec2(padding)
        else:
            self._spacing = vec2(padding)
        self._mark_dirty()
        return self

    def get_cell_padding(self, cell: tuple[int, int]) -> vec2:
        return self._cells_padding.get(cell, self._spacing)

    def set_outer_padding(self, padding: vec2 | float) -> LayoutObject:
        self._padding = vec2(padding)
        self._mark_dirty()
        return self

    def clear_outer_padding(self) -> LayoutObject:
        self._padding = vec2(0, 0)
        if self.renderer:
            self.renderer.bd = 0
        self._mark_dirty()
        return self

    def invert_left_right(self) -> LayoutObject:
        self._flip_x = True
        self._mark_dirty()
        return self

    def invert_up_down(self) -> LayoutObject:
        self._flip_y = True
        self._mark_dirty()
        return self

    def add_object(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: vec2 = Anchor.C) -> LayoutObject:
        obj.anchor = anchor
        return self.add(obj, x, y, span_x, span_y, anchor)

    def remove_object(self, obj: PygameObject) -> LayoutObject:
        return self.remove(obj)

    @property
    def min_col(self) -> int:
        return 0

    @min_col.setter
    def min_col(self, value: int) -> None:
        pass

    @property
    def max_col(self) -> float:
        return float('inf')

    @max_col.setter
    def max_col(self, value: float) -> None:
        pass

    @property
    def min_row(self) -> int:
        return 0

    @min_row.setter
    def min_row(self, value: int) -> None:
        pass

    @property
    def max_row(self) -> float:
        return float('inf')

    @max_row.setter
    def max_row(self, value: float) -> None:
        pass

    @property
    def invert_x_order(self) -> bool:
        return self._flip_x

    @invert_x_order.setter
    def invert_x_order(self, value: bool) -> None:
        self._flip_x = value
        self._mark_dirty()

    @property
    def invert_y_order(self) -> bool:
        return self._flip_y

    @invert_y_order.setter
    def invert_y_order(self, value: bool) -> None:
        self._flip_y = value
        self._mark_dirty()

    # endregion

    def __repr__(self) -> str:
        return f"LayoutObject({id(self)})"


class DebugOverlay(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)

    def toggle(self) -> LayoutObject:
        self.visible = not self.visible
        return self

    def __repr__(self) -> str:
        return f"DebugOverlay({id(self)})"
