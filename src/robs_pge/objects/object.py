from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING, Union, cast
import inspect

from .behavior_collection import BehaviorCollection
from .behaviors import ActionOnClickBehavior, ActionOnHoverBehavior, ActionOnScrollBehavior, ActionOnUpdateBehavior, AttributeClampingBehavior, AttributeFixingBehavior, AttributeGridSnappingBehavior, \
    AttributeValueSnappingBehavior, DraggableBehavior, DynamicAttributeBehavior, ObjectBehavior
from .object_collection import ObjectCollection
from ..animation import Animation, AnimationManager
from ..debug import QuickDebugManager
from ..events import Event, EventManager
from ..rendering import CircleRenderer, ObjectRenderer, DrawCommand
from ..utils import Anchor, CircleCollisionBox, CollisionBox, DictCollection, ObjectFlags, Rect, RectCollisionBox, Transform, Vec2, test_collision_box_overlap, FRect

if TYPE_CHECKING:
    from ..core import Camera
    from ..objects import PygameObject
    from .layer import Layer
    
    ObjectCallBackType = Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...] | Callable | tuple[Callable, ...]]


class PygameObject:
    DEFAULT_FLAGS = ObjectFlags.CULLABLE
    
    def __init__(self, transform: Transform, renderer: ObjectRenderer, services: DictCollection, sub_layer: int=0, anchor: Vec2=Anchor.C):
        self._transform = transform
        self._anchor = anchor
        
        self._layer: Optional[Layer] = None
        self._sub_layer = sub_layer
        
        self._flags = PygameObject.DEFAULT_FLAGS
        self._behaviors = BehaviorCollection(self)
        self._services = services
        
        self._properties: DictCollection = DictCollection()
        
        self._renderer = renderer
        self._collision_box = None
        
        self._children = ObjectCollection()
        
        self._parent: Optional[PygameObject] = None
        self._parent_anchor = Anchor.C
        
        self._culled = False
        
        self._clip_area: Optional[FRect] = None
        self._clip_area_relative: bool = False
        
        self._children_clip_area: Optional[FRect] = None
        self._children_clip_area_relative = True

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
    def world_transform(self) -> Transform:
        parent = self.parent
        return (parent.world_transform * (self.transform + Transform(parent.get_anchor_offset(self._parent_anchor - parent.anchor)))) if parent is not None else self.transform
    
    @property
    def camera_transform(self) -> Transform:
        cam_pos = self.world_to_camera(self.world_transform.pos)
        return Transform(cam_pos, self.world_transform.rotation, self.world_transform.scale)
    
    # region properties
    
    @property
    def properties(self) -> DictCollection[str, Any]:
        return self._properties
    
    def get_property[T](self, name: str, default: Optional[T] = None, ignore_missing=True) -> T:
        if not ignore_missing and not self.properties.has(name): raise AttributeError(f"Unknown property '{name}', only has {self.properties.keys()}")
        return self.properties.get(name, default)
    
    def set_property(self, name: str, value: Any):
        self.properties[name] = value
        return self
    
    def modify_property[T](self, name: str, modifier: Callable[[T], T], default: Optional[T] = None):
        self.set_property(name, modifier(self.get_property(name, default)))
        return self
    
    # endregion
    
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
    
    # region layer
    @property
    def layer(self) -> Optional[Layer]:
        return self._layer if self._layer is not None else self._parent.layer if self._parent is not None else None
    
    @layer.setter
    def layer(self, value: Layer):
        self._layer = value
    # endregion
    
    # endregion
    
    # region sub layer
    @property
    def sub_layer(self):
        return self._sub_layer
    
    @sub_layer.setter
    def sub_layer(self, value: int):
        self._sub_layer = value
    # endregion
    
    # region clip_area
    
    @property
    def clip_area(self):
        return self._clip_area
    
    @clip_area.setter
    def clip_area(self, value: Optional[FRect]):
        self._clip_area = value
    
    @property
    def clip_area_relative(self):
        return self._clip_area_relative
    
    def set_clip_area(self, rect: Optional[FRect], relative: bool = False):
        self._clip_area = rect
        self._clip_area_relative = relative
        return self
    
    def clear_clip_area(self):
        self._clip_area = None
        return self
    
    def get_world_clip_area(self) -> Optional[FRect]:
        if self._clip_area is None:
            parent = self.parent
            if parent is not None:
                return parent.get_world_children_clip_area()
            return None
        
        rect = self._clip_area
        
        parent = self.parent
        if parent is not None:
            parent_worl_clip_area = parent.get_world_children_clip_area()
            
            if self._clip_area_relative:
                parent_transform = parent.world_transform
                rect = parent_transform.apply_on_rect(rect)
                
            if parent_worl_clip_area is not None:
                rect = rect.clip(parent_worl_clip_area)
                
        return rect
    
    # endregion
    
    # region clip_area
    
    @property
    def children_clip_area(self):
        return self._children_clip_area
    
    @children_clip_area.setter
    def children_clip_area(self, value: Optional[FRect]):
        self._children_clip_area = value
    
    @property
    def children_clip_area_relative(self):
        return self._children_clip_area_relative
    
    def set_children_clip_area(self, rect: Optional[FRect], relative: bool = False):
        self._children_clip_area = rect
        self._children_clip_area_relative = relative
        return self
    
    def clear_children_clip_area(self):
        self._children_clip_area = None
        return self
    
    def get_world_children_clip_area(self) -> Optional[FRect]:
        
        rect = None
        
        if self._children_clip_area is not None:
            if self._children_clip_area_relative:
                rect = self.world_transform.apply_on_rect(self._children_clip_area)
            else:
                rect = self._children_clip_area
        
        parent = self.parent
        if parent is not None:
            parent_rect = parent.get_world_children_clip_area()
            if parent_rect is not None:
                rect = rect.clip(parent_rect) if rect is not None else parent_rect
        
        return rect
    
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
            
        return self
        
    def remove_child(self, obj: "PygameObject"):
        self._children.remove(obj)
        obj.set_parent(None)
        
        return self
        
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
        return flag == flag & self.flags
    
    @property
    def behaviors(self):
        return self._behaviors
    
    def add_behavior(self, behavior: ObjectBehavior | list[ObjectBehavior] | BehaviorCollection):
        self.behaviors.add_behavior(behavior)
        
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
        return self
        
    def add_quick_debug(self, getter: Callable[[], Any] | Callable[[PygameObject], Any], template: str = "{}"):
        arg_count = len(inspect.signature(getter).parameters)
        if arg_count == 0:
            self.get_service(QuickDebugManager).add_listener(getter, template)
        if arg_count == 1:
            self.get_service(QuickDebugManager).add_listener(lambda: getter(self), template)
        else:
            raise AttributeError("Can't accept method with more than 1 parameter")
        return self
        
    def do_on_update(self, action: ObjectCallBackType):
        self.add_behavior(ActionOnUpdateBehavior(action))
        return self
        
    def do_on_click(self, button: int, on_click: Optional[ObjectCallBackType] = None, on_hold: Optional[ObjectCallBackType] = None, on_release: Optional[ObjectCallBackType] = None):
        if on_click or on_hold or on_release:
            self.add_behavior(ActionOnClickBehavior(button, on_click, on_hold, on_release))
        return self
            
    def do_on_hover(self, hover_start: ObjectCallBackType = None, while_hovered: ObjectCallBackType = None, hover_end: ObjectCallBackType = None):
        if hover_start or while_hovered or hover_end:
            self.add_behavior(ActionOnHoverBehavior(hover_start, while_hovered, hover_end))
        return self
    
    def do_on_scroll(self, action: Optional[Callable[[PygameObject, int, Vec2], Any] | tuple[Callable[[PygameObject, int, Vec2], Any], ...]]):
        if action is not None:
            self.add_behavior(ActionOnScrollBehavior(action))
        return self
            
    def make_attribute_dynamic(self, attribute: str, getter: Any | Callable[[], Any | tuple[Any, ...]], template: Optional[str] = None, strength: float = 1):
        self.add_behavior(DynamicAttributeBehavior(attribute, getter, template, strength))
        return self
        
    def make_attribute_fixed(self, attribute: str, value: Optional[Any | Callable[[], Any]] = None, strength: float = 1):
        self.add_behavior(AttributeFixingBehavior(attribute, value, strength))
        return self
        
    def make_attribute_clamped(self, attribute: str, min_value: Optional[float | Callable[[],  float]] = None, max_value: Optional[float | Callable[[],  float]] = None, strength: float = 1):
        self.add_behavior(AttributeClampingBehavior(attribute, min_value, max_value, strength))
        return self
        
    def make_attribute_snap(self, attribute: str, values: list[float], offset: float = 0, strength: float = 1):
        self.add_behavior(AttributeValueSnappingBehavior(attribute, values, offset, strength))
        return self
        
    def make_attribute_snap_on_grid(self, attribute: str, step: float, offset: float = 0, strength: float = 1):
        self.add_behavior(AttributeGridSnappingBehavior(attribute, step, offset, strength))
        return self
    
    def make_draggable(self, button: int = 1, target: Optional["PygameObject"] = None):
        self.add_behavior(DraggableBehavior(button, target))
        return self
    
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
        
    def on_scroll(self, scroll: int, pos: Vec2):
        self.behaviors.on_scroll(scroll, pos)
    
    # endregion
    
    # region HIT TEST METHODS
    
    def test_screen_hit(self, screen: Vec2, camera: Optional[Camera] = None) -> bool:
        cam_pos = self.screen_to_camera(screen, camera)
        return self.test_camera_hit(cam_pos)
    
    def test_camera_hit(self, camera_pos: Vec2) -> bool:
        # 1. Check clip area in World Space
        clip = self.get_world_clip_area()
        if clip is not None:
            world_pos = self.camera_to_world(camera_pos)
            if not clip.collidepoint(world_pos.x, world_pos.y):
                return False
        
        # 2. Check texture hit directly from Camera Space -> Local Space
        return self.test_local_hit(self.camera_to_local(camera_pos))
    
    def test_world_hit(self, world: Vec2) -> bool:
        return self.test_camera_hit(self.world_to_camera(world))
    
    def test_local_hit(self, local: Vec2) -> bool:
        return self.renderer.test_hit(local) if self.renderer else False
    
    def test_uv_hit(self, uv: Vec2) -> bool:
        return self.test_local_hit(self.uv_to_local(uv))
    
    def test_aabb_object_hit(self, other: "PygameObject") -> bool:
        return self.get_world_aabb().colliderect(other.get_world_aabb())
    
    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # --- Screen Conversions ---
    def screen_to_camera(self, screen: Vec2, camera: Optional[Camera] = None) -> Vec2:
        if camera:
            return camera.screen_to_camera_pos(screen)
        if self.layer:
            return self.layer.screen_to_camera_pos(screen)
        return screen
    
    def screen_to_world(self, screen: Vec2, camera: Optional[Camera] = None) -> Vec2:
        return self.camera_to_world(self.screen_to_camera(screen, camera))
    
    def screen_to_local(self, screen: Vec2, camera: Optional[Camera] = None) -> Vec2:
        return self.camera_to_local(self.screen_to_camera(screen, camera))
    
    def screen_to_uv(self, screen: Vec2, camera: Optional[Camera] = None) -> Vec2:
        return self.local_to_uv(self.screen_to_local(screen, camera))
    
    # --- Camera Conversions ---
    def camera_to_screen(self, camera_pos: Vec2, camera: Optional[Camera] = None) -> Vec2:
        if camera:
            return camera.camera_to_screen_pos(camera_pos)
        if self.layer:
            return self.layer.camera_to_screen_pos(camera_pos)
        return camera_pos
    
    def camera_to_world(self, camera_pos: Vec2) -> Vec2:
        return self.layer.camera_to_world_pos(camera_pos) if self.layer else camera_pos
    
    def camera_to_local(self, camera_pos: Vec2) -> Vec2:
        # Bypassing the World skew! We use the camera_transform.
        return self.camera_transform.apply_inverse(camera_pos) + self.uv_to_local(self.anchor)
    
    def camera_to_uv(self, camera_pos: Vec2) -> Vec2:
        return self.local_to_uv(self.camera_to_local(camera_pos))
    
    # --- World Conversions ---
    def world_to_screen(self, world: Vec2, camera: Optional[Camera] = None) -> Vec2:
        return self.camera_to_screen(self.world_to_camera(world), camera)
    
    def world_to_camera(self, world: Vec2) -> Vec2:
        return self.layer.world_to_camera_pos(world) if self.layer else world
    
    def world_to_local(self, world: Vec2) -> Vec2:
        return self.camera_to_local(self.world_to_camera(world))
    
    def world_to_parent_local(self, world: Vec2) -> Vec2:
        parent = self.parent
        return parent.world_to_local(world) if parent else world
    
    def world_to_uv(self, world: Vec2) -> Vec2:
        return self.local_to_uv(self.world_to_local(world))
    
    # --- Local Conversions ---
    def local_to_screen(self, local: Vec2, camera: Optional[Camera] = None) -> Vec2:
        return self.camera_to_screen(self.local_to_camera(local), camera)
    
    def local_to_camera(self, local: Vec2) -> Vec2:
        return self.camera_transform.apply(local - self.uv_to_local(self.anchor))
    
    def local_to_world(self, local_pos: Vec2) -> Vec2:
        return self.camera_to_world(self.local_to_camera(local_pos))
    
    def local_to_uv(self, local) -> Vec2:
        return self.renderer.local_to_uv(local) if self.renderer else Vec2()
    
    # --- UV Conversions ---
    def uv_to_screen(self, uv: Vec2, camera: Optional[Camera] = None) -> Vec2:
        return self.local_to_screen(self.uv_to_local(uv), camera)
    
    def uv_to_camera(self, uv: Vec2) -> Vec2:
        return self.local_to_camera(self.uv_to_local(uv))
    
    def uv_to_world(self, uv: Vec2) -> Vec2:
        return self.local_to_world(self.uv_to_local(uv))
    
    def uv_to_local(self, uv: Vec2) -> Vec2:
        return self.renderer.uv_to_local(uv) if self.renderer else Vec2()
    
    def get_anchor_offset(self, anchor: Vec2):
        return self.uv_to_local(anchor)
    
    # endregion
    
    # region OTHER
    
    def trigger_event(self, event: Event) -> PygameObject:
        self.get_service(EventManager).trigger(event)
        return self
    
    def play_animation(self, animation: Animation) -> PygameObject:
        self.get_service(AnimationManager).play(animation)
        return self
    
    def quick_debug(self, *infos: Any) -> PygameObject:
        self.get_service(QuickDebugManager).quick_debug(infos)
        return self
    
    # endregion
    
    def _render_self(self, submit: Callable[[DrawCommand], Any]):
        self.renderer.render(submit, self.world_transform, self.layer, self.sub_layer, self.anchor, self.get_world_clip_area())
        return self
    
    def render(self, submit) -> PygameObject:
        self._culled = False
        if self.visible:
            if self.renderer and not self.has_flag(ObjectFlags.SKIP_RENDERING):
                self._render_self(submit)
            self.children.render(submit)
        return self
            
            
    def _update_self(self, dt) -> PygameObject:
        self.behaviors.on_update(dt)
        return self
        
    def update(self, dt: float=0.0) -> PygameObject:
        if not self.frozen:
            self.children.update(dt)
            if not self.has_flag(ObjectFlags.SKIP_UPDATE):
                self._update_self(dt)
            
        if self.renderer:
            self.renderer.update(dt)
            
        return self
            
    
    def __repr__(self):
        return f"PygameObject({id(self)})"
