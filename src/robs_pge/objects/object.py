from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING, Union, cast

from .behavior_collection import BehaviorCollection
from .behaviors import ActionOnClickBehavior, ActionOnHoverBehavior, ActionOnUpdateBehavior, AttributeClampingBehavior, AttributeFixingBehavior, AttributeGridSnappingBehavior, AttributeValueSnappingBehavior, DraggableBehavior, DynamicAttributeBehavior, ObjectBehavior
from .object_collection import ObjectCollection
from ..animation import Animation, AnimationManager
from ..debug import QuickDebugManager
from ..events import Event, EventManager
from ..rendering import CircleRenderer, ObjectRenderer
from ..utils import Anchor, CircleCollisionBox, CollisionBox, DictCollection, ObjectFlags, Rect, RectCollisionBox, Transform, Vec2, test_collision_box_overlap

if TYPE_CHECKING:
    from ..core import Camera
    from ..objects import PygameObject
    ObjectCallBackType = Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...] | Callable | tuple[Callable, ...]]
    

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
        
        self._fixed_x: Optional[float] = None
        self._fixed_y: Optional[float] = None

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
        return Vec2(self.renderer.get_aabb_size(self.world_transform.rotation)) * self.scale if self.renderer else Vec2()
    
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
        parent = self.parent
        return (parent.world_transform * (self.transform + Transform(parent.get_anchor_offset(self._parent_anchor - Vec2(0.5))))) if parent is not None else self.transform
    
    # region pos
    @property
    def pos(self):
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: Vec2):
        self.transform.pos = value
    
    @property
    def x_pos(self):
        return self.transform.pos.x
    
    @x_pos.setter
    def x_pos(self, value: float):
        self.transform.pos.x = value
    
    @property
    def y_pos(self):
        return self.transform.pos.y
    
    @y_pos.setter
    def y_pos(self, value: float):
        self.transform.pos.y = value
        
    def move(self, vec: Vec2):
        self.pos += vec
        
    def move_x(self, dx):
        self.x_pos += dx
        
    def move_y(self, dy):
        self.y_pos += dy
    
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
        parent = self.parent
        return not self.has_flag(ObjectFlags.HIDDEN) and (parent is None or parent.visible)
    
    @visible.setter
    def visible(self, value: bool):
        self.show() if value else self.hide()
        
    @property
    def hidden(self):
        return not self.visible
    
    @hidden.setter
    def hidden(self, value):
        self.visible = value
    
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
        parent = self.parent
        return self.has_flag(ObjectFlags.FROZEN) and (parent is None or parent.frozen)
    
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
    
    @property
    def collision_box(self) -> Optional[CollisionBox]:
        return self._collision_box
    
    def get_world_aabb(self):
        w, h = self.aabb_dims
        x, y = self.uv_to_world(Anchor.C)
        return Rect(x - w*0.5, y - h*0.5, w, h)
    
    # endregion
    
    def get_service[T](self, cls: type[T]) -> T:
        return self._services.get(cls)
    
    # region REGISTRATION METHODS
    
    def register_event_callback(self, event_type: str, callback: Callable[[Event], Any]):
        self.get_service(EventManager).register(event_type, callback)
        
    def add_quick_debug(self, getter: Callable, template: str = "{}"):
        self.get_service(QuickDebugManager).add_listener(getter, template)
        
    def do_on_update(self, action: ObjectCallBackType):
        self.add_behavior(ActionOnUpdateBehavior(action))
        
    def do_on_click(self, button: int, on_click: Optional[ObjectCallBackType] = None, on_hold: Optional[ObjectCallBackType] = None, on_release: Optional[ObjectCallBackType] = None):
        if on_click or on_hold or on_release:
            self.add_behavior(ActionOnClickBehavior(button, on_click, on_hold, on_release))
            
    def do_on_hover(self, hover_start: ObjectCallBackType = None, while_hovered: ObjectCallBackType = None, hover_end: ObjectCallBackType = None):
        if hover_start or while_hovered or hover_end:
            self.add_behavior(ActionOnHoverBehavior(hover_start, while_hovered, hover_end))
            
    def make_attribute_dynamic(self, attribute: str, getter: Callable[[], Any | tuple[Any, ...]], template: Optional[str] = None):
        self.add_behavior(DynamicAttributeBehavior(attribute, getter, template))
        
    def make_attribute_fixed(self, attribute: str):
        self.add_behavior(AttributeFixingBehavior(attribute))
        
    def make_attribute_clamped(self, attribute: str, min_value: Optional[float] = None, max_value: Optional[float] = None):
        self.add_behavior(AttributeClampingBehavior(attribute, min_value, max_value))
        
    def make_attribute_snap(self, attribute: str, values: list[float], offset: float = 0):
        self.add_behavior(AttributeValueSnappingBehavior(attribute, values, offset))
        
    def make_attribute_snap_on_grid(self, attribute: str, step: float, offset: float = 0):
        self.add_behavior(AttributeGridSnappingBehavior(attribute, step, offset))
        
    def make_draggable(self, button: int = 1):
        self.add_behavior(DraggableBehavior(button))
    
    # endregion
    
    # region COLLISION METHODS

    def add_collision_box(self, kind: Optional[str] = None, dims: Optional[Vec2] = None, radius: Optional[float] = None, rotation_offset: float = 0.0) -> "PygameObject":
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
    
    # region HIT TEST METHODS
    
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
    
    # region BEHAVIOR METHODS
    
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
    
    # region COORDINATES CONVERSION METHODS
    
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
    
    # region OTHER
    
    def trigger_event(self, event: Event):
        self.get_service(EventManager).trigger(event)
    
    def play_animation(self, animation: Animation):
        self.get_service(AnimationManager).play(animation)
    
    def quick_debug(self, *infos: Any) -> None:
        self.get_service(QuickDebugManager).quick_debug(infos)
    
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
