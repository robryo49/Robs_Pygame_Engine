from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING, cast

from .object_collection import ObjectCollection
from .object import PygameObject
from ..physics import PhysicsWorld
from ..events import EventManager
from ..rendering import DrawCommand
from ..utils import CoordinateSystem, DictCollection, vec2

if TYPE_CHECKING:
    from ..core import Camera


class Layer:
    def __init__(self, name: str, layer_value: float, camera: Camera, services: DictCollection, interactable: bool = True, coordinate_system: Optional[CoordinateSystem] = None):
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
        return self._id
    
    @property
    def layer_value(self) -> float:
        return self._layer_value
    
    @property
    def camera(self) -> "Camera":
        return self._camera
    
    @property
    def interactable(self) -> bool:
        return self._interactable
    
    @interactable.setter
    def interactable(self, value: bool) -> None:
        self._interactable = value
    
    @property
    def objects(self) -> ObjectCollection:
        return self._objects
    
    @property
    def coordinate_system(self) -> CoordinateSystem:
        return self._coordinate_system
    
    @property
    def event_manager(self) -> EventManager:
        return cast(EventManager, self._services.get(EventManager))

    @property
    def physics_world(self) -> Optional[PhysicsWorld]:
        return self._physics_world

    @property
    def has_physics(self) -> bool:
        return self._physics_world is not None

    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # region From Screen
    def screen_to_viewport_pos(self, pos: vec2) -> vec2: return self.camera.screen_to_viewport_pos(pos)
    def screen_to_viewport_vec(self, vec: vec2) -> vec2: return self.camera.screen_to_viewport_vec(vec)
    def screen_to_camera_pos(self, pos: vec2) -> vec2: return self.camera.screen_to_camera_pos(pos)
    def screen_to_camera_vec(self, vec: vec2) -> vec2: return self.camera.screen_to_camera_vec(vec)
    def screen_to_world_pos(self, pos: vec2) -> vec2: return self.camera.screen_to_world_pos(pos)
    def screen_to_world_vec(self, vec: vec2) -> vec2: return self.camera.screen_to_world_vec(vec)
    def screen_to_local_pos(self, pos: vec2) -> vec2: return self.world_to_local_pos(self.screen_to_world_pos(pos))
    def screen_to_local_vec(self, vec: vec2) -> vec2: return self.world_to_local_vec(self.screen_to_world_vec(vec))
    # endregion
    
    # region From Viewport
    def viewport_to_screen_pos(self, pos: vec2) -> vec2: return self.camera.viewport_to_screen_pos(pos)
    def viewport_to_screen_vec(self, vec: vec2) -> vec2: return self.camera.viewport_to_screen_vec(vec)
    def viewport_to_camera_pos(self, pos: vec2) -> vec2: return self.camera.viewport_to_camera_pos(pos)
    def viewport_to_camera_vec(self, vec: vec2) -> vec2: return self.camera.viewport_to_camera_vec(vec)
    def viewport_to_world_pos(self, pos: vec2) -> vec2: return self.camera.viewport_to_world_pos(pos)
    def viewport_to_world_vec(self, vec: vec2) -> vec2: return self.camera.viewport_to_world_vec(vec)
    def viewport_to_local_pos(self, pos: vec2) -> vec2: return self.world_to_local_pos(self.viewport_to_world_pos(pos))
    def viewport_to_local_vec(self, vec: vec2) -> vec2: return self.world_to_local_vec(self.viewport_to_world_vec(vec))
    # endregion
    
    # region From Camera
    def camera_to_screen_pos(self, pos: vec2) -> vec2: return self.camera.camera_to_screen_pos(pos)
    def camera_to_screen_vec(self, vec: vec2) -> vec2: return self.camera.camera_to_screen_vec(vec)
    def camera_to_viewport_pos(self, pos: vec2) -> vec2: return self.camera.camera_to_viewport_pos(pos)
    def camera_to_viewport_vec(self, vec: vec2) -> vec2: return self.camera.camera_to_viewport_vec(vec)
    def camera_to_world_pos(self, pos: vec2) -> vec2: return self.camera.camera_to_world_pos(pos)
    def camera_to_world_vec(self, vec: vec2) -> vec2: return self.camera.camera_to_world_vec(vec)
    def camera_to_local_pos(self, pos: vec2) -> vec2: return self.world_to_local_pos(self.camera_to_world_pos(pos))
    def camera_to_local_vec(self, vec: vec2) -> vec2: return self.world_to_local_vec(self.camera_to_world_vec(vec))
    # endregion
    
    # region From World
    def world_to_screen_pos(self, pos: vec2) -> vec2: return self.camera.world_to_screen_pos(pos)
    def world_to_screen_vec(self, vec: vec2) -> vec2: return self.camera.world_to_screen_vec(vec)
    def world_to_viewport_pos(self, pos: vec2) -> vec2: return self.camera.world_to_viewport_pos(pos)
    def world_to_viewport_vec(self, vec: vec2) -> vec2: return self.camera.world_to_viewport_vec(vec)
    def world_to_camera_pos(self, pos: vec2) -> vec2: return self.camera.world_to_camera_pos(pos)
    def world_to_camera_vec(self, vec: vec2) -> vec2: return self.camera.world_to_camera_vec(vec)
    def world_to_local_pos(self, pos: vec2) -> vec2: return self.coordinate_system.world_to_local_pos(pos)
    def world_to_local_vec(self, vec: vec2) -> vec2: return self.coordinate_system.world_to_local_vec(vec)
    # endregion
    
    # region From Local
    def local_to_screen_pos(self, pos: vec2) -> vec2: return self.world_to_screen_pos(self.local_to_world_pos(pos))
    def local_to_screen_vec(self, vec: vec2) -> vec2: return self.world_to_screen_vec(self.local_to_world_vec(vec))
    def local_to_viewport_pos(self, pos: vec2) -> vec2: return self.world_to_viewport_pos(self.local_to_world_pos(pos))
    def local_to_viewport_vec(self, vec: vec2) -> vec2: return self.world_to_viewport_vec(self.local_to_world_vec(vec))
    def local_to_camera_pos(self, pos: vec2) -> vec2: return self.world_to_camera_pos(self.local_to_world_pos(pos))
    def local_to_camera_vec(self, vec: vec2) -> vec2: return self.world_to_camera_vec(self.local_to_world_vec(vec))
    def local_to_world_pos(self, pos: vec2) -> vec2: return self.coordinate_system.local_to_world_pos(pos)
    def local_to_world_vec(self, vec: vec2) -> vec2: return self.coordinate_system.local_to_world_vec(vec)
    # endregion
    
    # endregion
    
    # region Object Management
    
    def add_object(self, obj: PygameObject | Iterable[PygameObject]) -> None:
        self.objects.add_object(obj)
        for o in obj if isinstance(obj, Iterable) else [obj]:
            o.layer = self
            if self._physics_world and o.has_physics and (body := o.physics_body) is not None:
                self._physics_world.add_body(body)

    def remove_object(self, obj: PygameObject | Iterable[PygameObject]) -> None:
        for o in obj if isinstance(obj, Iterable) else [obj]:
            if self._physics_world and o.has_physics and (body := o.physics_body) is not None:
                self._physics_world.remove_body(body)
        self.objects.remove_object(obj)
        for o in obj if isinstance(obj, Iterable) else [obj]:
            o.layer = None
    
    # endregion
    
    # region State & Visibility Controls
    
    def freeze(self) -> None:
        self.objects.freeze()
    
    def unfreeze(self) -> None:
        self.objects.unfreeze()
    
    def toggle_frozen(self) -> None:
        self.objects.toggle_frozen()
    
    def enable_rendering(self) -> None:
        self.objects.enable_rendering()
    
    def disable_rendering(self) -> None:
        self.objects.disable_rendering()
    
    def toggle_rendering(self) -> None:
        self.objects.toggle_rendering()
    
    # endregion
    
    # region Lifecycle Methods

    def update(self, dt: float) -> Layer:
        self.objects.update(dt)
        if self._physics_world:
            self._physics_world.update(dt)
        return self

    def render(self, submit: Callable[[DrawCommand], Any]) -> Layer:
        self.objects.render(submit)
        return self

    # endregion

    # region PHYSICS

    def enable_physics(self, gravity: vec2 = vec2(0, 980)) -> PhysicsWorld:
        if self._physics_world is None:
            self._physics_world = PhysicsWorld(self, gravity=gravity)
            self._register_existing_bodies()
        return cast(PhysicsWorld, self._physics_world)

    def _register_existing_bodies(self):
        if not self._physics_world:
            return
        # noinspection protected-member
        self.objects._handle_object_additions()
        for obj in self.objects:
            if obj.has_physics:
                self._physics_world.add_body(obj.physics_body)

    def disable_physics(self):
        if self._physics_world:
            self._physics_world.clear()
            self._physics_world = None

    # endregion
    
    def __iter__(self):
        return iter(self.objects)
    
    def __repr__(self) -> str:
        return f"Layer('{self._id}')"
    