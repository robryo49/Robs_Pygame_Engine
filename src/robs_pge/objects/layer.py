"""Layer containers that group objects with a camera and optional physics."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Any, Optional, TYPE_CHECKING, cast

from .object_collection import ObjectCollection
from .object import PygameObject
from ..physics import PhysicsWorld
from ..events import EventManager
from ..rendering import DrawCommand
from ..utils import CoordinateSystem, vec2

if TYPE_CHECKING:
    from ..core import Camera
    from ..core.states.services_collection import ServicesCollection


class Layer:
    """A sorted collection of objects sharing a camera and optional physics world."""

    def __init__(self, name: str, layer_value: float, camera: Camera, services: ServicesCollection, interactable: bool = True, coordinate_system: Optional[CoordinateSystem] = None) -> None:
        """
        Initialize a layer with a camera, services, and interaction settings.

        :param name: Human-readable layer name used to derive the identifier.
        :param layer_value: Z-order value used to sort layers.
        :param camera: Camera used to view this layer.
        :param services: Services collection available to the layer.
        :param interactable: Whether input interaction is enabled for this layer.
        :param coordinate_system: Optional coordinate system, or ``None`` for the default.
        """
        self._id = name.lower().replace(" ", "_")
        self._layer_value = layer_value
        self._interactable = interactable
        
        self._services = services
        
        self._coordinate_system = coordinate_system or CoordinateSystem()
        self._camera: Camera = camera

        self._objects = ObjectCollection()

        self._physics_world: Optional[PhysicsWorld] = None

        super().__init__()
        
    # region PROPERTIES
    
    @property
    def id(self) -> str:
        """Return the normalized layer identifier."""
        return self._id
    
    @property
    def layer_value(self) -> float:
        """Return the z-order value used to sort layers."""
        return self._layer_value
    
    @property
    def camera(self) -> "Camera":
        """Return the camera used to view this layer."""
        return self._camera
    
    @property
    def interactable(self) -> bool:
        """Return whether input interaction is enabled for this layer."""
        return self._interactable
    
    @interactable.setter
    def interactable(self, value: bool) -> None:
        """
        Set whether input interaction is enabled for this layer.

        :param value: The new value.
        """
        self._interactable = value
    
    @property
    def objects(self) -> ObjectCollection:
        """Return the direct objects contained in this layer."""
        return self._objects
    
    @property
    def coordinate_system(self) -> CoordinateSystem:
        """Return the coordinate system used for this layer's local space."""
        return self._coordinate_system
    
    @property
    def event_manager(self) -> EventManager:
        """Return the event manager provided by the layer's services."""
        return self._services.get_event_manager()

    @property
    def physics_world(self) -> Optional[PhysicsWorld]:
        """Return the physics world for this layer, if enabled."""
        return self._physics_world

    @property
    def has_physics(self) -> bool:
        """Return whether this layer currently has a physics world."""
        return self._physics_world is not None

    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # region From Screen
    def screen_to_viewport_pos(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to viewport space.

        :param pos: Position in screen space.
        :return: Position in viewport space.
        """
        return self.camera.screen_to_viewport_pos(pos)
    def screen_to_viewport_vec(self, vec: vec2) -> vec2:
        """
        Convert a screen space vector to viewport space.

        :param vec: Vector in screen space.
        :return: Vector in viewport space.
        """
        return self.camera.screen_to_viewport_vec(vec)
    def screen_to_camera_pos(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to camera space.

        :param pos: Position in screen space.
        :return: Position in camera space.
        """
        return self.camera.screen_to_camera_pos(pos)
    def screen_to_camera_vec(self, vec: vec2) -> vec2:
        """
        Convert a screen space vector to camera space.

        :param vec: Vector in screen space.
        :return: Vector in camera space.
        """
        return self.camera.screen_to_camera_vec(vec)
    def screen_to_world_pos(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to world space.

        :param pos: Position in screen space.
        :return: Position in world space.
        """
        return self.camera.screen_to_world_pos(pos)
    def screen_to_world_vec(self, vec: vec2) -> vec2:
        """
        Convert a screen space vector to world space.

        :param vec: Vector in screen space.
        :return: Vector in world space.
        """
        return self.camera.screen_to_world_vec(vec)
    def screen_to_local_pos(self, pos: vec2) -> vec2:
        """
        Convert a screen space position to local space.

        :param pos: Position in screen space.
        :return: Position in local space.
        """
        return self.world_to_local_pos(self.screen_to_world_pos(pos))
    def screen_to_local_vec(self, vec: vec2) -> vec2:
        """
        Convert a screen space vector to local space.

        :param vec: Vector in screen space.
        :return: Vector in local space.
        """
        return self.world_to_local_vec(self.screen_to_world_vec(vec))
    # endregion
    
    # region From Viewport
    def viewport_to_screen_pos(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to screen space.

        :param pos: Position in viewport space.
        :return: Position in screen space.
        """
        return self.camera.viewport_to_screen_pos(pos)
    def viewport_to_screen_vec(self, vec: vec2) -> vec2:
        """
        Convert a viewport space vector to screen space.

        :param vec: Vector in viewport space.
        :return: Vector in screen space.
        """
        return self.camera.viewport_to_screen_vec(vec)
    def viewport_to_camera_pos(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to camera space.

        :param pos: Position in viewport space.
        :return: Position in camera space.
        """
        return self.camera.viewport_to_camera_pos(pos)
    def viewport_to_camera_vec(self, vec: vec2) -> vec2:
        """
        Convert a viewport space vector to camera space.

        :param vec: Vector in viewport space.
        :return: Vector in camera space.
        """
        return self.camera.viewport_to_camera_vec(vec)
    def viewport_to_world_pos(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to world space.

        :param pos: Position in viewport space.
        :return: Position in world space.
        """
        return self.camera.viewport_to_world_pos(pos)
    def viewport_to_world_vec(self, vec: vec2) -> vec2:
        """
        Convert a viewport space vector to world space.

        :param vec: Vector in viewport space.
        :return: Vector in world space.
        """
        return self.camera.viewport_to_world_vec(vec)
    def viewport_to_local_pos(self, pos: vec2) -> vec2:
        """
        Convert a viewport space position to local space.

        :param pos: Position in viewport space.
        :return: Position in local space.
        """
        return self.world_to_local_pos(self.viewport_to_world_pos(pos))
    def viewport_to_local_vec(self, vec: vec2) -> vec2:
        """
        Convert a viewport space vector to local space.

        :param vec: Vector in viewport space.
        :return: Vector in local space.
        """
        return self.world_to_local_vec(self.viewport_to_world_vec(vec))
    # endregion
    
    # region From Camera
    def camera_to_screen_pos(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to screen space.

        :param pos: Position in camera space.
        :return: Position in screen space.
        """
        return self.camera.camera_to_screen_pos(pos)
    def camera_to_screen_vec(self, vec: vec2) -> vec2:
        """
        Convert a camera space vector to screen space.

        :param vec: Vector in camera space.
        :return: Vector in screen space.
        """
        return self.camera.camera_to_screen_vec(vec)
    def camera_to_viewport_pos(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to viewport space.

        :param pos: Position in camera space.
        :return: Position in viewport space.
        """
        return self.camera.camera_to_viewport_pos(pos)
    def camera_to_viewport_vec(self, vec: vec2) -> vec2:
        """
        Convert a camera space vector to viewport space.

        :param vec: Vector in camera space.
        :return: Vector in viewport space.
        """
        return self.camera.camera_to_viewport_vec(vec)
    def camera_to_world_pos(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to world space.

        :param pos: Position in camera space.
        :return: Position in world space.
        """
        return self.camera.camera_to_world_pos(pos)
    def camera_to_world_vec(self, vec: vec2) -> vec2:
        """
        Convert a camera space vector to world space.

        :param vec: Vector in camera space.
        :return: Vector in world space.
        """
        return self.camera.camera_to_world_vec(vec)
    def camera_to_local_pos(self, pos: vec2) -> vec2:
        """
        Convert a camera space position to local space.

        :param pos: Position in camera space.
        :return: Position in local space.
        """
        return self.world_to_local_pos(self.camera_to_world_pos(pos))
    def camera_to_local_vec(self, vec: vec2) -> vec2:
        """
        Convert a camera space vector to local space.

        :param vec: Vector in camera space.
        :return: Vector in local space.
        """
        return self.world_to_local_vec(self.camera_to_world_vec(vec))
    # endregion
    
    # region From World
    def world_to_screen_pos(self, pos: vec2) -> vec2:
        """
        Convert a world space position to screen space.

        :param pos: Position in world space.
        :return: Position in screen space.
        """
        return self.camera.world_to_screen_pos(pos)
    def world_to_screen_vec(self, vec: vec2) -> vec2:
        """
        Convert a world space vector to screen space.

        :param vec: Vector in world space.
        :return: Vector in screen space.
        """
        return self.camera.world_to_screen_vec(vec)
    def world_to_viewport_pos(self, pos: vec2) -> vec2:
        """
        Convert a world space position to viewport space.

        :param pos: Position in world space.
        :return: Position in viewport space.
        """
        return self.camera.world_to_viewport_pos(pos)
    def world_to_viewport_vec(self, vec: vec2) -> vec2:
        """
        Convert a world space vector to viewport space.

        :param vec: Vector in world space.
        :return: Vector in viewport space.
        """
        return self.camera.world_to_viewport_vec(vec)
    def world_to_camera_pos(self, pos: vec2) -> vec2:
        """
        Convert a world space position to camera space.

        :param pos: Position in world space.
        :return: Position in camera space.
        """
        return self.camera.world_to_camera_pos(pos)
    def world_to_camera_vec(self, vec: vec2) -> vec2:
        """
        Convert a world space vector to camera space.

        :param vec: Vector in world space.
        :return: Vector in camera space.
        """
        return self.camera.world_to_camera_vec(vec)
    def world_to_local_pos(self, pos: vec2) -> vec2:
        """
        Convert a world space position to local space.

        :param pos: Position in world space.
        :return: Position in local space.
        """
        return self.coordinate_system.world_to_local_pos(pos)
    def world_to_local_vec(self, vec: vec2) -> vec2:
        """
        Convert a world space vector to local space.

        :param vec: Vector in world space.
        :return: Vector in local space.
        """
        return self.coordinate_system.world_to_local_vec(vec)
    # endregion
    
    # region From Local
    def local_to_screen_pos(self, pos: vec2) -> vec2:
        """
        Convert a local space position to screen space.

        :param pos: Position in local space.
        :return: Position in screen space.
        """
        return self.world_to_screen_pos(self.local_to_world_pos(pos))
    def local_to_screen_vec(self, vec: vec2) -> vec2:
        """
        Convert a local space vector to screen space.

        :param vec: Vector in local space.
        :return: Vector in screen space.
        """
        return self.world_to_screen_vec(self.local_to_world_vec(vec))
    def local_to_viewport_pos(self, pos: vec2) -> vec2:
        """
        Convert a local space position to viewport space.

        :param pos: Position in local space.
        :return: Position in viewport space.
        """
        return self.world_to_viewport_pos(self.local_to_world_pos(pos))
    def local_to_viewport_vec(self, vec: vec2) -> vec2:
        """
        Convert a local space vector to viewport space.

        :param vec: Vector in local space.
        :return: Vector in viewport space.
        """
        return self.world_to_viewport_vec(self.local_to_world_vec(vec))
    def local_to_camera_pos(self, pos: vec2) -> vec2:
        """
        Convert a local space position to camera space.

        :param pos: Position in local space.
        :return: Position in camera space.
        """
        return self.world_to_camera_pos(self.local_to_world_pos(pos))
    def local_to_camera_vec(self, vec: vec2) -> vec2:
        """
        Convert a local space vector to camera space.

        :param vec: Vector in local space.
        :return: Vector in camera space.
        """
        return self.world_to_camera_vec(self.local_to_world_vec(vec))
    def local_to_world_pos(self, pos: vec2) -> vec2:
        """
        Convert a local space position to world space.

        :param pos: Position in local space.
        :return: Position in world space.
        """
        return self.coordinate_system.local_to_world_pos(pos)
    def local_to_world_vec(self, vec: vec2) -> vec2:
        """
        Convert a local space vector to world space.

        :param vec: Vector in local space.
        :return: Vector in world space.
        """
        return self.coordinate_system.local_to_world_vec(vec)
    # endregion
    
    # endregion
    
    # region Object Management
    
    def add_object(self, *objects: PygameObject | Iterable[PygameObject]) -> Layer:
        """
        Queue objects for addition and attach them to this layer.

        :param objects: Objects or iterables of objects to add.
        :return: This layer.
        """
        flattened = list(self.objects.flatten_objects(objects))

        for obj in flattened:
            old_layer = obj.layer
            if old_layer is not None and old_layer is not self and obj in old_layer.objects:
                old_layer.remove_object(obj)

        self.objects.add_object(*flattened)

        for obj in flattened:
            obj.layer = self
            if self._physics_world and obj.has_physics and (body := obj.physics_body) is not None:
                self._physics_world.add_body(body)

        return self

    def remove_object(self, *objects: PygameObject | Iterable[PygameObject]) -> Layer:
        """
        Queue objects for removal and detach them from this layer.

        :param objects: Objects or iterables of objects to remove.
        :return: This layer.
        """
        flattened = list(self.objects.flatten_objects(objects))

        for obj in flattened:
            if self._physics_world and obj.has_physics and (body := obj.physics_body) is not None:
                self._physics_world.remove_body(body)
            if obj.layer is self:
                obj.layer = None

        self.objects.remove_object(*flattened)
        return self

    def get_partial_objects_count(self) -> int:
        """
        Return the number of direct objects in this layer.

        :return: Number of direct objects.
        """
        return self.objects.size

    def get_full_objects_count(self) -> int:
        """
        Return the number of objects including descendants.

        :return: Number of objects including all descendants.
        """
        return self.objects.full_size

    def get_objects_count(self) -> tuple[int, int]:
        """
        Return direct and full object counts.

        :return: A tuple of the direct count and the full count.
        """
        return self.get_partial_objects_count(), self.get_full_objects_count()
    
    # endregion
    
    # region State & Visibility Controls
    
    def freeze(self) -> Layer:
        """
        Prevent objects in this layer from updating or rendering.

        :return: This layer.
        """
        self.objects.freeze()
        return self

    def unfreeze(self) -> Layer:
        """
        Allow objects in this layer to update and render again.

        :return: This layer.
        """
        self.objects.unfreeze()
        return self

    def toggle_frozen(self) -> Layer:
        """
        Toggle the frozen state of this layer.

        :return: This layer.
        """
        self.objects.toggle_frozen()
        return self

    def enable_rendering(self) -> Layer:
        """
        Enable rendering for this layer.

        :return: This layer.
        """
        self.objects.enable_rendering()
        return self

    def disable_rendering(self) -> Layer:
        """
        Disable rendering for this layer.

        :return: This layer.
        """
        self.objects.disable_rendering()
        return self

    def toggle_rendering(self) -> Layer:
        """
        Toggle rendering for this layer.

        :return: This layer.
        """
        self.objects.toggle_rendering()
        return self
    
    # endregion
    
    # region Lifecycle Methods

    def update(self, dt: float) -> Layer:
        """
        Update contained objects and the physics world.

        :param dt: Elapsed time in seconds since the previous update.
        :return: This layer.
        """
        self.objects.update(dt)
        if self._physics_world:
            self._physics_world.update(dt)
        return self

    def render(self, submit: Callable[[DrawCommand], Any]) -> Layer:
        """
        Submit contained objects for rendering.

        :param submit: Callback that accepts draw commands.
        :return: This layer.
        """
        self.objects.render(submit)
        return self

    # endregion

    # region PHYSICS

    def enable_physics(self, gravity: vec2 = vec2(0, 980)) -> PhysicsWorld:
        """
        Enable physics for this layer and return its physics world.

        :param gravity: Gravity vector for the physics world.
        :return: The layer's physics world.
        """
        if self._physics_world is None:
            self._physics_world = PhysicsWorld(self, gravity=gravity)
            self._register_existing_bodies()
        return cast(PhysicsWorld, self._physics_world)

    def _register_existing_bodies(self) -> None:
        """Register physics bodies of existing layer objects with the physics world."""
        if not self._physics_world:
            return
        # noinspection protected-member
        self.objects._handle_object_additions()
        for obj in self.objects:
            if obj.has_physics:
                self._physics_world.add_body(obj.physics_body)

    def disable_physics(self) -> Layer:
        """
        Disable and clear this layer's physics world.

        :return: This layer.
        """
        if self._physics_world:
            self._physics_world.clear()
            self._physics_world = None
        return self

    # endregion
    
    def __iter__(self) -> Iterator[PygameObject]:
        """
        Iterate over direct objects in this layer.

        :return: Iterator over the layer's direct objects.
        """
        return iter(self.objects)
    
    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"Layer('{self._id}')"
    