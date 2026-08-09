from __future__ import annotations

from typing import Literal, TypeVar, cast

from .behavior_collection import BehaviorCollection
from .behaviors import *
from .object_collection import ObjectCollection
from ..animation import Animation, AnimationManager
from ..debug import QuickDebugManager
from ..events import Event, EventManager
from ..physics import PhysicsBody, ShapeTypes
from ..rendering import DrawCommand, ObjectRenderer
from ..utils import Anchor, Callback, DictCollection, FRect, ObjectFlags, ObjectTags, Transform, vec2

if TYPE_CHECKING:
    from .layer import Layer


R = TypeVar('R', bound=ObjectRenderer)


class PygameObject[R]:
    DEFAULT_FLAGS = ObjectFlags.CULLABLE
    DEFAULT_TAGS = ObjectTags.NONE
    
    def __init__(self, transform: Transform, renderer: R, services: DictCollection, sub_layer: int=0, anchor: vec2=Anchor.C):
        self._transform = transform
        self._anchor = anchor
        
        self._layer: Optional[Layer] = None
        self._sub_layer = sub_layer
        
        self._flags = self.DEFAULT_FLAGS
        self._tags = self.DEFAULT_TAGS
        
        self._behaviors = BehaviorCollection(self)
        self._services = services
        
        self._properties: DictCollection = DictCollection()
        
        self._renderer = renderer
        
        self._children = ObjectCollection()
        
        self._parent: Optional[PygameObject] = None
        self._parent_anchor = Anchor.C
        
        self._culled = False
        
        self._clip_area: Optional[FRect] = None
        self._clip_area_relative: bool = False
        
        self._children_clip_area: Optional[FRect] = None
        self._children_clip_area_relative = True
        
        self._cached_world_transform: Optional[Transform] = None
        self._world_transform_dirty = True
        self._cached_visible = True
        self._visible_dirty = True

        self._physics_body: Optional[PhysicsBody] = None

    # region PROPERTIES
    
    @property
    def dims(self) -> vec2:
        return vec2() if self.renderer is None else self.renderer.dims
    
    @property
    def width(self) -> float:
        return 0 if self.renderer is None else self.renderer.width
    
    @property
    def height(self) -> float:
        return 0 if self.renderer is None else self.renderer.height
    
    @property
    def culled(self) -> bool:
        return self._culled
    
    @property
    def renderer(self) -> R:
        return self._renderer
    
    @property
    def transform(self) -> Transform:
        return self._transform
    
    def _invalidate_world_transform(self):
        self._world_transform_dirty = True
        for child in self._children:
            # noinspection protected-member
            child._invalidate_world_transform()

    def _invalidate_visible(self):
        self._visible_dirty = True
        for child in self._children:
            # noinspection protected-member
            child._invalidate_visible()
    
    @property
    def world_transform(self) -> Transform:
        # noinspection protected-member
        if self._transform._dirty:
            self._invalidate_world_transform()
            self._transform._dirty = False

        if not self._world_transform_dirty:
            return cast(Transform, self._cached_world_transform)
        
        parent = self.parent
        if parent is None:
            result = self.transform.with_position(self.layer.local_to_world_pos(self.pos)) # type: ignore
        else:
            result = parent.world_transform * (self.transform + Transform(parent.get_anchor_offset(self._parent_anchor - parent.anchor)))
        
        self._cached_world_transform = result
        self._world_transform_dirty = False
        return result
    
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
    def pos(self, value: vec2):
        self.transform.pos = value
        self._invalidate_world_transform()
    
    @property
    def x_pos(self):
        return self.transform.x_pos
    
    @x_pos.setter
    def x_pos(self, value: float):
        self.transform.x_pos = value
        self._invalidate_world_transform()
    
    @property
    def y_pos(self):
        return self.transform.y_pos
    
    @y_pos.setter
    def y_pos(self, value: float):
        self.transform.y_pos = value
        self._invalidate_world_transform()
        
    def move(self, vec: vec2):
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
        self._invalidate_world_transform()
        
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
        self._invalidate_world_transform()
        
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
    
    def set_parent(self, obj: Optional["PygameObject"], anchor: vec2 = Anchor.C):
        if self._parent not in [None, obj]:
            self._parent.remove_child(self)
        
        self._parent = obj
        self._parent_anchor = anchor
        self._invalidate_world_transform()
        self._invalidate_visible()
        
        return self
    # endregion
    
    # region children
    @property
    def children(self):
        return self._children
    
    def add_child(self, obj: "PygameObject", anchor: vec2 = Anchor.C):
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
        if not self._visible_dirty:
            return self._cached_visible
        
        parent = self.parent
        self._cached_visible = not self.has_flag(ObjectFlags.HIDDEN) and (parent is None or parent.visible)
        self._visible_dirty = False
        return self._cached_visible
    
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
    def flags(self) -> ObjectFlags:
        return self._flags
    
    def add_flag(self, flag: ObjectFlags):
        self._flags |= flag
        if flag & ObjectFlags.HIDDEN:
            self._invalidate_visible()
        return self
        
    def remove_flag(self, flag: ObjectFlags):
        self._flags &= ~flag
        if flag & ObjectFlags.HIDDEN:
            self._invalidate_visible()
        return self
    
    def has_flag(self, flag: ObjectFlags):
        return (int(self._flags) & int(flag)) == int(flag)
    
    
    @property
    def tags(self) -> ObjectTags:
        return self._tags
    
    def add_tag(self, tag: ObjectTags):
        self._tags |= tag
        if tag & ObjectFlags.HIDDEN:
            self._invalidate_visible()
        return self
        
    def remove_tag(self, tag: ObjectTags):
        self._tags &= ~tag
        if tag & ObjectFlags.HIDDEN:
            self._invalidate_visible()
        return self
    
    def has_tag(self, tag: ObjectTags):
        return (int(self._tags) & int(tag)) == int(tag)
    
    
    @property
    def behaviors(self):
        return self._behaviors
    
    def add_behavior(self, behavior: ObjectBehavior | list[ObjectBehavior] | BehaviorCollection):
        self.behaviors.add_behavior(behavior)
        return self
        
    def remove_behavior(self, behavior: ObjectBehavior | list[ObjectBehavior] | BehaviorCollection):
        self.behaviors.remove(behavior)
        return self
    
    # endregion
    
    def set_world_position(self, world_pos):
        parent = self.parent
        if parent is None:
            layer = self.layer
            if layer:
                local_pos = layer.world_to_local_pos(world_pos)
                self.transform.pos = local_pos
        else:
            local_pos = parent.world_transform.apply_inverse_on_point(world_pos)
            anchor_offset = parent.get_anchor_offset(self._parent_anchor - parent.anchor)
            self.transform.pos = local_pos - anchor_offset
    
    def set_world_rotation(self, world_rotation: float):
        parent = self.parent
        if parent is None:
            self.transform.rotation = world_rotation
        else:
            self.transform.rotation = world_rotation - parent.world_transform.rotation
    
    def get_service[T](self, cls: type[T]) -> T:
        return self._services.get(cls)
    
    # region REGISTRATION METHODS
    
    def register_event_callback(self, event_type: str, callback: Callback[[Event], Any]):
        self.get_service(EventManager).register(event_type, callback)
        return self

    def add_quick_debug(self, getter: Callable[[PygameObject], Any], template: str = "{}"):
        self.get_service(QuickDebugManager).add_listener(lambda: getter(self), template)
        return self

    def do_on_update(self, action: Callback[[PygameObject], Any]):
        self.add_behavior(ActionOnUpdateBehavior(action))
        return self

    def do_on_click(self, button: int, on_click: Callback[[PygameObject], Any] = None, on_hold: Callback[[PygameObject], Any] = None, on_release: Callback[[PygameObject], Any] = None):
        if on_click or on_hold or on_release:
            self.add_behavior(ActionOnClickBehavior(button, on_click, on_hold, on_release))
        return self

    def do_on_hover(self, hover_start: Callback[[PygameObject], Any] = None, while_hovered: Callback[[PygameObject], Any] = None, hover_end: Callback[[PygameObject], Any] = None):
        if hover_start or while_hovered or hover_end:
            self.add_behavior(ActionOnHoverBehavior(hover_start, while_hovered, hover_end))
        return self

    def do_on_scroll(self, action: Callback[[PygameObject, int, vec2], Any]):
        if action is not None:
            self.add_behavior(ActionOnScrollBehavior(action))
        return self

    def do_on_collision(self, on_collision: Callback[[PygameObject, PygameObject], Any] = None, while_colliding: Callback[[PygameObject, PygameObject], Any] = None, on_collision_end: Callback[[PygameObject, PygameObject], Any] = None, condition_on_other: Optional[Callable[[PygameObject], bool]] = None):
        if on_collision or while_colliding or on_collision_end:
            self.add_behavior(ActionOnCollisionBehavior(on_collision, while_colliding, on_collision_end, condition_on_other))
    
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

    # region PHYSICS

    @property
    def physics_body(self) -> Optional[PhysicsBody]:
        return self._physics_body

    @property
    def has_physics(self) -> bool:
        return self._physics_body is not None

    def add_physics_body(self, shape_type: Literal["box", "circle"] = ShapeTypes.BOX, sensor: bool = False, **kwargs) -> PhysicsBody:
        body = PhysicsBody(self, sensor=sensor, **kwargs)

        if shape_type == ShapeTypes.BOX:
            body.add_box_shape(kwargs.get("size", None))
        elif shape_type == ShapeTypes.CIRCLE:
            body.add_circle_shape(kwargs.get("radius", None))

        self._physics_body = body
        self.add_flag(ObjectFlags.COLLIDABLE if sensor else ObjectFlags.PHYSICS)
        self._register_body_with_layer()
        return body

    def remove_physics_body(self):
        if self._physics_body is not None:
            self._unregister_body_from_layer()
            self._physics_body.remove()
            self._physics_body = None
            self.remove_flag(ObjectFlags.COLLIDABLE | ObjectFlags.PHYSICS)

    def _register_body_with_layer(self):
        if self._physics_body and self._layer and self._layer.physics_world:
            self._layer.physics_world.add_body(self._physics_body)

    def _unregister_body_from_layer(self):
        if self._physics_body and self._layer and self._layer.physics_world:
            self._layer.physics_world.remove_body(self._physics_body)

    # endregion
    
    # region BEHAVIOR METHODS
    
    def while_hovered(self):
        self.behaviors.on_hover()
    
    def on_hover_end(self):
        self.behaviors.on_hover_end()
    
    def on_hover_start(self):
        self.behaviors.on_hover_start()
    
    def on_click(self, button: int, pos: vec2):
        self.behaviors.on_click(button, pos)
    
    def on_hold(self, button: int, pos: vec2):
        self.behaviors.on_hold(button, pos)
    
    def on_release(self, button: int, pos: vec2):
        self.behaviors.on_release(button, pos)
        
    def on_scroll(self, scroll: int, pos: vec2):
        self.behaviors.on_scroll(scroll, pos)
        
    def on_collision(self, obj: PygameObject):
        self.behaviors.on_collision(obj)
    
    def on_collision_end(self, obj: PygameObject):
        self.behaviors.on_collision_end(obj)
    
    # endregion
    
    # region HIT TEST METHODS
    
    def test_screen_hit(self, screen: vec2) -> bool:
        cam_pos = self.screen_to_camera(screen)
        return self.test_camera_hit(cam_pos)
    
    def test_camera_hit(self, camera_pos: vec2) -> bool:
        clip = self.get_world_clip_area()
        if clip is not None:
            world_pos = self.camera_to_world(camera_pos)
            if not clip.collidepoint(world_pos.x, world_pos.y):
                return False
        return self.test_pixel_hit(self.camera_to_pixel(camera_pos))
    
    def test_world_hit(self, world: vec2) -> bool:
        return self.test_camera_hit(self.world_to_camera(world))
    
    def test_local_hit(self, local: vec2) -> bool:
        return self.test_pixel_hit(self.local_to_pixel(local))
    
    def test_pixel_hit(self, pixel: vec2) -> bool:
        return self.renderer.test_hit(pixel) if self.renderer else False
    
    def test_uv_hit(self, uv: vec2) -> bool:
        return self.test_pixel_hit(self.uv_to_pixel(uv))
    
    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # region From Screen
    def screen_to_viewport(self, pos: vec2) -> vec2: return self.layer.screen_to_viewport_pos(pos) # type: ignore
    def screen_to_camera(self, pos: vec2) -> vec2: return self.layer.screen_to_camera_pos(pos) # type: ignore
    def screen_to_world(self, pos: vec2) -> vec2: return self.layer.screen_to_world_pos(pos) # type: ignore
    def screen_to_layer(self, pos: vec2) -> vec2: return self.world_to_layer(self.screen_to_world(pos))
    def screen_to_local(self, pos: vec2) -> vec2: return self.world_to_local(self.screen_to_world(pos))
    def screen_to_pixel(self, pos: vec2) -> vec2: return self.local_to_pixel(self.screen_to_local(pos))
    def screen_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.screen_to_pixel(pos), children_anchor)
    def screen_to_uv(self, pos: vec2) -> vec2: return self.pixel_to_uv(self.screen_to_pixel(pos))
    # endregion
    
    # region From Viewport
    def viewport_to_screen(self, pos: vec2) -> vec2: return self.layer.viewport_to_screen_pos(pos) # type: ignore
    def viewport_to_camera(self, pos: vec2) -> vec2: return self.layer.viewport_to_camera_pos(pos) # type: ignore
    def viewport_to_world(self, pos: vec2) -> vec2: return self.layer.viewport_to_world_pos(pos) # type: ignore
    def viewport_to_layer(self, pos: vec2) -> vec2: return self.world_to_layer(self.viewport_to_world(pos))
    def viewport_to_local(self, pos: vec2) -> vec2: return self.world_to_local(self.viewport_to_world(pos))
    def viewport_to_pixel(self, pos: vec2) -> vec2: return self.local_to_pixel(self.viewport_to_local(pos))
    def viewport_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.viewport_to_pixel(pos), children_anchor)
    def viewport_to_uv(self, pos: vec2) -> vec2: return self.pixel_to_uv(self.viewport_to_pixel(pos))
    # endregion
    
    # region From Camera
    def camera_to_screen(self, pos: vec2) -> vec2: return self.layer.camera_to_screen_pos(pos) # type: ignore
    def camera_to_viewport(self, pos: vec2) -> vec2: return self.layer.camera_to_viewport_pos(pos) # type: ignore
    def camera_to_world(self, pos: vec2) -> vec2: return self.layer.camera_to_world_pos(pos) # type: ignore
    def camera_to_layer(self, pos: vec2) -> vec2: return self.world_to_layer(self.camera_to_world(pos))
    def camera_to_local(self, pos: vec2) -> vec2: return self.world_to_local(self.camera_to_world(pos))
    def camera_to_pixel(self, pos: vec2) -> vec2: return self.local_to_pixel(self.camera_to_local(pos))
    def camera_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.camera_to_pixel(pos), children_anchor)
    def camera_to_uv(self, pos: vec2) -> vec2: return self.pixel_to_uv(self.camera_to_pixel(pos))
    # endregion
    
    # region From World
    def world_to_screen(self, pos: vec2) -> vec2: return self.layer.world_to_screen_pos(pos) # type: ignore
    def world_to_viewport(self, pos: vec2) -> vec2: return self.layer.world_to_viewport_pos(pos) # type: ignore
    def world_to_camera(self, pos: vec2) -> vec2: return self.layer.world_to_camera_pos(pos) # type: ignore
    def world_to_layer(self, pos: vec2) -> vec2: return self.layer.world_to_local_pos(pos) # type: ignore
    def world_to_local(self, pos: vec2) -> vec2: return self.world_transform.apply_inverse_on_point(pos)
    def world_to_pixel(self, pos: vec2) -> vec2: return self.local_to_pixel(self.world_to_local(pos))
    def world_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.world_to_pixel(pos), children_anchor)
    def world_to_uv(self, pos: vec2) -> vec2: return self.pixel_to_uv(self.world_to_pixel(pos))
    # endregion
    
    # region From Layer
    def layer_to_screen(self, pos: vec2) -> vec2: return self.world_to_screen(self.layer_to_world(pos))
    def layer_to_viewport(self, pos: vec2) -> vec2: return self.world_to_viewport(self.layer_to_world(pos))
    def layer_to_camera(self, pos: vec2) -> vec2: return self.world_to_camera(self.layer_to_world(pos))
    def layer_to_world(self, pos: vec2) -> vec2: return self.layer.local_to_world_pos(pos) # type: ignore
    def layer_to_local(self, pos: vec2) -> vec2: return self.world_to_local(self.layer_to_world(pos))
    def layer_to_pixel(self, pos: vec2) -> vec2: return self.local_to_pixel(self.layer_to_local(pos))
    def layer_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.layer_to_pixel(pos), children_anchor)
    def layer_to_uv(self, pos: vec2) -> vec2: return self.pixel_to_uv(self.layer_to_pixel(pos))
    # endregion
    
    # region From Local
    def local_to_screen(self, pos: vec2) -> vec2: return self.world_to_screen(self.local_to_world(pos))
    def local_to_viewport(self, pos: vec2) -> vec2: return self.world_to_viewport(self.local_to_world(pos))
    def local_to_camera(self, pos: vec2) -> vec2: return self.world_to_camera(self.local_to_world(pos))
    def local_to_world(self, pos: vec2) -> vec2: return self.world_transform.apply_on_point(pos)
    def local_to_layer(self, pos: vec2) -> vec2: return self.world_to_layer(self.local_to_world(pos))
    def local_to_pixel(self, pos: vec2) -> vec2: return pos + self.get_anchor_offset(self.anchor)
    def local_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.local_to_pixel(pos), children_anchor)
    def local_to_uv(self, pos: vec2) -> vec2: return self.pixel_to_uv(self.local_to_pixel(pos))
    # endregion
    
    # region From Pixel
    def pixel_to_screen(self, pos: vec2) -> vec2: return self.local_to_screen(self.pixel_to_local(pos))
    def pixel_to_viewport(self, pos: vec2) -> vec2: return self.local_to_viewport(self.pixel_to_local(pos))
    def pixel_to_camera(self, pos: vec2) -> vec2: return self.local_to_camera(self.pixel_to_local(pos))
    def pixel_to_world(self, pos: vec2) -> vec2: return self.local_to_world(self.pixel_to_local(pos))
    def pixel_to_layer(self, pos: vec2) -> vec2: return self.local_to_layer(self.pixel_to_local(pos))
    def pixel_to_local(self, pos: vec2) -> vec2: return pos - self.get_anchor_offset(self.anchor)
    def pixel_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return pos - self.get_anchor_offset(children_anchor)
    def pixel_to_uv(self, pos: vec2) -> vec2: return self.renderer.local_to_uv(pos) if self.renderer else vec2()
    # endregion
    
    # region From Children Local
    def children_local_to_screen(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_screen(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_viewport(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_viewport(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_camera(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_camera(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_world(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_world(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_layer(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_layer(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_local(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_pixel(self, pos: vec2, children_anchor: vec2) -> vec2: return pos + self.get_anchor_offset(children_anchor)
    def children_local_to_uv(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_uv(self.children_local_to_pixel(pos, children_anchor))
    # endregion
    
    # region From UV
    def uv_to_screen(self, pos: vec2) -> vec2: return self.pixel_to_screen(self.uv_to_pixel(pos))
    def uv_to_viewport(self, pos: vec2) -> vec2: return self.pixel_to_viewport(self.uv_to_pixel(pos))
    def uv_to_camera(self, pos: vec2) -> vec2: return self.pixel_to_camera(self.uv_to_pixel(pos))
    def uv_to_world(self, pos: vec2) -> vec2: return self.pixel_to_world(self.uv_to_pixel(pos))
    def uv_to_layer(self, pos: vec2) -> vec2: return self.pixel_to_layer(self.uv_to_pixel(pos))
    def uv_to_local(self, pos: vec2) -> vec2: return self.pixel_to_local(self.uv_to_pixel(pos))
    def uv_to_pixel(self, pos: vec2) -> vec2: return self.renderer.uv_to_local(pos) if self.renderer else vec2()
    def uv_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2: return self.pixel_to_children_local(self.uv_to_pixel(pos), children_anchor)
    # endregion
    
    # region Coordinates Helpers
    def get_anchor_offset(self, anchor: vec2) -> vec2: return self.uv_to_pixel(anchor)
    def world_to_parent_local(self, pos: vec2) -> vec2: return self.parent.world_to_local(pos) if self.parent else pos # type: ignore
    def world_to_parent_children_local(self, pos: vec2) -> vec2: return self.parent.world_to_children_local(pos, self._parent_anchor) if self.parent else pos # type: ignore
    def parent_children_local_to_world(self, pos: vec2) -> vec2: return self.parent.children_local_to_world(pos, self._parent_anchor) if self.parent else pos # type: ignore
    # endregion
    
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
        self.renderer.render(submit, self.world_transform, self.layer, self.sub_layer, self.anchor, self.get_world_clip_area()) # type: ignore
        return self
    
    def _is_culled(self) -> bool:
        layer = self.layer
        if layer is None:
            return False
        camera = layer.camera
        cam_pos = camera.pos
        obj_pos = self.world_transform.pos
        dx = obj_pos.x - cam_pos.x
        dy = obj_pos.y - cam_pos.y
        dist_sq = dx * dx + dy * dy
        if dist_sq <= camera.bounding_radius_squared:
            return False
        obj_radius = self.renderer.get_bounding_radius() * self.world_transform.scale if self.renderer else 0
        radius_sum = camera.bounding_radius + obj_radius
        return dist_sq > radius_sum * radius_sum
    
    def render(self, submit) -> "PygameObject":
        if self._flags == ObjectFlags.CULLABLE:
            if not self.visible:
                return self
            if self._is_culled():
                self._culled = True
                return self
            self._culled = False
            if self.renderer:
                self._render_self(submit)
            self.children.render(submit)
            return self
        
        if not self.visible:
            return self
        
        if self.has_flag(ObjectFlags.CULLABLE) and self._is_culled():
            self._culled = True
            return self
        
        self._culled = False
        if self.renderer and not self.has_flag(ObjectFlags.SKIP_RENDERING):
            self._render_self(submit)
        self.children.render(submit)
        return self
            
            
    def _update_self(self, dt) -> PygameObject:
        self.behaviors.on_update(dt)
        return self
        
    def update(self, dt: float=0.0) -> PygameObject:
        if self._flags == ObjectFlags.CULLABLE:
            self.children.update(dt)
            self._update_self(dt)
            if self.renderer:
                self.renderer.update(dt)
            return self
        
        if not self.frozen:
            self.children.update(dt)
            if not self.has_flag(ObjectFlags.SKIP_UPDATE):
                self._update_self(dt)
            
        if self.renderer:
            self.renderer.update(dt)
            
        return self
            
    
    def __repr__(self):
        return f"PygameObject({id(self)})"
