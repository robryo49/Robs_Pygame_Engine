from typing import cast

from .behavior_collection import BehaviorCollection
from .behaviors import *
from .object_collection import ObjectCollection
from ..core.camera import Camera
from ..rendering import CircleShape, ObjectRenderer, RectShape, SpriteRenderer, TextRenderer
from ..utils import Anchor, Color, DictCollection, Easing, ObjectFlags, Rect, Transform, Vec2, clamp, inf


class PygameObject:
    DEFAULT_FLAGS = ObjectFlags.CULLABLE | ObjectFlags.VISIBLE
    
    def __init__(self, transform: Transform, renderer: Optional[ObjectRenderer], services: DictCollection, layer: int=0, anchor: Vec2=Anchor.C):
        self._transform = transform
        self._layer = layer
        self._anchor = anchor
        
        self._flags = PygameObject.DEFAULT_FLAGS
        self._behaviors = BehaviorCollection(self)
        self._services = services
        
        self._renderer = renderer
        
        self._children = ObjectCollection()
        
        self._parent: Optional[PygameObject] = None
        self._parent_anchor = Anchor.C
        
        self._culled = False

    # region PROPERTIES
    
    @property
    def dims(self):
        return self.renderer.dims if self.renderer else Vec2()
    
    @property
    def width(self):
        return self.renderer.width if self.renderer else 0
    
    @property
    def height(self):
        return self.renderer.height if self.renderer else 0
    
    @property
    def aabb_dims(self):
        return Vec2(self.renderer.get_aabb_size(self.rotation) * self.scale) if self.renderer else Vec2()
    
    @property
    def culled(self):
        return self._culled
    
    @property
    def renderer(self):
        return self._renderer
    
    @property
    def transform(self):
        return self._transform
    
    @property
    def world_transform(self):
        return (self.parent.world_transform * (self.transform + Transform(self.parent.get_anchor_offset(self._parent_anchor - Vec2(0.5))))) if self.parent else self.transform
    
    # region pos
    @property
    def pos(self):
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: Vec2):
        self.transform.pos = value
        
    def move(self, vec: Vec2):
        self.pos += vec
        
    def move_x(self, dx):
        self.pos.x += dx
        
    def move_y(self, dy):
        self.pos.y += dy
    # endregion
    
    # region rotation
    @property
    def rotation(self):
        return self.transform.rotation
    
    @rotation.setter
    def rotation(self, value: int):
        self.transform.rotation = value
        
    def rotate(self, value: float):
        self.rotation += value
    # endregion
    
    # region scale
    @property
    def scale(self):
        return self.transform.scale
    
    @scale.setter
    def scale(self, value):
        self.transform.scale = value
        
    def scale_by(self, value: float):
        self.scale *= value
    # endregion
    
    # region anchor
    @property
    def anchor(self):
        return self._anchor
    
    @anchor.setter
    def anchor(self, value):
        self._anchor = value
    # endregion
    
    # region layer
    @property
    def layer(self):
        return self._layer
    
    @layer.setter
    def layer(self, value: int):
        self._layer = value
    # endregion
    
    # region parent
    @property
    def parent(self):
        return self._parent
    
    def set_parent(self, obj: Optional["PygameObject"], anchor: Vec2 = Anchor.C):
        if self._parent not in [None, obj]:
            self._parent.remove_child(self)
        
        self._parent = obj
        self._parent_anchor = anchor
        
        if self._parent is not None and not self._parent.children.has(self):
            self._parent.add_child(self)
        return self
    # endregion
    
    # region children
    @property
    def children(self):
        return self._children
    
    def add_child(self, obj: "PygameObject", anchor: Vec2 = Anchor.C):
        self._children.add(obj)
        
        if obj.parent is not self:
            obj.set_parent(self, anchor)
        
    def remove_child(self, obj: "PygameObject"):
        self._children.remove(obj)
        obj.set_parent(None)
    # endregion
    
    @property
    def visible(self):
        return self.has_flag(ObjectFlags.VISIBLE) and (self.parent is None or self.parent.visible)
    
    @visible.setter
    def visible(self, value: bool):
        self.show() if value else self.hide()
    
    def show(self):
        self.add_flag(ObjectFlags.VISIBLE)
    
    def hide(self):
        self.remove_flag(ObjectFlags.VISIBLE)
    
    def toggle_visible(self):
        self.visible = not self.visible
        
    def skip_rendering(self):
        self.add_flag(ObjectFlags.SKIP_RENDERING)
        
    def enable_rendering(self):
        self.remove_flag(ObjectFlags.SKIP_RENDERING)
        
    
    @property
    def flags(self):
        return self._flags
    
    def add_flag(self, flag):
        self._flags |= flag
        return self
        
    def remove_flag(self, flag):
        self._flags &= ~flag
        return self
    
    def has_flag(self, flag):
        return bool(flag & self.flags)
    
    
    @property
    def behaviors(self):
        return self._behaviors
    
    def add_behavior(self, behavior: ObjectBehavior | list[ObjectBehavior] | BehaviorCollection):
        self.behaviors.add(behavior)
        
    def remove_behavior(self, behavior: ObjectBehavior | list[ObjectBehavior] | BehaviorCollection):
        self.behaviors.remove(behavior)
    
    # endregion
        
    def get_service(self, cls: type):
        return self._services.get(cls)
    
    
    # region METHODS
    
    # region behavior methods
    
    def while_hovered(self):
        self.behaviors.on_hover()
        
    def on_hover_end(self):
        self.behaviors.on_hover_end()
        
    def on_hover_start(self):
        self.behaviors.on_hover_start()
        
    def on_click(self, button: int, pos: Vec2):
        self.behaviors.on_click(button, pos)
        
    def on_hold(self, button: int, pos: Vec2):
        self.behaviors.on_hold(button, pos)
        
    def on_release(self, button: int, pos: Vec2):
        self.behaviors.on_release(button, pos)
        
    # endregion
    
    # region coordinates conversion methods
    
    def screen_to_local(self, screen: Vec2, camera: Optional[Camera] = None):
        return self.world_to_local(camera.screen_to_world_pos(screen)) if camera else self.world_to_local(screen)
    
    def screen_to_uv(self, screen: Vec2, camera: Optional[Camera] = None):
        return self.world_to_uv(camera.screen_to_world_pos(screen)) if camera else self.world_to_uv(screen)
        
    
    def world_to_local(self, world: Vec2):
        return self.world_transform.apply_inverse(world) + self.uv_to_local(self.anchor)
    
    def world_to_uv(self, world: Vec2):
        return self.local_to_uv(self.world_to_local(world))
    
    
    def local_to_world(self, local_pos: Vec2):
        return self.world_transform.apply(local_pos - self.uv_to_local(self.anchor))
    
    def local_to_uv(self, local):
        return self.renderer.local_to_uv(local) if self.renderer else Vec2()
    
    def local_to_screen(self, local: Vec2, camera: Optional[Camera] = None):
        return camera.world_to_screen_pos(self.local_to_world(local)) if camera else self.local_to_world(local)
    
    
    def uv_to_local(self, uv: Vec2):
        return self.renderer.uv_to_local(uv) if self.renderer else Vec2()
    
    def uv_to_world(self, uv: Vec2):
        return self.local_to_world(self.uv_to_local(uv))
    
    def uv_to_screen(self, uv: Vec2, camera: Optional[Camera] = None):
        return camera.world_to_screen_pos(self.uv_to_world(uv)) if camera else self.uv_to_world(uv)
    
    
    def get_anchor_offset(self, anchor: Vec2):
        return self.uv_to_local(anchor)
    
    # endregion
    
    # region hit test methods
    
    def test_screen_hit(self, screen: Vec2, camera: Optional[Camera] = None):
        return self.test_world_hit(camera.screen_to_world_pos(screen) if camera else screen)
    
    def test_world_hit(self, world: Vec2):
        return self.test_local_hit(self.world_to_local(world))
    
    def test_local_hit(self, local: Vec2):
        return self.renderer.test_hit(local) if self.renderer else False
    
    def test_uv_hit(self, uv: Vec2):
        return self.test_local_hit(self.uv_to_local(uv))
    
    # endregion
    
    def get_world_aabb(self):
        w, h = self.aabb_dims
        x, y = self.uv_to_world(Anchor.C)
        return Rect(x - w*0.5, y - h*0.5, w, h)
    
    # endregion
    
    def render(self, submit, camera: Optional[Camera] = None):
        self._culled = False
        
        if self.visible and self.renderer and not self.has_flag(ObjectFlags.SKIP_RENDERING):
            
            if self.has_flag(ObjectFlags.CULLABLE) and camera:
                camera_rect = camera.world_aabb
                object_rect = self.get_world_aabb()
                
                if not object_rect.colliderect(camera_rect):
                    self._culled = True
            
            if not self._culled:
                self.renderer.render(submit, self.world_transform, self.layer, self.anchor)
        
        self.children.render(submit, camera)
        
    def update(self, dt: float):
        self.behaviors.on_update(dt)
        self.children.update(dt)
        
        if self.renderer:
            self.renderer.update(dt)
    
    def __repr__(self):
        return f"PygameObject({id(self)})"
    
    
    
class RectObject(PygameObject):
    def __init__(self, transform: Transform, renderer: RectShape, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(RectShape, self._renderer)
    
    
    @property
    def dims(self):
        return self.renderer.dims
    
    @dims.setter
    def dims(self, value: Vec2):
        self.renderer.dims = value
    
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
        
    
    @property
    def height(self):
        return self.renderer.height
    
    @height.setter
    def height(self, value: int):
        self.renderer.height = value
        
        
    @property
    def bg_color(self):
        return self.renderer.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        self.renderer.bg_color = value
        
    
    @property
    def border(self):
        return self.renderer.border
    
    @border.setter
    def border(self, value: int):
        self.renderer.border = value
    
    
    @property
    def bd_color(self):
        return self.renderer.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        self.renderer.bd_color = value
    
    
    @property
    def bd_radius(self):
        return self.renderer.bd_radius
    
    @bd_radius.setter
    def bd_radius(self, value: int):
        self.renderer.bd_radius = value
    
    # endregion
    

class CircleObject(PygameObject):
    def __init__(self, transform: Transform, renderer: CircleShape, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(CircleShape, self._renderer)
    
    
    @property
    def dims(self):
        return self.renderer.dims
    
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
        
    
    @property
    def height(self):
        return self.renderer.height
    
    @height.setter
    def height(self, value):
        self.renderer.height = value
        
    
    @property
    def diameter(self):
        return self.renderer.diameter
    
    @diameter.setter
    def diameter(self, value: int):
        self.renderer.diameter = value
        
    
    @property
    def radius(self):
        return self.renderer.radius
    
    @radius.setter
    def radius(self, value: int):
        self.renderer.radius = value
    
    
    @property
    def bg_color(self):
        return self.renderer.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        self.renderer.bg_color = value
    
    
    @property
    def bd_color(self):
        return self.renderer.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        self.renderer.bd_color = value
    
    
    @property
    def border(self):
        return self.renderer.border
    
    @border.setter
    def border(self, value: int):
        self.renderer.border = value
    
    # endregion
    

class TextObject(PygameObject):
    def __init__(self, transform: Transform, renderer: TextRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)

    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(TextRenderer, self._renderer)
    
    @property
    def text(self):
        return self.renderer.text
    
    @text.setter
    def text(self, value: str):
        self.renderer.text = value
    
    # endregion
    
    
class SpriteObject(PygameObject):
    def __init__(self, transform: Transform, renderer: SpriteRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(SpriteRenderer, self._renderer)
    
    @property
    def dims(self):
        return self.renderer.dims
    
    @property
    def width(self):
        return self.renderer.width
    
    @property
    def height(self):
        return self.renderer.height
    
    # endregion



class LayoutObject(RectObject):
    def __init__(self, transform: Transform, renderer: RectShape, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        self._grid_objects_grid_positions: dict[PygameObject, tuple[int, int]] = {}
        self._grid_objects_spanning: dict[PygameObject, tuple[int, int]] = {}
        self._grid_objects_dimensions : dict[PygameObject, Vec2] = {}
        self._grid_objects_positions : dict[PygameObject, Vec2] = {}
        
        self._fixed_cols: dict[int, bool] = {}
        self._col_widths: dict[int, float] = {}
        self._col_offsets: dict[int, float] = {}
        
        self._fixed_rows: dict[int, bool] = {}
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
        
        self.add_flag(ObjectFlags.SKIP_RENDERING)
        
    
    # region PROPERITIES
    
    # region min_col
    @property
    def min_col(self):
        return self._min_col
    
    @min_col.setter
    def min_col(self, value):
        self._min_col = value
        
        for obj in self._grid_objects_grid_positions:
            self._grid_objects_grid_positions[obj] = (max(value, self._grid_objects_grid_positions[obj][0]), self._grid_objects_grid_positions[obj][1])
    # endregion
    
    # region max_col
    @property
    def max_col(self):
        return self._max_col
    
    @max_col.setter
    def max_col(self, value):
        self._max_col = value
        
        for obj in self._grid_objects_grid_positions:
            self._grid_objects_grid_positions[obj] = (min(value, self._grid_objects_grid_positions[obj][0]), self._grid_objects_grid_positions[obj][1])
    # endregion
    
    # region min_row
    @property
    def min_row(self):
        return self._min_row
    
    @min_row.setter
    def min_row(self, value):
        self._min_row = value
        
        for obj in self._grid_objects_grid_positions:
            self._grid_objects_grid_positions[obj] = (self._grid_objects_grid_positions[obj][0], max(value, self._grid_objects_grid_positions[obj][1]))
    # endregion
    
    # region max_row
    @property
    def max_row(self):
        return self._max_row
    
    @max_row.setter
    def max_row(self, value):
        self._max_row = value
        
        for obj in self._grid_objects_grid_positions:
            self._grid_objects_grid_positions[obj] = (self._grid_objects_grid_positions[obj][0], min(value, self._grid_objects_grid_positions[obj][1]))
    # endregion
    
    # region invert_x_order
    @property
    def invert_x_order(self):
        return self._invert_x_order
    
    @invert_x_order.setter
    def invert_x_order(self, value):
        self._invert_x_order = value
    # endregion
    
    # region invert_y_order
    @property
    def invert_y_order(self):
        return self._invert_y_order
    
    @invert_y_order.setter
    def invert_y_order(self, value):
        self._invert_y_order = value
    # endregion
    
    # endregion
    
    
    def fix_col_width(self, col_x: int, width: int = None):
        if width is not None:
            self._col_widths[col_x] = width
        self._fixed_cols[col_x] = True
        
        self.mark_dirty()
    
    def fix_row_height(self, row_y: int, height: int = None):
        if height is not None:
            self._row_heights[row_y] = height
        self._fixed_rows[row_y] = True
        
        self.mark_dirty()
        
    def unfix_col_width(self, col_x: int):
        self._fixed_cols[col_x] = False
        
        self.mark_dirty()
        
    def unfix_row_height(self, row_y: int):
        self._fixed_rows[row_y] = False
        
        self.mark_dirty()
        
        
    def fix_width(self, width: int = None):
        self._fixed_width = width or self.width
        
        self.mark_dirty()
        
    def fix_height(self, height: int = None):
        self._fixed_height = height or self.height
        
        self.mark_dirty()
        
    def unfix_width(self):
        self._fixed_width = None
        
        self.mark_dirty()
        
    def unfix_height(self):
        self._fixed_height = None
        
        self.mark_dirty()
    
    
    def invert_left_right(self):
        self._invert_x_order = True
        
    def invert_up_down(self):
        self._invert_y_order = True
    
    
    def set_constant_padding(self, padding: Vec2 | int):
        self.set_cell_padding(padding / 2)
        self.set_outer_padding(padding / 2)
    
    def set_cell_padding(self, padding: Vec2 | int, cell: Optional[tuple[int, int]] = None):
        if cell is not None:
            self._cells_padding[cell] = Vec2(padding)
        else:
            self._padding = Vec2(padding)
            
        self.mark_dirty()
            
    def clear_cell_padding(self, cell: Optional[tuple[int, int]] = None):
        if cell is not None:
            self._cells_padding.pop(cell, 0)
        else:
            self._padding = Vec2()
            
        self.mark_dirty()
        
    def set_outer_padding(self, padding: Vec2 | int):
        padding = Vec2(padding)
        self._outer_padding = padding
        self.renderer.border = min(padding.x, padding.y)
        self.mark_dirty()
        
    def clear_outer_padding(self):
        self._outer_padding = Vec2()
        self.renderer.border = 0
        self.mark_dirty()
        
    
    
    def get_col_width(self, grid_x: int, span: int = 0):
        return sum(self._col_widths.get(grid_x + offset, 0) for offset in range(span + 1))
    
    def get_row_height(self, grid_y: int, span: int = 0):
        return sum(self._row_heights.get(grid_y + offset, 0) for offset in range(span + 1))
    
    
    def get_obj_pos(self, obj: PygameObject):
        grid_x, grid_y = grid_pos = self._grid_objects_grid_positions.get(obj, (0, 0))
        span_x, span_y = self._grid_objects_spanning.get(obj, (0, 0))
        padding = self._cells_padding.get(grid_pos, self._padding)
        
        dir_x = -1 if self._invert_x_order else 1
        dir_y = -1 if self._invert_y_order else 1
        
        cell_x = (
            dir_x * (self._col_offsets[grid_x] + sum(self.get_col_width(col_x) for col_x in range(grid_x, grid_x + span_x)) * obj.anchor.x) +
            padding.x * (1 - 2 * obj.anchor.x) + (self.width - self._outer_padding.x * 2) * (1 - dir_x) / 2
        )
        
        cell_y = (
            dir_y * (self._row_offsets[grid_y] + sum(self.get_row_height(row_y) for row_y in range(grid_y, grid_y + span_y)) * obj.anchor.y) +
            padding.y * (1 - 2 * obj.anchor.y) + (self.height - self._outer_padding.y * 2) * (1 - dir_y) / 2
        )
        
        return Vec2(cell_x, cell_y) + self._outer_padding - self.get_anchor_offset(self.anchor)
        
        
    def add_object(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: Vec2 = Anchor.C):
        self.add_child(obj)
        self._grid_objects_grid_positions[obj] = (clamp(x, self._min_col, self._max_col), clamp(y, self._min_row, self._max_row))
        self._grid_objects_dimensions[obj] = Vec2(obj.dims)
        self._grid_objects_spanning[obj] = (span_x, span_y)
        
        obj.anchor = anchor
        self.mark_dirty()
        
    def remove_object(self, obj: PygameObject):
        self.remove_child(obj)
        self._grid_objects_grid_positions.pop(obj, None)
        
        self.mark_dirty()
    
    
    def check_if_dirty(self):
        for obj, grid_pos in self._grid_objects_grid_positions.items():
            grid_x, grid_y = grid_pos
            span_x, span_y = self._grid_objects_spanning.get(obj, (1, 1))
            if self._grid_objects_dimensions.get(obj, Vec2()).x != obj.dims.x:
                for col_x in range(grid_x, grid_x + span_x):
                    if not self._fixed_cols.get(col_x, False):
                        self.mark_dirty()
                        
            if self._grid_objects_dimensions.get(obj, Vec2()).y != obj.dims.y:
                for row_y in range(grid_y, grid_y + span_y):
                    if not self._fixed_rows.get(row_y, False):
                        self.mark_dirty()
        
            self._grid_objects_dimensions[obj] = Vec2(obj.dims)
                
        return self._dirty
        
    def mark_dirty(self):
        self._dirty = True
    
    
    def _reset_dims(self):
        for col_x in dict(self._col_widths):
            if not self._fixed_cols.get(col_x, False):
                self._col_widths.pop(col_x)
        
        for row_y in dict(self._row_heights):
            if not self._fixed_rows.get(row_y, False):
                self._row_heights.pop(row_y)
        
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
            width, height = self._grid_objects_dimensions.get(obj, Vec2(0, 0))
            span_x, span_y = spanning
            
            free_columns = [col_x for col_x in range(grid_x, grid_x + span_x) if not self._fixed_cols.get(col_x, False)]
            target = width + 2 * pad_x
            missing = target - sum(self._col_widths.get(col_x, 0) for col_x in range(grid_x, grid_x + span_x))
            if free_columns and missing > 0:
                for col_x in free_columns:
                    self._col_widths[col_x] = self._col_widths.get(col_x, 0) + missing / len(free_columns)
            
            free_rows = [row_y for row_y in range(grid_y, grid_y + span_y) if not self._fixed_rows.get(row_y, False)]
            target = height + 2 * pad_y
            missing = target - sum(self._row_heights.get(row_y, 0) for row_y in range(grid_y, grid_y + span_y))
            if free_rows and missing > 0:
                for row_y in free_rows:
                    self._row_heights[row_y] = self._row_heights.get(row_y, 0) + missing / len(free_rows)
        
        if self._fixed_width:
            free_columns = [col_x for col_x in self._col_widths if not self._fixed_cols.get(col_x, False)]
            target = self._fixed_width - self._outer_padding.x*2
            missing = target - sum(self._col_widths.values())
            if free_columns and missing > 0:
                for col_x in free_columns:
                    self._col_widths[col_x] = self._col_widths.get(col_x, 0) + missing / len(free_columns)
        else:
            self.width = sum(self._col_widths.values()) + self._outer_padding.x * 2
        
        if self._fixed_height:
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
    
    
    def update(self, dt: float):
        self.behaviors.on_update(dt)
        self.children.update(dt)
        
        if self.check_if_dirty():
            self.update_grid()
            
        if self.renderer:
            self.renderer.update(dt)


class DebugOverlay(LayoutObject):
    pass


class ButtonObject(RectObject):
    def __init__(self, transform: Transform, background: RectShape, text: TextObject, action: Callable, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        
        super().__init__(transform, background, services, layer, anchor)
        
        self._text = text
        
        self.add_child(self._text, Anchor.C)
        
        self.add_behavior([
            ScaleOnHoverBehavior(1.2, 0.1, Easing.EASE_OUT_QUAD),
            ScaleOnClickBehavior(1, 0.9, 0.1, Easing.EASE_OUT_QUAD),
            ActionOnClickBehavior(1, action)
        ])
        
    # region PROPERTIES
    
    @property
    def text(self):
        return self._text.text
    
    @text.setter
    def text(self, value):
        self._text.text = value
    
    # endregion
