from .primitive_objects import RectObject, TextObject
from ..behaviors import *
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, Vec2, clamp, inf


class LayoutObject(RectObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        self._grid_objects_grid_positions: dict[PygameObject, tuple[int, int]] = {}
        self._grid_objects_spanning: dict[PygameObject, tuple[int, int]] = {}
        self._grid_objects_dims : dict[PygameObject, Vec2] = {}
        self._grid_objects_positions : dict[PygameObject, Vec2] = {}
        
        
        self._fixed_cols: dict[int, bool] = {}
        self._min_col_widths: dict[int, float] = {}
        
        self._col_widths: dict[int, float] = {}
        self._col_offsets: dict[int, float] = {}
        
        
        self._fixed_rows: dict[int, bool] = {}
        self._min_row_heights: dict[int, float] = {}
        
        self._row_heights: dict[int, float] = {}
        self._row_offsets: dict[int, float] = {}
        
        
        self._outer_padding: Vec2 = Vec2()
        self._padding: Vec2 = Vec2()
        self._cells_padding: dict[tuple[int, int], Vec2] = {}
        
        self._min_col = 0
        self._max_col = inf
        self._min_row = 0
        self._max_row = inf
        
        self._invert_y_order = False
        self._invert_x_order = False
        
        self._fixed_width = None
        self._fixed_height = None
        
        self._dirty = False
        self._dirty_check = True
        
        self._scroll_offset: Vec2 = Vec2()
        self._scroll_speed: float = 15.0
        
    
    # region PROPERITIES
    
    # region dirty_check
    @property
    def dirty_check(self):
        return self._dirty_check
    
    @dirty_check.setter
    def dirty_check(self, value):
        self._dirty_check = value
    
    def enable_dirty_check(self):
        self.dirty_check = True
    
    def disable_dirty_check(self):
        self.dirty_check = False
        self.check_if_dirty()
    
    def toggle_dirty_check(self):
        self.dirty_check = not self.dirty_check
        self.check_if_dirty()
    
    # endregion
    
    # region min_col
    @property
    def min_col(self):
        return self._min_col
    
    @min_col.setter
    def min_col(self, value):
        self._min_col = value
        
        for obj, pos in self._grid_objects_grid_positions.items():
            new = (max(value, self._grid_objects_grid_positions[obj][0]), self._grid_objects_grid_positions[obj][1])
            if new != self._grid_objects_grid_positions[obj]:
                self._grid_objects_grid_positions[obj] = new
                self.mark_dirty()
    # endregion
    
    # region max_col
    @property
    def max_col(self):
        return self._max_col
    
    @max_col.setter
    def max_col(self, value):
        self._max_col = value
        
        for obj, pos in self._grid_objects_grid_positions.items():
            new = (min(value, self._grid_objects_grid_positions[obj][0]), self._grid_objects_grid_positions[obj][1])
            if new != self._grid_objects_grid_positions[obj]:
                self._grid_objects_grid_positions[obj] = new
                self.mark_dirty()
    # endregion
    
    # region min_row
    @property
    def min_row(self):
        return self._min_row
    
    @min_row.setter
    def min_row(self, value):
        self._min_row = value
        
        for obj, pos in self._grid_objects_grid_positions.items():
            new = (self._grid_objects_grid_positions[obj][0], max(value, self._grid_objects_grid_positions[obj][1]))
            if new != self._grid_objects_grid_positions[obj]:
                self._grid_objects_grid_positions[obj] = new
                self.mark_dirty()
    # endregion
    
    # region max_row
    @property
    def max_row(self):
        return self._max_row
    
    @max_row.setter
    def max_row(self, value):
        self._max_row = value
        
        for obj, pos in self._grid_objects_grid_positions.items():
            new = (self._grid_objects_grid_positions[obj][0], min(value, self._grid_objects_grid_positions[obj][1]))
            if new != self._grid_objects_grid_positions[obj]:
                self._grid_objects_grid_positions[obj] = new
                self.mark_dirty()
    # endregion
    
    # region invert_x_order
    @property
    def invert_x_order(self):
        return self._invert_x_order
    
    @invert_x_order.setter
    def invert_x_order(self, value):
        self._invert_x_order = value
        self.mark_dirty()
    # endregion
    
    # region invert_y_order
    @property
    def invert_y_order(self):
        return self._invert_y_order
    
    @invert_y_order.setter
    def invert_y_order(self, value):
        self._invert_y_order = value
        self.mark_dirty()
    # endregion
    
    # region scroll_offset
    @property
    def scroll_offset(self):
        return self._scroll_offset
    
    @scroll_offset.setter
    def scroll_offset(self, value: Vec2):
        if value != self._scroll_offset:
            self._scroll_offset = value
            self.mark_dirty()
    # endregion
    
    # endregion
    
    
    def fix_col_width(self, col_x: int, width: Optional[int | float] = None):
        if width is not None:
            self._col_widths[col_x] = width
        self._fixed_cols[col_x] = True
        
        self.mark_dirty()
        return self
    
    def fix_row_height(self, row_y: int, height: Optional[int | float] = None):
        if height is not None:
            self._row_heights[row_y] = height
        self._fixed_rows[row_y] = True
        
        self.mark_dirty()
        return self
    
    def unfix_col_width(self, col_x: int):
        self._fixed_cols[col_x] = False
        
        self.mark_dirty()
        return self
    
    def unfix_row_height(self, row_y: int):
        self._fixed_rows[row_y] = False
        
        self.mark_dirty()
        return self
    
    
    def fix_width(self, width: Optional[int | float] = None):
        self._fixed_width = width or self.width
        
        self.mark_dirty()
        return self
    
    def fix_height(self, height: Optional[int | float] = None):
        self._fixed_height = height or self.height
        
        self.mark_dirty()
        return self
    
    def unfix_width(self):
        self._fixed_width = None
        
        self.mark_dirty()
        return self
    
    def unfix_height(self):
        self._fixed_height = None
        
        self.mark_dirty()
        return self
    
    
    def invert_left_right(self):
        self._invert_x_order = True
        self.mark_dirty()
        return self
    
    def invert_up_down(self):
        self._invert_y_order = True
        self.mark_dirty()
        return self
    
    
    def set_constant_padding(self, padding: Vec2 | int):
        self.set_cell_padding(padding / 2)
        self.set_outer_padding(padding / 2)
        return self
    
    def set_cell_padding(self, padding: Vec2 | int | float, cell: Optional[tuple[int, int]] = None):
        if cell is not None:
            self._cells_padding[cell] = Vec2(padding)
        else:
            self._padding = Vec2(padding)
        
        self.mark_dirty()
        return self
    
    def clear_cell_padding(self, cell: Optional[tuple[int, int]] = None):
        if cell is not None:
            self._cells_padding.pop(cell, 0)
        else:
            self._padding = Vec2()
        
        self.mark_dirty()
        return self
    
    def set_outer_padding(self, padding: Vec2 | int | float):
        padding = Vec2(padding)
        self._outer_padding = padding
        self.mark_dirty()
        return self
    
    def clear_outer_padding(self):
        self._outer_padding = Vec2()
        self.renderer.bd = 0
        self.mark_dirty()
        return self
    
    
    def get_scroll_range_y(self) -> float:
        content_height = sum(self._row_heights.values())
        viewport_height = self._fixed_height if self._fixed_height is not None else self.height
        return max(0.0, content_height - viewport_height)
    
    def enable_scroll(self, speed: float = 15.0):
        self._scroll_speed = speed
        self.do_on_scroll(lambda o, scroll, pos: o.apply_scroll(scroll))
        return self
    
    def apply_scroll(self, scroll: int):
        max_offset = self.get_scroll_range_y()
        new_y = clamp(self.scroll_offset.y - scroll * self._scroll_speed, 0, max_offset)
        self.scroll_offset = Vec2(self.scroll_offset.x, new_y)
    
    
    def get_col_width(self, grid_x: int, span: int = 0):
        return sum(self._col_widths.get(grid_x + offset, 0) for offset in range(span + 1))
    
    def get_row_height(self, grid_y: int, span: int = 0):
        return sum(self._row_heights.get(grid_y + offset, 0) for offset in range(span + 1))
    
    def get_obj_pos(self, obj: PygameObject):
        grid_x, grid_y = grid_pos = self._grid_objects_grid_positions.get(obj, (0, 0))
        span_x, span_y = self._grid_objects_spanning.get(obj, (0, 0))
        pad_x, pad_y = self._cells_padding.get(grid_pos, self._padding)
        
        obj_offset_x = sum(self.get_col_width(col_x) for col_x in range(grid_x, grid_x + span_x)) * (obj.anchor.x if not self._invert_x_order else (1 - obj.anchor.x))
        obj_offset_y = sum(self.get_row_height(row_y) for row_y in range(grid_y, grid_y + span_y)) * (obj.anchor.y if not self._invert_y_order else (1 - obj.anchor.y))
        
        cell_x =  self._col_offsets[grid_x] + obj_offset_x + pad_x * (1 - 2 * obj.anchor.x) * (1 if not self._invert_x_order else -1)
        cell_y = self._row_offsets[grid_y] + obj_offset_y + pad_y * (1 - 2 * obj.anchor.y) * (1 if not self._invert_y_order else -1)
        
        if self._invert_x_order:
            cell_x = self.width - self._outer_padding.x * 2 - cell_x
        
        if self._invert_y_order:
            cell_y = self.height - self._outer_padding.y * 2 - cell_y
        
        
        return Vec2(cell_x, cell_y) + self._outer_padding - self.get_anchor_offset(Anchor.C) - Vec2(0, self.get_scroll_range_y()) + self._scroll_offset
    
    
    
    def add_object(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: Vec2 = Anchor.C):
        self.add_child(obj)
        
        self._grid_objects_grid_positions[obj] = (clamp(x, self._min_col, self._max_col), clamp(y, self._min_row, self._max_row))
        self._grid_objects_dims[obj] = Vec2(obj.dims)
        self._grid_objects_spanning[obj] = (span_x, span_y)
        
        obj.anchor = anchor
        self.mark_dirty()
        return self
    
    def remove_object(self, obj: PygameObject):
        self.remove_child(obj)
        self._grid_objects_grid_positions.pop(obj, None)
        
        self.mark_dirty()
    
    def stack_y(self, obj: PygameObject, x: Optional[int] = None, span_x: Optional[int] = None, anchor: Vec2 = Anchor.C):
        
        min_x = (min(pos[0] for pos in self._grid_objects_grid_positions.values()) + 1) if self._grid_objects_grid_positions else 0
        max_x = (max(pos[0] for pos in self._grid_objects_grid_positions.values()) + 1) if self._grid_objects_grid_positions else 0
        
        positions = list(pos for pos in self._grid_objects_grid_positions.values() if pos[0] == x or x is None)
        max_y = (max(pos[1] for pos in positions) + 1) if positions else 0
        
        x = min_x - 1 if x is None else x
        span_x = (max_x - min_x + 1) if span_x is None else span_x
        
        self.add_object(obj, x, max_y, span_x, 1, anchor)
        return self
    
    def stack_x(self, obj: PygameObject, y: Optional[int] = None, span_y: Optional[int] = None, anchor: Vec2 = Anchor.C):
        
        positions = list(pos for pos in self._grid_objects_grid_positions.values() if pos[1] == y or y is None)
        max_x = (max(pos[0] for pos in positions) + 1) if positions else 0
        
        min_y = (min(pos[1] for pos in self._grid_objects_grid_positions.values()) + 1) if self._grid_objects_grid_positions else 0
        max_y = (max(pos[1] for pos in self._grid_objects_grid_positions.values()) + 1) if self._grid_objects_grid_positions else 0
        
        y = min_y - 1 if y is None else y
        span_y = (max_y - min_y + 1) if span_y is None else span_y
        
        self.add_object(obj, max_x, y, 1, span_y, anchor)
        return self
    
    
    def check_if_dirty(self):
        for obj, grid_pos in self._grid_objects_grid_positions.items():
            grid_x, grid_y = grid_pos
            span_x, span_y = self._grid_objects_spanning.get(obj, (1, 1))
            if self._grid_objects_dims.get(obj, Vec2()).x != obj.dims.x:
                for col_x in range(grid_x, grid_x + span_x):
                    if not self._fixed_cols.get(col_x, False):
                        self.mark_dirty()
            
            if self._grid_objects_dims.get(obj, Vec2()).y != obj.dims.y:
                for row_y in range(grid_y, grid_y + span_y):
                    if not self._fixed_rows.get(row_y, False):
                        self.mark_dirty()
            
            self._grid_objects_dims[obj] = Vec2(obj.dims)
        
        return self._dirty
    
    def mark_dirty(self):
        self._dirty = True
    
    
    def _reset_dims(self):
        for col_x in dict(self._col_widths):
            if not self._fixed_cols.get(col_x, False):
                self._col_widths.pop(col_x)
            
            if self._min_row_heights.get(col_x, False):
                self._col_widths[col_x] = self._min_row_heights[col_x]
        
        for row_y in dict(self._row_heights):
            if not self._fixed_rows.get(row_y, False):
                self._row_heights.pop(row_y)
            
            if self._min_row_heights.get(row_y, False):
                self._row_heights[row_y] = self._min_row_heights[row_y]
    
    def _compute_offsets(self):
        offset = 0
        for col_x in sorted(dict(self._col_widths)):
            self._col_offsets[col_x] = offset
            offset += self._col_widths[col_x]
        
        offset = 0
        for row_y in sorted(dict(self._row_heights)):
            self._row_offsets[row_y] = offset
            offset += self._row_heights[row_y]
    
    
    def update_grid_size(self):
        self._reset_dims()
        
        for obj, spanning in sorted(self._grid_objects_spanning.items(), key=lambda x: x[1][0] * x[1][1]):
            grid_x, grid_y = grid_pos = self._grid_objects_grid_positions.get(obj, (0, 0))
            pad_x, pad_y = self._cells_padding.get(grid_pos, self._padding)
            width, height = self._grid_objects_dims.get(obj, Vec2(0, 0))
            span_x, span_y = spanning
            
            free_columns = [col_x for col_x in range(grid_x, grid_x + span_x) if not self._fixed_cols.get(col_x, False)]
            for col_x in range(grid_x, grid_x + span_x):
                self._col_widths.setdefault(col_x, 0)
            target = width + 2 * pad_x
            missing = target - sum(self._col_widths.get(col_x, 0) for col_x in range(grid_x, grid_x + span_x))
            if free_columns and missing > 0:
                for col_x in free_columns:
                    self._col_widths[col_x] = self._col_widths.get(col_x, 0) + missing / len(free_columns)
            
            free_rows = [row_y for row_y in range(grid_y, grid_y + span_y) if not self._fixed_rows.get(row_y, False)]
            for row_y in range(grid_y, grid_y + span_y):
                self._row_heights.setdefault(row_y, 0)
            target = height + 2 * pad_y
            missing = target - sum(self._row_heights.get(row_y, 0) for row_y in range(grid_y, grid_y + span_y))
            if free_rows and missing > 0:
                for row_y in free_rows:
                    self._row_heights[row_y] = self._row_heights.get(row_y, 0) + missing / len(free_rows)
        
        if self._fixed_width:
            self.width = self._fixed_width
            free_columns = [col_x for col_x in self._col_widths if not self._fixed_cols.get(col_x, False)]
            target = self._fixed_width - self._outer_padding.x*2
            missing = target - sum(self._col_widths.values())
            if free_columns and missing > 0:
                for col_x in free_columns:
                    self._col_widths[col_x] = self._col_widths.get(col_x, 0) + missing / len(free_columns)
        else:
            self.width = sum(self._col_widths.values()) + self._outer_padding.x * 2
        
        if self._fixed_height:
            self.height = self._fixed_height
            free_rows = [row_y for row_y in self._row_heights if not self._fixed_rows.get(row_y, False)]
            target = self._fixed_height - self._outer_padding.y*2
            missing = target - sum(self._row_heights.values())
            if free_rows and missing > 0:
                for row_y in free_rows:
                    self._row_heights[row_y] = self._row_heights.get(row_y, 0) + missing / len(free_rows)
        else:
            self.height = sum(self._row_heights.values()) + self._outer_padding.y * 2
        
        self._compute_offsets()
                    
                    
    def update_grid_object_positions(self):
        for obj in self._grid_objects_grid_positions:
            obj.pos = self.get_obj_pos(obj)
    
    def update_grid(self):
        self.update_grid_size()
        self.update_grid_object_positions()
        self._dirty = False
    
    
    def _update_self(self, dt: float):
        self.behaviors.on_update(dt)
        
        if self.dirty_check and self.check_if_dirty():
            self.update_grid()
        
        if self.renderer:
            self.renderer.update(dt)
    
    def __repr__(self):
        return f"LayoutObject({id(self)})"


class DebugOverlay(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    def toggle(self) -> "LayoutObject":
        self.visible = not self.visible
        return self
    
    def __repr__(self):
        return f"DebugOverlay({id(self)})"


class DebugPanelObject(LayoutObject):
    def __init__(
            self,
            transform: Transform,
            renderer: RectRenderer,
            services: DictCollection,
            panel: LayoutObject,
            title_panel: RectObject,
            header: RectObject,
            title_text: TextObject,
            layer: int = 0,
            anchor: Vec2 = Anchor.C
    ):
        super().__init__(transform, renderer, services, layer, anchor)
        
        self._panel = panel
        self._title_panel = title_panel
        self._header = header
        self._title_text = title_text
    
    # region PROPERTIES
    
    @property
    def panel(self):
        return self._panel
    
    @property
    def title_panel(self):
        return self._title_panel
    
    @property
    def header(self):
        return self._header
    
    @property
    def title_text(self):
        return self._title_text
    
    # endregion
    
    def unfix_width(self):
        super().unfix_width()
        self.panel.unfix_width()
        
    def unfix_height(self):
        super().unfix_height()
        self.panel.unfix_height()
        
    def fix_height(self, height: Optional[int | float] = None):
        if height:
            super().fix_height(height)
            self.panel.fix_height(round(height - self.title_panel.height - self.header.height))
    
    def fix_width(self, width: Optional[int | float] = None):
        super().fix_width(width)
        self.panel.fix_width(width)
        self.title_panel.width = width
        self.header.width = width
    
    
    def stack_pannel_x(self, obj: PygameObject, y: Optional[int] = None, span_y: Optional[int] = None, anchor: Vec2 = Anchor.C):
        self.panel.stack_x(obj, y, span_y, anchor)
        return self
    
    def stack_pannel_y(self, obj: PygameObject, x: Optional[int] = None, span_x: Optional[int] = None, anchor: Vec2 = Anchor.C):
        self.panel.stack_y(obj, x, span_x, anchor)
        return self
    
    def add_pannel_object(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: Vec2 = Anchor.C):
        self.panel.add_object(obj, x, y, span_x, span_y, anchor)
        return self
    
    def __repr__(self):
        return f"DebugPannel({id(self)})"
    

    