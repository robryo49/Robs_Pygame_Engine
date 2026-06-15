from __future__ import annotations
from typing import TYPE_CHECKING
from typing import cast

from .behavior_collection import BehaviorCollection
from .behaviors import *
from .object_collection import ObjectCollection
from rendering import CircleRenderer, ObjectRenderer, RectRenderer, SpriteRenderer, TextRenderer
from rendering.object_renderer import LineRenderer
from utils import Anchor, Color, DictCollection, Easing, ObjectFlags, Rect, Transform, Vec2, clamp, inf, invert_y

if TYPE_CHECKING:
    from core import Camera


class PygameObject:
    DEFAULT_FLAGS = ObjectFlags.CULLABLE
    
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
        return Vec2(self.renderer.get_aabb_size(self.world_transform.rotation) * self.scale) if self.renderer else Vec2()
    
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
        return not self.has_flag(ObjectFlags.HIDDEN) and (self.parent is None or self.parent.visible)
    
    @visible.setter
    def visible(self, value: bool):
        self.show() if value else self.hide()
    
    def show(self):
        if self.has_flag(ObjectFlags.HIDDEN):
            self.remove_flag(ObjectFlags.HIDDEN)
        return self
    
    def hide(self):
        self.add_flag(ObjectFlags.HIDDEN)
        return self
    
    def toggle_visible(self):
        self.visible = not self.visible
        return self
        
        
    def skip_rendering(self):
        self.add_flag(ObjectFlags.SKIP_RENDERING)
        return self
        
    def enable_rendering(self):
        self.remove_flag(ObjectFlags.SKIP_RENDERING)
        return self
    
    
    @property
    def frozen(self):
        return self.has_flag(ObjectFlags.FROZEN) and (self.parent is None or self.parent.frozen)
    
    @frozen.setter
    def frozen(self, value: bool):
        self.freeze() if value else self.unfreeze()
    
    def unfreeze(self):
        if self.has_flag(ObjectFlags.FROZEN):
            self.remove_flag(ObjectFlags.FROZEN)
        return self
    
    def freeze(self):
        self.add_flag(ObjectFlags.FROZEN)
        return self
    
    def toggle_freeze(self):
        self.frozen = not self.frozen
        return self
    
    
    def skip_update(self):
        self.add_flag(ObjectFlags.SKIP_UPDATE)
        return self
    
    def enable_update(self):
        self.remove_flag(ObjectFlags.SKIP_UPDATE)
        return self
        
    
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
        
        return self
        
    def remove_behavior(self, behavior: ObjectBehavior | list[ObjectBehavior] | BehaviorCollection):
        self.behaviors.remove(behavior)
        
        return self
    
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
    
    
    def _render_self(self, submit, camera: Camera):
        self.renderer.render(submit, self.world_transform, self.layer, self.anchor)
    
    def render(self, submit, camera: Camera):
        self._culled = False
        if self.visible:
            if self.renderer and not self.has_flag(ObjectFlags.SKIP_RENDERING):
                
                if True or self.has_flag(ObjectFlags.CULLABLE):
                    camera_rect = camera.world_aabb
                    object_rect = self.get_world_aabb()
                
                    if not object_rect.colliderect(camera_rect):
                        self._culled = True
                
                if not self._culled:
                    self._render_self(submit, camera)
            self.children.render(submit, camera)
            
            
    def _update_self(self, dt):
        self.behaviors.on_update(dt)
        
    def update(self, dt: float):
        if not self.frozen:
            self.children.update(dt)
            if not self.has_flag(ObjectFlags.SKIP_UPDATE):
                self._update_self(dt)
            
        if self.renderer:
            self.renderer.update(dt)
            
    
    def __repr__(self):
        return f"PygameObject({id(self)})"
    
    
    
class RectObject(PygameObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(RectRenderer, self._renderer)
    
    
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
    def bd(self):
        return self.renderer.bd
    
    @bd.setter
    def bd(self, value: int):
        self.renderer.bd = value
    
    
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
    def __init__(self, transform: Transform, renderer: CircleRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(CircleRenderer, self._renderer)
    
    
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
    def bd(self):
        return self.renderer.bd
    
    @bd.setter
    def bd(self, value: int):
        self.renderer.bd = value
    
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


class LineObject(PygameObject):
    def __init__(self, transform: Transform, renderer: LineRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self):
        return cast(LineRenderer, self._renderer)
    
    
    @property
    def points(self):
        return self.renderer.points
    
    @points.setter
    def points(self, value: list[Vec2]):
        self.renderer.points = value
    
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
    
    
    @property
    def color(self):
        return self.renderer.color
    
    @color.setter
    def color(self, value: Color):
        self.renderer.color = value
    
    # endregion



class LayoutObject(RectObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
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
        
        for obj, pos in self._grid_objects_grid_positions:
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
        
        for obj, pos in self._grid_objects_grid_positions:
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
        
        for obj, pos in self._grid_objects_grid_positions:
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
        
        for obj, pos in self._grid_objects_grid_positions:
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
            
        
        return Vec2(cell_x, cell_y) + self._outer_padding - self.get_anchor_offset(self.anchor)
    
    
    
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
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, layer: int = 0, anchor: Vec2=Anchor.C):
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
    
    def stack_pannel_x(self, obj: PygameObject, y: Optional[int] = None, span_y: Optional[int] = None, anchor: Vec2 = Anchor.C):
        self.panel.stack_x(obj, y, span_y, anchor)
        return self
        
    def stack_pannel_y(self, obj: PygameObject, x: Optional[int] = None, span_x: Optional[int] = None, anchor: Vec2 = Anchor.C):
        self.panel.stack_y(obj, x, span_x, anchor)
        return self
    
    def add_pannel_object(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: Vec2 = Anchor.C):
        self.panel.add_object(obj, x, y, span_x, span_y, anchor)
        return self
    

class ButtonObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, action: Callable, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        
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



class ProgressBarObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, bar: RectObject, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._value = 0.0
        self._max_value = 1.0
        
        self._progress = 0.0
        
        self._dirty = True
        
        self._bar = bar
        self._bar.anchor = Anchor.TL
        self._bar.pos = invert_y(Vec2(self.bd))
        self.add_child(bar, Anchor.TL)
        
    # region PROPERTIES
    
    # region color
    @property
    def color(self):
        return self._bar.bg_color
    
    @color.setter
    def color(self, value):
        self._bar.bg_color = value
    # endregion
    
    # region value
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = clamp(value, 0, self.max_value)
        self._progress = self._value / self._max_value
        self.mark_dirty()
    # endregion
    
    # region max_value
    @property
    def max_value(self):
        return self._max_value
    
    @max_value.setter
    def max_value(self, value):
        self._max_value = value
        self._value = min(self._value, self._max_value)
        self._progress = self._value / value
        self.mark_dirty()
    # endregion
    
    # region progress
    @property
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = clamp(value)
        self._value = self._progress * self._max_value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def mark_dirty(self):
        self._dirty = True
        
    def _update_self(self, dt: float):
        super()._update_self(dt)
        
        if self._dirty:
            self._bar.width = round((self.width - self.bd*2) * self.progress)
            self._dirty = False
            
            
class GraphObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, line: LineObject, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._pad_x = 0
        self._pad_y = 0
        
        self._min_x = None
        self._max_x = None
        
        self._min_y = None
        self._max_y = None
        
        self._min_data_x = inf
        self._max_data_x = 0.0
        
        self._min_data_y = inf
        self._max_data_y = 0.0
        
        self._data_points = []
        self._max_data_points = None
        self._max_data_x_range = None
        
        self._dirty = True
        
        self._line = line
        self.add_child(line, Vec2(0.5, -0.5))
    
    # region PROPERTIES
    
    # region color
    @property
    def color(self):
        return self._line.color
    
    @color.setter
    def color(self, value):
        self._line.color = value
    # endregion
    
    # region min_x
    @property
    def min_x(self):
        return self._min_x
    
    @min_x.setter
    def min_x(self, value):
        self._min_x = value
    # endregion
    
    # region max_x
    @property
    def max_x(self):
        return self._max_x
    
    @max_x.setter
    def max_x(self, value):
        self._max_x = value
    # endregion
    
    # region min_y
    @property
    def min_y(self):
        return self._min_y
    
    @min_y.setter
    def min_y(self, value):
        self._min_y = value
    # endregion
    
    # region max_y
    @property
    def max_y(self):
        return self._max_y
    
    @max_y.setter
    def max_y(self, value):
        self._max_y = value
    # endregion
    
    # region pad_x
    @property
    def pad_x(self):
        return self._pad_x
    
    @pad_x.setter
    def pad_x(self, value):
        self._pad_x = value
    # endregion
    
    # region pad_y
    @property
    def pad_y(self):
        return self._pad_y
    
    @pad_y.setter
    def pad_y(self, value):
        self._pad_y = value
    # endregion
    
    # region max_data_points
    @property
    def max_data_points(self):
        return self._max_data_points
    
    @max_data_points.setter
    def max_data_points(self, value):
        self._max_data_points = value
    # endregion
    
    # region max_data_x_range
    @property
    def max_data_x_range(self):
        return self._max_data_x_range
    
    @max_data_x_range.setter
    def max_data_x_range(self, value):
        self._max_data_x_range = value
    # endregion
    
    # endregion
    
    def insert_point(self, point: Vec2):
        
        i = 0
        n = len(self._data_points)
        for i in range(n):
            p = self._data_points[n-i-1]
            if p.x < point.x:
                break
        
        self._data_points.insert(n-i, point)
        
        if self._max_data_points and len(self._data_points) > self._max_data_points:
            self.remove_last()
            
        self._min_data_x = min(self._min_data_x, point.x)
        self._max_data_x = max(self._max_data_x, point.x)
        
        self._min_data_y = min(self._min_data_y, point.y)
        self._max_data_y = max(self._max_data_y, point.y)
        
        if self._max_data_x_range and abs(self._max_data_x - self._min_data_x) > self._max_data_x_range:
            self.remove_last()
        
        self.mark_dirty()
        
    def _update_data_range_from_removed_point(self, point: Vec2):
        if point.x == self._min_data_x:
            self._min_data_x = min(p.x for p in self._data_points) if self._data_points else 0
        if point.x == self._max_data_x:
            self._max_data_x = max(p.x for p in self._data_points) if self._data_points else 0
            
        if point.y == self._min_data_y:
            self._min_data_y = min(p.y for p in self._data_points) if self._data_points else 0
        if point.y == self._max_data_y:
            self._max_data_y = max(p.y for p in self._data_points) if self._data_points else 0
        
    
    def remove_point(self, point: Vec2):
        self._data_points.remove(point)
        self._update_data_range_from_removed_point(point)
        self.mark_dirty()
    
    
    def remove_last(self):
        point = self._data_points.pop(0)
        self._update_data_range_from_removed_point(point)
        
        self.mark_dirty()
    
    def mark_dirty(self):
        self._dirty = True
    
    def _update_self(self, dt: float):
        super()._update_self(dt)
        
        if self._dirty:
            points = []
            
            if self._data_points:
                min_x = self._min_x if self._min_x is not None else self._min_data_x
                max_x = self._max_x if self._max_x is not None else self._max_data_x
                min_y = self._min_y if self._min_y is not None else self._min_data_y
                max_y = self._max_y if self._max_y is not None else self._max_data_y
                
                width = max_x - min_x
                height = max_y - min_y
                
                x_fac = (self.width - 2*self._pad_x)/width if width else 0
                y_fac = (self.height - 2*self._pad_y)/height if height else 0
                
                for point in self._data_points:
                    if min_x <= point.x <= max_x and min_y <= point.y <= max_y:
                        points.append(Vec2(self._pad_x + (point.x - min_x)*x_fac, self._pad_y + (point.y - min_y)*y_fac))
            
            self._line.points = points
            
            self._dirty = False

