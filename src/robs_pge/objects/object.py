from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING, Optional, Union, cast

from ..events import Event, EventManager
from ..rendering import CircleRenderer, ObjectRenderer

from ..utils import Anchor, DictCollection, Transform, Vec2, ObjectFlags, Rect, CollisionBox, RectCollisionBox, CircleCollisionBox, test_collision_box_overlap
from .behavior_collection import BehaviorCollection
from .behaviors import ObjectBehavior
from .object_collection import ObjectCollection

if TYPE_CHECKING:
    from ..core import Camera
    

class PygameObject:
    DEFAULT_FLAGS = ObjectFlags.CULLABLE
    
    def __init__(self, transform: Transform, renderer: ObjectRenderer, services: DictCollection, layer: int=0, anchor: Vec2=Anchor.C):
        self._transform = transform
        self._layer = layer
        self._anchor = anchor
        
        self._flags = PygameObject.DEFAULT_FLAGS
        self._behaviors = BehaviorCollection(self)
        self._services = services
        
        self._renderer = renderer
        self._collision_box = None
        
        self._children = ObjectCollection()
        
        self._parent: Optional[PygameObject] = None
        self._parent_anchor = Anchor.C
        
        self._culled = False

    # region PROPERTIES
    
    @property
    def dims(self):
        return Vec2() if self.renderer is None else self.renderer.dims
    
    @property
    def width(self):
        return 0 if self.renderer is None else self.renderer.width
    
    @property
    def height(self):
        return 0 if self.renderer is None else self.renderer.height
    
    @property
    def aabb_dims(self):
        return Vec2(self.renderer.get_aabb_size(self.world_transform.rotation) * self.scale) if self.renderer else Vec2()
    
    @property
    def culled(self):
        return self._culled
    
    @property
    def renderer(self) -> ObjectRenderer:
        return self._renderer
    
    @property
    def transform(self):
        return self._transform
    
    @property
    def world_transform(self):
        return (self.parent.world_transform * (self.transform + Transform(self.parent.get_anchor_offset(self._parent_anchor - Vec2(0.5))))) if self.parent is not None else self.transform
    
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
    
    def register_event_callback(self, event_type: str, callback: Callable[[Event], Any]):
        self.get_service(EventManager).register_listener(event_type, callback)
        
    def trigger_event(self, event: Event):
        self.get_service(EventManager).trigger_event(event)
    
    # region collision
    @property
    def collision_box(self) -> Optional[CollisionBox]:
            return self._collision_box

    def add_collision_box(
                    self,
                    kind: Optional[str] = None,
                    dims: Optional[Vec2] = None,
                    radius: Optional[float] = None,
                    rotation_offset: float = 0.0
            ) -> "PygameObject":
        if kind is None:
                kind = "circle" if isinstance(self.renderer, CircleRenderer) else "rect"

        if kind == "circle":
            if radius is None:
                radius = cast(CircleRenderer, self.renderer).radius if isinstance(self.renderer, CircleRenderer) else max(self.dims) / 2
            self._collision_box = CollisionBox("circle", radius=radius, rotation_offset=rotation_offset)
        else:
            half_extents = (dims / 2) if dims is not None else (self.dims / 2)
            self._collision_box = CollisionBox("rect", half_extents=half_extents, rotation_offset=rotation_offset)

        return self

    def remove_collision_box(self) -> "PygameObject":
        self._collision_box = None
        return self

    def get_world_collision_shape(self) -> Optional[Union[RectCollisionBox, CircleCollisionBox]]:
        if self._collision_box is None:
            return None
        wt = self.world_transform
        return self._collision_box.to_world_shape(wt.pos, wt.rotation, wt.scale)

    def test_object_collision(self, other: "PygameObject") -> bool:
        if self._collision_box is None or other.collision_box is None:
            return False
        return test_collision_box_overlap(self._collision_box, self.world_transform, cast(CollisionBox, other.collision_box), other.world_transform)
    # endregion
    
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
    
    def test_aabb_object_hit(self, other: "PygameObject") -> bool:
        return self.get_world_aabb().colliderect(other.get_world_aabb())
    
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
