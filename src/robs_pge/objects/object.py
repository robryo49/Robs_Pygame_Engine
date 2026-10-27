"""Base scene object with transforms, rendering, behaviors, and physics."""

from __future__ import annotations

from typing import Any, Literal, Optional, TYPE_CHECKING, cast, Callable

from .object_flags import ObjectFlags
from .object_tags import ObjectTags
from .behaviors import *
from .object_collection import ObjectCollection
from ..sound import Sound
from ..animation import Animation
from ..events import Event
from ..physics import BodyTypes, PhysicsBody, ShapeTypes
from ..rendering import DrawCommand
from ..utils import Anchor, Callback, FRect, Transform, length, vec2

if TYPE_CHECKING:
    from ..objects import Layer
    from ..core import ServicesCollection


FOCUSED_LAYER = 10000
DRAGGABLE_BEHAVIOR_ID = "draggable_behavior"


class PygameObject[R]:
    """Base scene object with transforms, rendering, behaviors, and physics."""

    DEFAULT_FLAGS = ObjectFlags.CULLABLE
    DEFAULT_TAGS = ObjectTags.NONE

    def __init__(self, transform: Transform, renderer: R, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize an object with a transform, renderer, and services.

        :param transform: Local transform of the object.
        :param renderer: Renderer used to draw the object.
        :param services: Services collection available to the object.
        :param sub_layer: Sub-layer offset for render ordering.
        :param anchor: Anchor used to position the renderer relative to the transform.
        """
        self._transform = transform
        self._anchor = anchor
        
        self._layer: Optional[Layer] = None
        self._sub_layer = sub_layer
        self._focused = False
        
        self._flags = self.DEFAULT_FLAGS
        self._tags = self.DEFAULT_TAGS
        
        self._behaviors = self._create_behavior_manager()
        self._services: ServicesCollection = services
        
        self._properties: dict = {}
        
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

    def _create_behavior_manager(self) -> BehaviorManager:
        """
        Create the behavior manager for this object.

        :return: A behavior manager bound to this object.
        """
        return BehaviorManager(self)

    # region PROPERTIES
    
    @property
    def dims(self) -> vec2:
        """Return the renderer dimensions, or zero when no renderer is set."""
        return vec2() if self.renderer is None else self.renderer.dims
    
    @property
    def width(self) -> float:
        """Return the renderer width, or zero when no renderer is set."""
        return 0 if self.renderer is None else self.renderer.width
    
    @property
    def height(self) -> float:
        """Return the renderer height, or zero when no renderer is set."""
        return 0 if self.renderer is None else self.renderer.height
    
    @property
    def culled(self) -> bool:
        """Return whether the object was culled in the last render pass."""
        return self._culled
    
    @property
    def renderer(self) -> R:
        """Return the renderer used to draw this object."""
        return self._renderer
    
    @property
    def transform(self) -> Transform:
        """Return the local transform of this object."""
        return self._transform
    
    def _invalidate_world_transform(self) -> None:
        """Mark cached world transforms dirty for this object and its children."""
        self._world_transform_dirty = True
        for child in self._children:
            # noinspection protected-member
            child._invalidate_world_transform()

    def _invalidate_visible(self) -> None:
        """Mark cached visibility dirty for this object and its children."""
        self._visible_dirty = True
        for child in self._children:
            # noinspection protected-member
            child._invalidate_visible()
    
    @property
    def world_transform(self) -> Transform:
        # noinspection protected-member
        """Return the transform of this object in world space."""
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
    def world_pos(self) -> vec2:
        """Return the world-space position of this object."""
        return self.world_transform.pos

    @property
    def world_x_pos(self) -> float:
        """Return the world-space x position of this object."""
        return self.world_transform.x_pos

    @property
    def world_y_pos(self) -> float:
        """Return the world-space y position of this object."""
        return self.world_transform.y_pos

    @property
    def world_rotation(self) -> float:
        """Return the world-space rotation of this object in degrees."""
        return self.world_transform.rotation
    
    @property
    def camera_transform(self) -> Transform:
        """Return the transform of this object in camera space."""
        cam_pos = self.world_to_camera(self.world_transform.pos)
        return Transform(cam_pos, self.world_transform.rotation, self.world_transform.scale)

    @property
    def camera_pos(self) -> vec2:
        """Return the camera-space position of this object."""
        return self.camera_transform.pos

    @property
    def camera_x_pos(self) -> float:
        """Return the camera-space x position of this object."""
        return self.camera_transform.x_pos

    @property
    def camera_y_pos(self) -> float:
        """Return the camera-space y position of this object."""
        return self.camera_transform.y_pos

    @property
    def camera_rotation(self) -> float:
        """Return the camera-space rotation of this object in degrees."""
        return self.camera_transform.rotation
    
    # region properties
    
    @property
    def properties(self) -> dict[str, Any]:
        """Return the dynamic user-defined properties attached to this object."""
        return self._properties
    
    def get_property[T](self, name: str, default: Optional[T] = None, ignore_missing: bool = True) -> T:
        """
        Return a dynamic property, optionally raising when it is missing.

        :param name: Property name.
        :param default: Value returned when the property is missing.
        :param ignore_missing: Whether to return the default instead of raising.
        :return: The property value or the supplied default.
        :raises AttributeError: When the property is missing and ``ignore_missing`` is false.
        """
        if not ignore_missing and name not in self.properties:
            raise AttributeError(f"Unknown property '{name}', only has {self.properties.keys()}")
        return self.properties.get(name, default)

    def set_property(self, name: str, value: Any) -> PygameObject[R]:
        """
        Set a dynamic property.

        :param name: Property name.
        :param value: Value to store.
        :return: This object.
        """
        self.properties[name] = value
        return self

    def modify_property[T](self, name: str, modifier: Callable[[T], T], default: Optional[T] = None) -> PygameObject[R]:
        """
        Transform a dynamic property in place.

        :param name: Property name.
        :param modifier: Callable that receives and returns the property value.
        :param default: Value passed to the modifier when the property is missing.
        :return: This object.
        """
        self.set_property(name, modifier(self.get_property(name, default)))
        return self

    def remove_property(self, name: str) -> PygameObject[R]:
        """
        Remove a dynamic property if present.

        :param name: Property name.
        :return: This object.
        """
        self.properties.pop(name, None)
        return self
    
    # endregion
    
    # region pos
    @property
    def pos(self) -> vec2:
        """Return the local position of this object."""
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: vec2) -> None:
        """
        Set the local position of this object.

        :param value: The new local position of this object.
        """
        self.transform.pos = value
        self._invalidate_world_transform()
    
    @property
    def x_pos(self) -> float:
        """Return the local x position of this object."""
        return self.transform.x_pos
    
    @x_pos.setter
    def x_pos(self, value: float) -> None:
        """
        Set the local x position of this object.

        :param value: The new local x position of this object.
        """
        self.transform.x_pos = value
        self._invalidate_world_transform()
    
    @property
    def y_pos(self) -> float:
        """Return the local y position of this object."""
        return self.transform.y_pos
    
    @y_pos.setter
    def y_pos(self, value: float) -> None:
        """
        Set the local y position of this object.

        :param value: The new local y position of this object.
        """
        self.transform.y_pos = value
        self._invalidate_world_transform()
        
    def move(self, vec: vec2) -> PygameObject[R]:
        """
        Translate the object by a vector.

        :param vec: Translation vector.
        :return: This object.
        """
        self.pos += vec
        return self

    def move_x(self, dx: float) -> PygameObject[R]:
        """
        Translate the object horizontally.

        :param dx: Horizontal translation.
        :return: This object.
        """
        self.x_pos += dx
        return self

    def move_y(self, dy: float) -> PygameObject[R]:
        """
        Translate the object vertically.

        :param dy: Vertical translation.
        :return: This object.
        """
        self.y_pos += dy
        return self
    
    # endregion
    
    # region rotation
    @property
    def rotation(self) -> float:
        """Return the local rotation of this object in degrees."""
        return self.transform.rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        """
        Set the local rotation of this object in degrees.

        :param value: The new local rotation of this object in degrees.
        """
        self.transform.rotation = value
        self._invalidate_world_transform()
        
    def rotate(self, value: float) -> PygameObject[R]:
        """
        Rotate the object by an angle in degrees.

        :param value: Angle in degrees to add to the current rotation.
        :return: This object.
        """
        self.rotation += value
        return self
    # endregion
    
    # region scale
    @property
    def scale(self) -> float:
        """Return the uniform scale of this object."""
        return self.transform.scale
    
    @scale.setter
    def scale(self, value: float) -> None:
        """
        Set the uniform scale of this object.

        :param value: The new uniform scale of this object.
        """
        self.transform.scale = value
        self._invalidate_world_transform()
        
    def scale_by(self, value: float) -> PygameObject[R]:
        """
        Multiply the object's scale by a factor.

        :param value: Scale factor.
        :return: This object.
        """
        self.scale *= value
        return self
    # endregion
    
    # region anchor
    @property
    def anchor(self) -> vec2:
        """Return the anchor used to position the object's renderer relative to its transform."""
        return self._anchor
    
    @anchor.setter
    def anchor(self, value: vec2) -> None:
        """
        Set the anchor used to position the object's renderer relative to its transform.

        :param value: The new anchor used to position the object's renderer relative to its transform.
        """
        self._anchor = value
    # endregion
    
    # region layer
    
    # region layer
    @property
    def layer(self) -> Optional[Layer]:
        """Return the layer this object belongs to, inheriting from its parent when needed."""
        return self._layer if self._layer is not None else self._parent.layer if self._parent is not None else None

    @layer.setter
    def layer(self, value: Optional[Layer]) -> None:
        """
        Set the layer this object belongs to, inheriting from its parent when needed.

        :param value: The new value.
        """
        self._layer = value
    # endregion
    
    # endregion
    
    # region sub layer
    @property
    def sub_layer(self) -> int:
        """Return the sub-layer offset used for rendering order within a layer."""
        return self._sub_layer
    
    @sub_layer.setter
    def sub_layer(self, value: int) -> None:
        """
        Set the sub-layer offset used for rendering order within a layer.

        :param value: The new sub-layer offset used for rendering order within a layer.
        """
        self._sub_layer = value
    # endregion

    @property
    def render_sub_layer(self) -> int:
        """Return the effective render sub-layer including focus and parent offsets."""
        parent = self.parent
        return self._sub_layer + (FOCUSED_LAYER if self.focused else 0) + (parent.render_sub_layer if parent is not None else 0)
    
    # region clip_area
    
    @property
    def clip_area(self) -> Optional[FRect]:
        """Return the clipping rectangle applied to this object."""
        return self._clip_area
    
    @clip_area.setter
    def clip_area(self, value: Optional[FRect]) -> None:
        """
        Set the clipping rectangle applied to this object.

        :param value: The new clipping rectangle applied to this object.
        """
        self._clip_area = value
    
    @property
    def clip_area_relative(self) -> bool:
        """Return whether the clip area is relative to the parent transform."""
        return self._clip_area_relative
    
    def set_clip_area(self, rect: Optional[FRect], relative: bool = False) -> PygameObject[R]:
        """
        Set the clipping rectangle applied to this object.

        :param rect: Clipping rectangle, or ``None`` to clear it.
        :param relative: Whether the rectangle is relative to the parent transform.
        :return: This object.
        """
        self._clip_area = rect
        self._clip_area_relative = relative
        return self

    def clear_clip_area(self) -> PygameObject[R]:
        """
        Remove this object's clipping rectangle.

        :return: This object.
        """
        self._clip_area = None
        return self
    
    def get_world_clip_area(self) -> Optional[FRect]:
        """
        Return the effective world-space clipping rectangle for this object.

        :return: The clipping rectangle in world space, or ``None`` when unclipped.
        """
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
    
    # region children clip_area
    
    @property
    def children_clip_area(self) -> Optional[FRect]:
        """Return the clipping rectangle inherited by this object's children."""
        return self._children_clip_area
    
    @children_clip_area.setter
    def children_clip_area(self, value: Optional[FRect]) -> None:
        """
        Set the clipping rectangle inherited by this object's children.

        :param value: The new value.
        """
        self._children_clip_area = value
    
    @property
    def children_clip_area_relative(self) -> bool:
        """Return whether the children clip area is relative to this object's transform."""
        return self._children_clip_area_relative
    
    def set_children_clip_area(self, rect: Optional[FRect], relative: bool = False) -> PygameObject[R]:
        """
        Set the clipping rectangle inherited by children.

        :param rect: Clipping rectangle, or ``None`` to clear it.
        :param relative: Whether the rectangle is relative to this object's transform.
        :return: This object.
        """
        self._children_clip_area = rect
        self._children_clip_area_relative = relative
        return self
    
    def clear_children_clip_area(self) -> PygameObject[R]:
        """
        Remove the clipping rectangle inherited by children.

        :return: This object.
        """
        self._children_clip_area = None
        return self
    
    def get_world_children_clip_area(self) -> Optional[FRect]:
        
        """
        Return the effective world-space clipping rectangle inherited by children.

        :return: The children clipping rectangle in world space, or ``None`` when unclipped.
        """
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
    def parent(self) -> Optional[PygameObject]:
        """Return the parent object, if any."""
        return self._parent

    def set_parent(self, obj: Optional[PygameObject], anchor: vec2 = Anchor.C) -> PygameObject[R]:
        """
        Attach this object to a parent using the given parent anchor.

        :param obj: Parent object, or ``None`` to detach.
        :param anchor: Anchor on the parent used to position this object.
        :return: This object.
        """
        if self._parent is obj:
            self._parent_anchor = anchor
            return self

        old_parent = self._parent
        self._parent = obj
        self._parent_anchor = anchor

        if old_parent is not None:
            old_parent.remove_child(self)

        self._invalidate_world_transform()
        self._invalidate_visible()

        return self
    # endregion
    
    # region children
    @property
    def children(self) -> ObjectCollection:
        """Return the child objects attached to this object."""
        return self._children
    
    def add_child(self, obj: PygameObject, anchor: vec2 = Anchor.C) -> PygameObject[R]:
        """
        Attach an object as a child using the given anchor.

        :param obj: Object to attach as a child.
        :param anchor: Anchor on this object used to position the child.
        :return: This object.
        """
        self._children.add(obj)

        if obj.parent is not self:
            obj.set_parent(self, anchor)

        return self

    def remove_child(self, obj: PygameObject) -> PygameObject[R]:
        """
        Remove a child object from this object.

        :param obj: Child object to remove.
        :return: This object.
        """
        if self._children.has(obj):
            self._children.remove(obj)

        if obj.parent is self:
            obj.set_parent(None)

        return self

    # endregion
    
    @property
    def visible(self) -> bool:
        """Return whether this object and all ancestors are visible."""
        if not self._visible_dirty:
            return self._cached_visible
        
        parent = self.parent
        self._cached_visible = not self.has_flag(ObjectFlags.HIDDEN) and (parent is None or parent.visible)
        self._visible_dirty = False
        return self._cached_visible
    
    @visible.setter
    def visible(self, value: bool) -> None:
        """
        Set whether this object and all ancestors are visible.

        :param value: The new value.
        """
        self.show() if value else self.hide()
        
    @property
    def hidden(self) -> bool:
        """Return whether this object or an ancestor is hidden."""
        return not self.visible
    
    @hidden.setter
    def hidden(self, value: bool) -> None:
        """
        Set whether this object or an ancestor is hidden.

        :param value: The new value.
        """
        self.visible = value
    
    def show(self) -> PygameObject[R]:
        """
        Clear the hidden flag.

        :return: This object.
        """
        if self.has_flag(ObjectFlags.HIDDEN):
            self.remove_flag(ObjectFlags.HIDDEN)
        return self
    
    def hide(self) -> PygameObject[R]:
        """
        Set the hidden flag.

        :return: This object.
        """
        self.add_flag(ObjectFlags.HIDDEN)
        return self
    
    def toggle_visible(self) -> PygameObject[R]:
        """
        Toggle visibility.

        :return: This object.
        """
        self.visible = not self.visible
        return self
        
    def skip_rendering(self) -> PygameObject[R]:
        """
        Skip rendering this object.

        :return: This object.
        """
        self.add_flag(ObjectFlags.SKIP_RENDERING)
        return self
        
    def enable_rendering(self) -> PygameObject[R]:
        """
        Allow rendering this object.

        :return: This object.
        """
        self.remove_flag(ObjectFlags.SKIP_RENDERING)
        return self


    @property
    def focused(self) -> bool:
        """Return whether this object is focused."""
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        """
        Set whether this object is focused.

        :param value: The new value.
        """
        self._focused = value

    def focus(self) -> PygameObject[R]:
        """
        Mark this object as focused.

        :return: This object.
        """
        self.focused = True
        return self

    def unfocus(self) -> PygameObject[R]:
        """
        Clear the focused state.

        :return: This object.
        """
        self.focused = False
        return self

    def toggle_focus(self) -> PygameObject[R]:
        """
        Toggle the focused state.

        :return: This object.
        """
        self.focused = not self.focused
        return self
    
    
    @property
    def frozen(self) -> bool:
        """Return whether this object or any ancestor is frozen."""
        parent = self.parent
        return self.has_flag(ObjectFlags.FROZEN) or (parent is not None and parent.frozen)

    @frozen.setter
    def frozen(self, value: bool) -> None:
        """
        Set whether this object or any ancestor is frozen.

        :param value: The new value.
        """
        self.freeze() if value else self.unfreeze()

    def unfreeze(self) -> PygameObject[R]:
        """
        Clear this object's frozen flag.

        :return: This object.
        """
        if self.has_flag(ObjectFlags.FROZEN):
            self.remove_flag(ObjectFlags.FROZEN)
        return self
    
    def freeze(self) -> PygameObject[R]:
        """
        Set this object's frozen flag.

        :return: This object.
        """
        self.add_flag(ObjectFlags.FROZEN)
        return self
    
    def toggle_freeze(self) -> PygameObject[R]:
        """
        Toggle this object's frozen flag.

        :return: This object.
        """
        self.frozen = not self.frozen
        return self
    
    
    def skip_update(self) -> PygameObject[R]:
        """
        Skip behavior updates for this object.

        :return: This object.
        """
        self.add_flag(ObjectFlags.SKIP_UPDATE)
        return self
    
    def enable_update(self) -> PygameObject[R]:
        """
        Allow behavior updates for this object.

        :return: This object.
        """
        self.remove_flag(ObjectFlags.SKIP_UPDATE)
        return self
        
    
    @property
    def flags(self) -> ObjectFlags:
        """Return the bit flags controlling object behavior."""
        return self._flags
    
    def add_flag(self, flag: ObjectFlags) -> PygameObject[R]:
        """
        Add one or more flags.

        :param flag: Flag bits to add.
        :return: This object.
        """
        self._flags |= flag
        if flag & ObjectFlags.HIDDEN:
            self._invalidate_visible()
        return self
        
    def remove_flag(self, flag: ObjectFlags) -> PygameObject[R]:
        """
        Remove one or more flags.

        :param flag: Flag bits to remove.
        :return: This object.
        """
        self._flags &= ~flag
        if flag & ObjectFlags.HIDDEN:
            self._invalidate_visible()
        return self
    
    def has_flag(self, flag: ObjectFlags) -> bool:
        """
        Return whether all bits in a flag are set.

        :param flag: Flag bits to test.
        :return: ``True`` when every bit in ``flag`` is set.
        """
        return (int(self._flags) & int(flag)) == int(flag)
    
    
    @property
    def tags(self) -> ObjectTags:
        """Return the object tags used for categorization."""
        return self._tags
    
    def add_tag(self, tag: ObjectTags) -> PygameObject[R]:
        """
        Add one or more object tags.

        :param tag: Tag bits to add.
        :return: This object.
        """
        self._tags |= tag
        return self

    def remove_tag(self, tag: ObjectTags) -> PygameObject[R]:
        """
        Remove one or more object tags.

        :param tag: Tag bits to remove.
        :return: This object.
        """
        self._tags &= ~tag
        return self

    def has_tag(self, tag: ObjectTags) -> bool:
        """
        Return whether all bits in a tag are set.

        :param tag: Tag bits to test.
        :return: ``True`` when every bit in ``tag`` is set.
        """
        return (int(self._tags) & int(tag)) == int(tag)


    @property
    def services(self) -> ServicesCollection:
        """Return the services collection available to this object."""
        return self._services

    
    @property
    def behaviors(self) -> BehaviorManager:
        """Return the behavior manager for this object."""
        return self._behaviors
    
    def add_behavior[T: ObjectBehavior](self, behavior: T, behavior_id: Optional[str] = None) -> T:
        """
        Attach a behavior to this object.

        :param behavior: Behavior instance to attach.
        :param behavior_id: Optional identifier for the behavior.
        :return: The attached behavior.
        """
        return self.behaviors.add(behavior, behavior_id)
        
    def remove_behavior[T: ObjectBehavior](self, behavior: T | str) -> Optional[T]:
        """
        Detach a behavior from this object.

        :param behavior: Behavior instance or identifier to detach.
        :return: The detached behavior, or ``None`` when it was not attached.
        """
        return self.behaviors.remove(behavior)
    
    # endregion
    
    def set_world_position(self, world_pos: vec2) -> PygameObject[R]:
        """
        Set the object's position from a world-space position.

        :param world_pos: Target position in world space.
        :return: This object.
        """
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
        return self

    def set_world_rotation(self, world_rotation: float) -> PygameObject[R]:
        """
        Set rotation while accounting for the parent's world rotation.

        :param world_rotation: Target rotation in world space, in degrees.
        :return: This object.
        """
        parent = self.parent
        if parent is None:
            self.transform.rotation = world_rotation
        else:
            self.transform.rotation = world_rotation - parent.world_transform.rotation
        return self
    
    # region REGISTRATION METHODS
    
    def register_event_callback(self, event_type: str, callback: Callback[[Event], Any]) -> None:
        """
        Register an event callback for this object's event manager.

        :param event_type: Event type to listen for.
        :param callback: Callback invoked when the event is triggered.
        """
        self.services.get_event_manager().register(event_type, callback)

    def register_quick_debug(self, name: str, getter: Callable[[PygameObject], Any], template: str = "{}") -> None:
        """
        Register a quick-debug value backed by this object.

        :param name: Debug entry name.
        :param getter: Callable that receives this object and returns the value.
        :param template: Format template used to display the value.
        """
        self.services.get_quick_debug_manager().register_listener(name, lambda: getter(self), template)

    def do_on_update(self, action: Callback[[PygameObject], Any]) -> PygameObject[R]:
        """
        Attach an update callback behavior.

        :param action: Callback invoked on each update with this object.
        :return: This object.
        """
        self.add_behavior(ActionOnUpdateBehavior(action))
        return self

    def do_on_click(
        self,
        button: int,
        on_click: Optional[Callback[[PygameObject], Any]] = None,
        on_hold: Optional[Callback[[PygameObject], Any]] = None,
        on_release: Optional[Callback[[PygameObject], Any]] = None,
    ) -> PygameObject[R]:
        """
        Attach click, hold, and release callback behavior.

        :param button: Mouse button index to listen for.
        :param on_click: Optional callback invoked on press.
        :param on_hold: Optional callback invoked while held.
        :param on_release: Optional callback invoked on release.
        :return: This object.
        """
        self.add_behavior(ActionOnClickBehavior(button, on_click, on_hold, on_release))
        return self

    def do_on_hover(
        self,
        hover_start: Optional[Callback[[PygameObject], Any]] = None,
        while_hovered: Optional[Callback[[PygameObject], Any]] = None,
        hover_end: Optional[Callback[[PygameObject], Any]] = None,
    ) -> PygameObject[R]:
        """
        Attach hover callback behavior.

        :param hover_start: Optional callback invoked when hovering starts.
        :param while_hovered: Optional callback invoked while hovered.
        :param hover_end: Optional callback invoked when hovering ends.
        :return: This object.
        """
        self.add_behavior(ActionOnHoverBehavior(hover_start, while_hovered, hover_end))
        return self

    def do_on_scroll(self, action: Callback[[PygameObject, int, vec2], Any]) -> PygameObject[R]:
        """
        Attach a scroll callback behavior.

        :param action: Callback invoked with the object, scroll amount, and position.
        :return: This object.
        """
        self.add_behavior(ActionOnScrollBehavior(action))
        return self

    def do_on_collision(
        self,
        on_collision: Optional[Callback[[PygameObject, PygameObject], Any]] = None,
        while_colliding: Optional[Callback[[PygameObject, PygameObject], Any]] = None,
        on_collision_end: Optional[Callback[[PygameObject, PygameObject], Any]] = None,
        condition_on_other: Optional[Callable[[PygameObject], bool]] = None,
    ) -> PygameObject[R]:
        """
        Attach collision callback behavior.

        :param on_collision: Optional callback invoked when a collision begins.
        :param while_colliding: Optional callback invoked while colliding.
        :param on_collision_end: Optional callback invoked when a collision ends.
        :param condition_on_other: Optional predicate that filters colliding objects.
        :return: This object.
        """
        self.add_behavior(ActionOnCollisionBehavior(on_collision, while_colliding, on_collision_end, condition_on_other))
        return self
    
    
    def make_attribute_dynamic(
        self,
        attribute: str,
        value_getter: Any | Callable[[], Any | tuple[Any, ...]],
        template: Optional[str] = None,
        strength: float = 1,
        attr_getter: Callable[..., Any] = getattr,
        attr_setter: Callable[..., Any] = setattr,
    ) -> PygameObject[R]:
        """
        Drive an attribute from a getter every update.

        :param attribute: Attribute name to drive.
        :param value_getter: Value or zero-argument callable supplying the value.
        :param template: Optional format template applied to the value.
        :param strength: Interpolation strength applied each update.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        :return: This object.
        """
        self.add_behavior(
            DynamicAttributeBehavior(attribute, value_getter, template, strength, attr_getter, attr_setter),
            f"attribute_{attribute}_setter",
        )
        return self

    def make_attribute_fixed(
        self,
        attribute: str,
        value: Optional[Any | Callable[[], Any]] = None,
        strength: float = 1,
        attr_getter: Callable[..., Any] = getattr,
        attr_setter: Callable[..., Any] = setattr,
    ) -> PygameObject[R]:
        """
        Force an attribute to a fixed value or getter.

        :param attribute: Attribute name to fix.
        :param value: Fixed value or zero-argument callable.
        :param strength: Interpolation strength applied each update.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        :return: This object.
        """
        self.add_behavior(
            AttributeFixingBehavior(attribute, value, strength, attr_getter, attr_setter),
            f"attribute_{attribute}_setter",
        )
        return self

    def make_attribute_clamped(
        self,
        attribute: str,
        min_value: Optional[float | Callable[[], float]] = None,
        max_value: Optional[float | Callable[[], float]] = None,
        strength: float = 1,
        attr_getter: Callable[..., Any] = getattr,
        attr_setter: Callable[..., Any] = setattr,
    ) -> PygameObject[R]:
        """
        Clamp an attribute to optional minimum and maximum values.

        :param attribute: Attribute name to clamp.
        :param min_value: Optional lower bound or getter.
        :param max_value: Optional upper bound or getter.
        :param strength: Interpolation strength applied each update.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        :return: This object.
        """
        self.add_behavior(
            AttributeClampingBehavior(attribute, min_value, max_value, strength, attr_getter, attr_setter)
        )
        return self

    def make_attribute_snap(
        self,
        attribute: str,
        values: list[float],
        offset: float = 0,
        strength: float = 1,
        attr_getter: Callable[..., Any] = getattr,
        attr_setter: Callable[..., Any] = setattr,
    ) -> PygameObject[R]:
        """
        Snap an attribute to the nearest value in a list.

        :param attribute: Attribute name to snap.
        :param values: Candidate values.
        :param offset: Offset applied when comparing values.
        :param strength: Interpolation strength applied each update.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        :return: This object.
        """
        self.add_behavior(
            AttributeValueSnappingBehavior(attribute, values, offset, strength, attr_getter, attr_setter)
        )
        return self

    def make_attribute_snap_on_grid(
        self,
        attribute: str,
        step: float,
        offset: float = 0,
        strength: float = 1,
        attr_getter: Callable[..., Any] = getattr,
        attr_setter: Callable[..., Any] = setattr,
    ) -> PygameObject[R]:
        """
        Snap an attribute to a regular grid.

        :param attribute: Attribute name to snap.
        :param step: Grid step size.
        :param offset: Offset applied to the grid.
        :param strength: Interpolation strength applied each update.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        :return: This object.
        """
        self.add_behavior(
            AttributeGridSnappingBehavior(attribute, step, offset, strength, attr_getter, attr_setter)
        )
        return self
    
    
    def make_property_dynamic(
        self,
        prop_name: str,
        value_getter: Any | Callable[[], Any | tuple[Any, ...]],
        template: Optional[str] = None,
        strength: float = 1,
    ) -> PygameObject[R]:
        """
        Drive a dynamic property from a getter every update.

        :param prop_name: Dynamic property name to drive.
        :param value_getter: Value or zero-argument callable supplying the value.
        :param template: Optional format template applied to the value.
        :param strength: Interpolation strength applied each update.
        :return: This object.
        """
        self.add_behavior(
            DynamicAttributeBehavior(
                prop_name,
                value_getter,
                template,
                strength,
                lambda obj, name: obj.get_property(name),
                lambda obj, name, value: obj.set_property(name, value),
            ),
            f"property_{prop_name}_setter",
        )
        return self

    def make_property_fixed(
        self,
        prop_name: str,
        value: Optional[Any | Callable[[], Any]] = None,
        strength: float = 1,
    ) -> PygameObject[R]:
        """
        Force a dynamic property to a fixed value or getter.

        :param prop_name: Dynamic property name to fix.
        :param value: Fixed value or zero-argument callable.
        :param strength: Interpolation strength applied each update.
        :return: This object.
        """
        self.add_behavior(
            AttributeFixingBehavior(
                prop_name,
                value,
                strength,
                lambda obj, name: obj.get_property(name),
                lambda obj, name, new_value: obj.set_property(name, new_value),
            ),
            f"property_{prop_name}_setter",
        )
        return self

    def make_property_clamped(
        self,
        prop_name: str,
        min_value: Optional[float | Callable[[], float]] = None,
        max_value: Optional[float | Callable[[], float]] = None,
        strength: float = 1,
    ) -> PygameObject[R]:
        """
        Clamp a dynamic property to optional bounds.

        :param prop_name: Dynamic property name to clamp.
        :param min_value: Optional lower bound or getter.
        :param max_value: Optional upper bound or getter.
        :param strength: Interpolation strength applied each update.
        :return: This object.
        """
        self.add_behavior(
            AttributeClampingBehavior(
                prop_name,
                min_value,
                max_value,
                strength,
                lambda obj, name: obj.get_property(name),
                lambda obj, name, value: obj.set_property(name, value),
            )
        )
        return self

    def make_property_snap(
        self,
        prop_name: str,
        values: list[float],
        offset: float = 0,
        strength: float = 1,
    ) -> PygameObject[R]:
        """
        Snap a dynamic property to the nearest value in a list.

        :param prop_name: Dynamic property name to snap.
        :param values: Candidate values.
        :param offset: Offset applied when comparing values.
        :param strength: Interpolation strength applied each update.
        :return: This object.
        """
        self.add_behavior(
            AttributeValueSnappingBehavior(
                prop_name,
                values,
                offset,
                strength,
                lambda obj, name: obj.get_property(name),
                lambda obj, name, value: obj.set_property(name, value),
            )
        )
        return self

    def make_property_snap_on_grid(
        self,
        prop_name: str,
        step: float,
        offset: float = 0,
        strength: float = 1,
    ) -> PygameObject[R]:
        """
        Snap a dynamic property to a regular grid.

        :param prop_name: Dynamic property name to snap.
        :param step: Grid step size.
        :param offset: Offset applied to the grid.
        :param strength: Interpolation strength applied each update.
        :return: This object.
        """
        self.add_behavior(
            AttributeGridSnappingBehavior(
                prop_name,
                step,
                offset,
                strength,
                lambda obj, name: obj.get_property(name),
                lambda obj, name, value: obj.set_property(name, value),
            )
        )
        return self
    
    
    def make_draggable(
        self,
        button: int = 1,
        target: Optional[PygameObject] = None,
        on_drag_start: Optional[Callback[[PygameObject], None]] = None,
        while_dragging: Optional[Callback[[PygameObject], None]] = None,
        on_drag_end: Optional[Callback[[PygameObject], None]] = None,
    ) -> PygameObject[R]:
        """
        Attach draggable behavior to this object.

        :param button: Mouse button used for dragging.
        :param target: Optional object to move instead of this object.
        :param on_drag_start: Optional callback invoked when dragging starts.
        :param while_dragging: Optional callback invoked while dragging.
        :param on_drag_end: Optional callback invoked when dragging ends.
        :return: This object.
        """
        self.add_behavior(
            DraggableBehavior(button, target, on_drag_start, while_dragging, on_drag_end),
            DRAGGABLE_BEHAVIOR_ID,
        )
        return self

    # endregion

    # region PHYSICS
    
    @staticmethod
    def get_default_shape_type() -> Literal["box", "circle"]:
        """
        Return the default shape type for this object's physics body.

        :return: The default shape type.
        """
        return ShapeTypes.BOX

    @property
    def physics_body(self) -> Optional[PhysicsBody]:
        """Return the physics body attached to this object, if any."""
        return self._physics_body

    @property
    def has_physics(self) -> bool:
        """Return whether this object has a physics body."""
        return self._physics_body is not None

    def add_physics_body(self, shape_type: Optional[Literal["box", "circle"]] = None, sensor: bool = False,
                         dims: Optional[vec2] = None, radius: Optional[float] = None,
                         body_type: int = BodyTypes.DYNAMIC, mass: float = 1, moment: Optional[float] = None, friction: float = 0.5,
                         elasticity: float = 0.0, collision_layer: int = 1, collision_mask: int = 0xFFFFFFFF) -> PhysicsBody:
        """
        Create and attach a physics body with an optional shape.

        :param shape_type: Shape type, or ``None`` for the default.
        :param sensor: Whether the shape is a non-solid sensor.
        :param dims: Box dimensions, or ``None`` to use the renderer dimensions.
        :param radius: Circle radius, or ``None`` to derive it.
        :param body_type: Pymunk body type constant.
        :param mass: Body mass.
        :param moment: Rotational inertia, or ``None`` to calculate it.
        :param friction: Shape friction coefficient.
        :param elasticity: Shape elasticity coefficient.
        :param collision_layer: Collision category bits.
        :param collision_mask: Collision mask bits.
        :return: The created physics body.
        """
        body = PhysicsBody(self, body_type, mass, moment, friction, elasticity, sensor, collision_layer, collision_mask)

        shape_type = shape_type or self.get_default_shape_type()
        
        dims = self.dims if dims is None else dims
        radius = radius if radius is not None else getattr(self, "radius") if hasattr(self, "radius") else length(dims)
        
        if shape_type == ShapeTypes.BOX:
            body.add_box_shape(dims.to_tuple())
        elif shape_type == ShapeTypes.CIRCLE:
            body.add_circle_shape(radius)

        self._physics_body = body
        self.add_flag(ObjectFlags.COLLIDABLE if sensor else ObjectFlags.PHYSICS)
        self._register_body_with_layer()
        return body
    
    def add_collision_box(self, shape_type: Optional[Literal["box", "circle"]] = None) -> PhysicsBody:
        """
        Add a static collision shape to this object.

        :param shape_type: Shape type, or ``None`` for the default.
        :return: The created physics body.
        """
        return self.add_physics_body(shape_type, True, body_type=BodyTypes.STATIC)

    def remove_physics_body(self) -> PygameObject[R]:
        """
        Remove this object's physics body, if any.

        :return: This object.
        """
        if self._physics_body is not None:
            self._unregister_body_from_layer()
            self._physics_body.remove()
            self._physics_body = None
            self.remove_flag(ObjectFlags.COLLIDABLE | ObjectFlags.PHYSICS)
        return self

    def _register_body_with_layer(self) -> None:
        """Register the physics body with the object's layer, if possible."""
        if self._physics_body and self._layer and self._layer.physics_world:
            self._layer.physics_world.add_body(self._physics_body)

    def _unregister_body_from_layer(self) -> None:
        """Remove the physics body from the object's layer, if possible."""
        if self._physics_body and self._layer and self._layer.physics_world:
            self._layer.physics_world.remove_body(self._physics_body)

    # endregion
    
    # region BEHAVIOR METHODS
    
    def while_hovered(self) -> None:
        """Dispatch the hover callback to behaviors."""
        self.behaviors.on_hover()

    def on_hover_end(self) -> None:
        """Dispatch the hover-end callback to behaviors."""
        self.behaviors.on_hover_end()

    def on_hover_start(self) -> None:
        """Dispatch the hover-start callback to behaviors."""
        self.behaviors.on_hover_start()

    def on_click(self, button: int, pos: vec2) -> None:
        """
        Dispatch a click callback to behaviors.

        :param button: Mouse button index.
        :param pos: Position in the object's local space.
        """
        self.behaviors.on_click(button, pos)

    def on_hold(self, button: int, pos: vec2) -> None:
        """
        Dispatch a hold callback to behaviors.

        :param button: Mouse button index.
        :param pos: Position in the object's local space.
        """
        self.behaviors.on_hold(button, pos)

    def on_release(self, button: int, pos: vec2) -> None:
        """
        Dispatch a release callback to behaviors.

        :param button: Mouse button index.
        :param pos: Position in the object's local space.
        """
        self.behaviors.on_release(button, pos)

    def on_scroll(self, scroll: int, pos: vec2) -> None:
        """
        Dispatch a scroll callback to behaviors.

        :param scroll: Scroll amount.
        :param pos: Position in the object's local space.
        """
        self.behaviors.on_scroll(scroll, pos)

    def on_collision(self, obj: PygameObject) -> None:
        """
        Dispatch a collision-begin callback to behaviors.

        :param obj: Other object involved in the collision.
        """
        self.behaviors.on_collision(obj)

    def on_collision_end(self, obj: PygameObject) -> None:
        """
        Dispatch a collision-end callback to behaviors.

        :param obj: Other object involved in the collision.
        """
        self.behaviors.on_collision_end(obj)
    
    # endregion
    
    # region HIT TEST METHODS
    
    def test_screen_hit(self, screen: vec2) -> bool:
        """
        Test whether a screen space position hits this object.

        :param screen: Position in screen space.
        :return: ``True`` when the position hits the object.
        """
        cam_pos = self.screen_to_camera(screen)
        return self.test_camera_hit(cam_pos)
    
    def test_camera_hit(self, camera_pos: vec2) -> bool:
        """
        Test whether a camera space position hits this object.

        :param camera_pos: Position in camera space.
        :return: ``True`` when the position hits the object.
        """
        clip = self.get_world_clip_area()
        if clip is not None:
            world_pos = self.camera_to_world(camera_pos)
            if not clip.collidepoint(world_pos.x, world_pos.y):
                return False
        return self.test_pixel_hit(self.camera_to_pixel(camera_pos))
    
    def test_world_hit(self, world: vec2) -> bool:
        """
        Test whether a world space position hits this object.

        :param world: Position in world space.
        :return: ``True`` when the position hits the object.
        """
        return self.test_camera_hit(self.world_to_camera(world))
    
    def test_local_hit(self, local: vec2) -> bool:
        """
        Test whether a local space position hits this object.

        :param local: Position in local space.
        :return: ``True`` when the position hits the object.
        """
        return self.test_pixel_hit(self.local_to_pixel(local))
    
    def test_pixel_hit(self, pixel: vec2) -> bool:
        """
        Test whether a pixel space position hits this object.

        :param pixel: Position in pixel space.
        :return: ``True`` when the position hits the object.
        """
        return self.renderer.test_hit(pixel) if self.renderer else False
    
    def test_uv_hit(self, uv: vec2) -> bool:
        """
        Test whether a UV space position hits this object.

        :param uv: Position in UV space.
        :return: ``True`` when the position hits the object.
        """
        return self.test_pixel_hit(self.uv_to_pixel(uv))
    
    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # region From Screen
    def screen_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to viewport space.

        :param pos: Position in screen space.
        :return: Position in viewport space.
        """
        return self.layer.screen_to_viewport_pos(pos) # type: ignore
    def screen_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to camera space.

        :param pos: Position in screen space.
        :return: Position in camera space.
        """
        return self.layer.screen_to_camera_pos(pos) # type: ignore
    def screen_to_world(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to world space.

        :param pos: Position in screen space.
        :return: Position in world space.
        """
        return self.layer.screen_to_world_pos(pos) # type: ignore
    def screen_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to layer space.

        :param pos: Position in screen space.
        :return: Position in layer space.
        """
        return self.world_to_layer(self.screen_to_world(pos))
    def screen_to_local(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to local space.

        :param pos: Position in screen space.
        :return: Position in local space.
        """
        return self.world_to_local(self.screen_to_world(pos))
    def screen_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to pixel space.

        :param pos: Position in screen space.
        :return: Position in pixel space.
        """
        return self.local_to_pixel(self.screen_to_local(pos))
    def screen_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a screen space position to children-local space.

        :param pos: Position in screen space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.screen_to_pixel(pos), children_anchor)
    def screen_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to UV space.

        :param pos: Position in screen space.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.screen_to_pixel(pos))
    # endregion
    
    # region From Viewport
    def viewport_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to screen space.

        :param pos: Position in viewport space.
        :return: Position in screen space.
        """
        return self.layer.viewport_to_screen_pos(pos) # type: ignore
    def viewport_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to camera space.

        :param pos: Position in viewport space.
        :return: Position in camera space.
        """
        return self.layer.viewport_to_camera_pos(pos) # type: ignore
    def viewport_to_world(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to world space.

        :param pos: Position in viewport space.
        :return: Position in world space.
        """
        return self.layer.viewport_to_world_pos(pos) # type: ignore
    def viewport_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to layer space.

        :param pos: Position in viewport space.
        :return: Position in layer space.
        """
        return self.world_to_layer(self.viewport_to_world(pos))
    def viewport_to_local(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to local space.

        :param pos: Position in viewport space.
        :return: Position in local space.
        """
        return self.world_to_local(self.viewport_to_world(pos))
    def viewport_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to pixel space.

        :param pos: Position in viewport space.
        :return: Position in pixel space.
        """
        return self.local_to_pixel(self.viewport_to_local(pos))
    def viewport_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a viewport space position to children-local space.

        :param pos: Position in viewport space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.viewport_to_pixel(pos), children_anchor)
    def viewport_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to UV space.

        :param pos: Position in viewport space.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.viewport_to_pixel(pos))
    # endregion
    
    # region From Camera
    def camera_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to screen space.

        :param pos: Position in camera space.
        :return: Position in screen space.
        """
        return self.layer.camera_to_screen_pos(pos) # type: ignore
    def camera_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to viewport space.

        :param pos: Position in camera space.
        :return: Position in viewport space.
        """
        return self.layer.camera_to_viewport_pos(pos) # type: ignore
    def camera_to_world(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to world space.

        :param pos: Position in camera space.
        :return: Position in world space.
        """
        return self.layer.camera_to_world_pos(pos) # type: ignore
    def camera_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to layer space.

        :param pos: Position in camera space.
        :return: Position in layer space.
        """
        return self.world_to_layer(self.camera_to_world(pos))
    def camera_to_local(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to local space.

        :param pos: Position in camera space.
        :return: Position in local space.
        """
        return self.world_to_local(self.camera_to_world(pos))
    def camera_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to pixel space.

        :param pos: Position in camera space.
        :return: Position in pixel space.
        """
        return self.local_to_pixel(self.camera_to_local(pos))
    def camera_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a camera space position to children-local space.

        :param pos: Position in camera space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.camera_to_pixel(pos), children_anchor)
    def camera_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to UV space.

        :param pos: Position in camera space.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.camera_to_pixel(pos))
    # endregion
    
    # region From World
    def world_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a world space position to screen space.

        :param pos: Position in world space.
        :return: Position in screen space.
        """
        return self.layer.world_to_screen_pos(pos) # type: ignore
    def world_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a world space position to viewport space.

        :param pos: Position in world space.
        :return: Position in viewport space.
        """
        return self.layer.world_to_viewport_pos(pos) # type: ignore
    def world_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a world space position to camera space.

        :param pos: Position in world space.
        :return: Position in camera space.
        """
        return self.layer.world_to_camera_pos(pos) # type: ignore
    def world_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a world space position to layer space.

        :param pos: Position in world space.
        :return: Position in layer space.
        """
        return self.layer.world_to_local_pos(pos) # type: ignore
    def world_to_local(self, pos: vec2) -> vec2:
        """
        Convert a world space position to local space.

        :param pos: Position in world space.
        :return: Position in local space.
        """
        return self.world_transform.apply_inverse_on_point(pos)
    def world_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a world space position to pixel space.

        :param pos: Position in world space.
        :return: Position in pixel space.
        """
        return self.local_to_pixel(self.world_to_local(pos))
    def world_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a world space position to children-local space.

        :param pos: Position in world space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.world_to_pixel(pos), children_anchor)
    def world_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a world space position to UV space.

        :param pos: Position in world space.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.world_to_pixel(pos))
    # endregion
    
    # region From Layer
    def layer_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to screen space.

        :param pos: Position in layer space.
        :return: Position in screen space.
        """
        return self.world_to_screen(self.layer_to_world(pos))
    def layer_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to viewport space.

        :param pos: Position in layer space.
        :return: Position in viewport space.
        """
        return self.world_to_viewport(self.layer_to_world(pos))
    def layer_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to camera space.

        :param pos: Position in layer space.
        :return: Position in camera space.
        """
        return self.world_to_camera(self.layer_to_world(pos))
    def layer_to_world(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to world space.

        :param pos: Position in layer space.
        :return: Position in world space.
        """
        return self.layer.local_to_world_pos(pos) # type: ignore
    def layer_to_local(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to local space.

        :param pos: Position in layer space.
        :return: Position in local space.
        """
        return self.world_to_local(self.layer_to_world(pos))
    def layer_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to pixel space.

        :param pos: Position in layer space.
        :return: Position in pixel space.
        """
        return self.local_to_pixel(self.layer_to_local(pos))
    def layer_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a layer space position to children-local space.

        :param pos: Position in layer space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.layer_to_pixel(pos), children_anchor)
    def layer_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a layer space position to UV space.

        :param pos: Position in layer space.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.layer_to_pixel(pos))
    # endregion
    
    # region From Local
    def local_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a local space position to screen space.

        :param pos: Position in local space.
        :return: Position in screen space.
        """
        return self.world_to_screen(self.local_to_world(pos))
    def local_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a local space position to viewport space.

        :param pos: Position in local space.
        :return: Position in viewport space.
        """
        return self.world_to_viewport(self.local_to_world(pos))
    def local_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a local space position to camera space.

        :param pos: Position in local space.
        :return: Position in camera space.
        """
        return self.world_to_camera(self.local_to_world(pos))
    def local_to_world(self, pos: vec2) -> vec2:
        """
        Convert a local space position to world space.

        :param pos: Position in local space.
        :return: Position in world space.
        """
        return self.world_transform.apply_on_point(pos)
    def local_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a local space position to layer space.

        :param pos: Position in local space.
        :return: Position in layer space.
        """
        return self.world_to_layer(self.local_to_world(pos))
    def local_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a local space position to pixel space.

        :param pos: Position in local space.
        :return: Position in pixel space.
        """
        return pos + self.get_anchor_offset(self.anchor)
    def local_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a local space position to children-local space.

        :param pos: Position in local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.local_to_pixel(pos), children_anchor)
    def local_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a local space position to UV space.

        :param pos: Position in local space.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.local_to_pixel(pos))
    # endregion
    
    # region From Pixel
    def pixel_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to screen space.

        :param pos: Position in pixel space.
        :return: Position in screen space.
        """
        return self.local_to_screen(self.pixel_to_local(pos))
    def pixel_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to viewport space.

        :param pos: Position in pixel space.
        :return: Position in viewport space.
        """
        return self.local_to_viewport(self.pixel_to_local(pos))
    def pixel_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to camera space.

        :param pos: Position in pixel space.
        :return: Position in camera space.
        """
        return self.local_to_camera(self.pixel_to_local(pos))
    def pixel_to_world(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to world space.

        :param pos: Position in pixel space.
        :return: Position in world space.
        """
        return self.local_to_world(self.pixel_to_local(pos))
    def pixel_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to layer space.

        :param pos: Position in pixel space.
        :return: Position in layer space.
        """
        return self.local_to_layer(self.pixel_to_local(pos))
    def pixel_to_local(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to local space.

        :param pos: Position in pixel space.
        :return: Position in local space.
        """
        return pos - self.get_anchor_offset(self.anchor)
    def pixel_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a pixel space position to children-local space.

        :param pos: Position in pixel space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return pos - self.get_anchor_offset(children_anchor)
    def pixel_to_uv(self, pos: vec2) -> vec2:
        """
        Convert a pixel space position to UV space.

        :param pos: Position in pixel space.
        :return: Position in UV space.
        """
        return self.renderer.local_to_uv(pos) if self.renderer else vec2()
    # endregion
    
    # region From Children Local
    def children_local_to_screen(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to screen space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in screen space.
        """
        return self.pixel_to_screen(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_viewport(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to viewport space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in viewport space.
        """
        return self.pixel_to_viewport(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_camera(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to camera space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in camera space.
        """
        return self.pixel_to_camera(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_world(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to world space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in world space.
        """
        return self.pixel_to_world(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_layer(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to layer space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in layer space.
        """
        return self.pixel_to_layer(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to local space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in local space.
        """
        return self.pixel_to_local(self.children_local_to_pixel(pos, children_anchor))
    def children_local_to_pixel(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to pixel space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in pixel space.
        """
        return pos + self.get_anchor_offset(children_anchor)
    def children_local_to_uv(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a children-local space position to UV space.

        :param pos: Position in children-local space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in UV space.
        """
        return self.pixel_to_uv(self.children_local_to_pixel(pos, children_anchor))
    # endregion
    
    # region From UV
    def uv_to_screen(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to screen space.

        :param pos: Position in UV space.
        :return: Position in screen space.
        """
        return self.pixel_to_screen(self.uv_to_pixel(pos))
    def uv_to_viewport(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to viewport space.

        :param pos: Position in UV space.
        :return: Position in viewport space.
        """
        return self.pixel_to_viewport(self.uv_to_pixel(pos))
    def uv_to_camera(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to camera space.

        :param pos: Position in UV space.
        :return: Position in camera space.
        """
        return self.pixel_to_camera(self.uv_to_pixel(pos))
    def uv_to_world(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to world space.

        :param pos: Position in UV space.
        :return: Position in world space.
        """
        return self.pixel_to_world(self.uv_to_pixel(pos))
    def uv_to_layer(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to layer space.

        :param pos: Position in UV space.
        :return: Position in layer space.
        """
        return self.pixel_to_layer(self.uv_to_pixel(pos))
    def uv_to_local(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to local space.

        :param pos: Position in UV space.
        :return: Position in local space.
        """
        return self.pixel_to_local(self.uv_to_pixel(pos))
    def uv_to_pixel(self, pos: vec2) -> vec2:
        """
        Convert a UV space position to pixel space.

        :param pos: Position in UV space.
        :return: Position in pixel space.
        """
        return self.renderer.uv_to_local(pos) if self.renderer else vec2()
    def uv_to_children_local(self, pos: vec2, children_anchor: vec2) -> vec2:
        """
        Convert a UV space position to children-local space.

        :param pos: Position in UV space.
        :param children_anchor: Anchor on this object used for children-local coordinates.
        :return: Position in children-local space.
        """
        return self.pixel_to_children_local(self.uv_to_pixel(pos), children_anchor)
    # endregion
    
    # region Coordinates Helpers
    def get_anchor_offset(self, anchor: vec2) -> vec2:
        """
        Return the pixel offset for an anchor within this object.

        :param anchor: Anchor in UV space.
        :return: The anchor offset in pixel space.
        """
        return self.uv_to_pixel(anchor)
    def world_to_parent_local(self, pos: vec2) -> vec2:
        """
        Convert a world space position to parent-local space.

        :param pos: Position in world space.
        :return: Position in parent-local space.
        """
        return self.parent.world_to_local(pos) if self.parent else pos # type: ignore
    def world_to_parent_children_local(self, pos: vec2) -> vec2:
        """
        Convert a world space position to parent children-local space.

        :param pos: Position in world space.
        :return: Position in parent children-local space.
        """
        return self.parent.world_to_children_local(pos, self._parent_anchor) if self.parent else pos # type: ignore
    def parent_children_local_to_world(self, pos: vec2) -> vec2:
        """
        Convert a parent children-local space position to world space.

        :param pos: Position in parent children-local space.
        :return: Position in world space.
        """
        return self.parent.children_local_to_world(pos, self._parent_anchor) if self.parent else pos # type: ignore
    # endregion
    
    # endregion
    
    # region OTHER
    
    def trigger_event(self, event: Event) -> PygameObject:
        """
        Trigger an event through the object's event manager.

        :param event: Event to trigger.
        :return: This object.
        """
        self.services.get_event_manager().trigger(event)
        return self

    def play_sound(self, sound: Sound | str, volume: float=1.0, loops: int = 0,
                   max_time: float = 0.0, fade_time: float = 0.0, category: str = "main"):
        self.services.get_sound_manager().play_sound(sound, volume, loops, max_time, fade_time, category)
    
    def play_animation(self, animation: Animation) -> PygameObject:
        """
        Queue an animation through the animation manager.

        :param animation: Animation to play.
        :return: This object.
        """
        self.services.get_animation_manager().play(animation)
        return self
    
    def quick_debug(self, name: str, value: Any, duration: float = 0.0) -> PygameObject:
        """
        Submit a quick-debug value through the debug manager.

        :param name: Debug entry name.
        :param value: Value to display.
        :param duration: Display duration in seconds, or zero for a single frame.
        :return: This object.
        """
        self.services.get_quick_debug_manager().quick_debug(name, value, duration)
        return self
    
    # endregion

    def _render_self(self, submit: Callable[[DrawCommand], Any]) -> PygameObject[R]:
        """
        Submit this object's renderer for drawing.

        :param submit: Callback that accepts draw commands.
        :return: This object.
        """
        self.renderer.render(
            submit,
            self.world_transform,
            self.layer,
            self.render_sub_layer,
            self.anchor,
            self.get_world_clip_area(),
        )  # type: ignore[arg-type]
        return self
    
    def _is_culled(self) -> bool:
        """
        Return whether the object is outside the camera's culling radius.

        :return: ``True`` when the object should be culled.
        """
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
    
    def render(self, submit: Callable[[DrawCommand], Any]) -> PygameObject[R]:
        """
        Submit this object and its children for rendering.

        :param submit: Callback that accepts draw commands.
        :return: This object.
        """
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

    def _update_self(self, dt: float) -> PygameObject[R]:
        """
        Dispatch the update hook to this object's behaviors.

        :param dt: Elapsed time in seconds since the previous update.
        :return: This object.
        """
        self.behaviors.on_update(dt)
        return self

    def update(self, dt: float = 0.0) -> PygameObject[R]:
        """
        Update behaviors, children, and the renderer.

        :param dt: Elapsed time in seconds since the previous update.
        :return: This object.
        """
        if not self.frozen:
            self.children.update(dt)
            if not self.has_flag(ObjectFlags.SKIP_UPDATE):
                self._update_self(dt)

        if self.renderer:
            self.renderer.update(dt)

        return self

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"PygameObject({id(self)})"
