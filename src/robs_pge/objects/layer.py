from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .object_collection import ObjectCollection
from ..rendering import DrawCommand
from ..utils import CoordinateSystem, vec2, ObjectLikeType

if TYPE_CHECKING:
    from ..core import Camera


class Layer:
    def __init__(self, name: str, layer_value: float, camera: Camera, interactable: bool = True, coordinate_system: Optional[CoordinateSystem] = None):
        self._id = name.lower().replace(" ", "_")
        self._layer_value = layer_value
        self._interactable = interactable
        
        self._coordinate_system = coordinate_system or CoordinateSystem()
        self._camera: Camera = camera
        
        self._objects = ObjectCollection()
        
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
    
    # endregion
    
    # region Coordinates Conversion Methods
    
    # region Screen <-> World
    
    def screen_to_world_pos(self, screen_pos: vec2) -> vec2:
        return self.camera.screen_to_world_pos(screen_pos)
    
    def screen_to_world_vec(self, screen_vec: vec2) -> vec2:
        return self.camera.screen_to_world_vec(screen_vec)
    
    def world_to_screen_pos(self, world_pos: vec2) -> vec2:
        return self.camera.world_to_screen_pos(world_pos)
    
    def world_to_screen_vec(self, world_vec: vec2) -> vec2:
        return self.camera.world_to_screen_vec(world_vec)
    
    # endregion
    
    
    # region Viewport <-> World
    
    def viewport_to_world_pos(self, viewport_pos: vec2) -> vec2:
        return self.camera.viewport_to_world_pos(viewport_pos)
    
    def viewport_to_world_vec(self, viewport_vec: vec2) -> vec2:
        return self.camera.viewport_to_world_vec(viewport_vec)
    
    def world_to_viewport_pos(self, world_pos: vec2) -> vec2:
        return self.camera.world_to_viewport_pos(world_pos)
    
    def world_to_viewport_vec(self, world_vec: vec2) -> vec2:
        return self.camera.world_to_viewport_vec(world_vec)
    
    # endregion
    
    
    # region Camera <-> World
    
    def camera_to_world_pos(self, camera_pos: vec2) -> vec2:
        return self.camera.camera_to_world_pos(camera_pos)
    
    def camera_to_world_vec(self, camera_vec: vec2) -> vec2:
        return self.camera.camera_to_world_vec(camera_vec)
    
    def world_to_camera_pos(self, world_pos: vec2) -> vec2:
        return self.camera.world_to_camera_pos(world_pos)
    
    def world_to_camera_vec(self, world_vec: vec2) -> vec2:
        return self.camera.world_to_camera_vec(world_vec)
    
    # endregion
    
    
    # region World <-> Local
    
    def world_to_local_pos(self, world_pos: vec2) -> vec2:
        return self.coordinate_system.world_to_local_pos(world_pos)
    
    def world_to_local_vec(self, world_vec: vec2) -> vec2:
        return self.coordinate_system.world_to_local_vec(world_vec)
    
    def local_to_world_pos(self, local_pos: vec2) -> vec2:
        return self.coordinate_system.local_to_world_pos(local_pos)
    
    def local_to_world_vec(self, local_vec: vec2) -> vec2:
        return self.coordinate_system.local_to_world_vec(local_vec)
    
    # endregion
    
    
    # region Camera <-> Local
    
    def camera_to_local_pos(self, camera_pos: vec2) -> vec2:
        world_pos = self.camera_to_world_pos(camera_pos)
        return self.world_to_local_pos(world_pos)
    
    def camera_to_local_vec(self, camera_vec: vec2) -> vec2:
        world_vec = self.camera_to_world_vec(camera_vec)
        return self.world_to_local_vec(world_vec)
    
    def local_to_camera_pos(self, local_pos: vec2) -> vec2:
        world_pos = self.local_to_world_pos(local_pos)
        return self.world_to_camera_pos(world_pos)
    
    def local_to_camera_vec(self, local_vec: vec2) -> vec2:
        world_vec = self.local_to_world_vec(local_vec)
        return self.world_to_camera_vec(world_vec)
    
    # endregion
    
    
    # region Viewport <-> Local
    
    def viewport_to_local_pos(self, viewport_pos: vec2) -> vec2:
        world_pos = self.viewport_to_world_pos(viewport_pos)
        return self.world_to_local_pos(world_pos)
    
    def viewport_to_local_vec(self, viewport_vec: vec2) -> vec2:
        world_vec = self.viewport_to_world_vec(viewport_vec)
        return self.world_to_local_vec(world_vec)
    
    def local_to_viewport_pos(self, local_pos: vec2) -> vec2:
        world_pos = self.local_to_world_pos(local_pos)
        return self.world_to_viewport_pos(world_pos)
    
    def local_to_viewport_vec(self, local_vec: vec2) -> vec2:
        world_vec = self.local_to_world_vec(local_vec)
        return self.world_to_viewport_vec(world_vec)
    
    # endregion
    
    
    # region Screen <-> Local
    
    def screen_to_local_pos(self, screen_pos: vec2) -> vec2:
        world_pos = self.screen_to_world_pos(screen_pos)
        return self.world_to_local_pos(world_pos)
    
    def screen_to_local_vec(self, screen_vec: vec2) -> vec2:
        world_vec = self.screen_to_world_vec(screen_vec)
        return self.world_to_local_vec(world_vec)
    
    def local_to_screen_pos(self, local_pos: vec2) -> vec2:
        world_pos = self.local_to_world_pos(local_pos)
        return self.world_to_screen_pos(world_pos)
    
    def local_to_screen_vec(self, local_vec: vec2) -> vec2:
        world_vec = self.local_to_world_vec(local_vec)
        return self.world_to_screen_vec(world_vec)
    
    # endregion
    
    # endregion
    
    # region Object Management
    
    def add_object(self, obj: ObjectLikeType | list[ObjectLikeType]) -> None:
        self.objects.add_object(obj)
        targets = obj if isinstance(obj, (list, tuple)) else [obj]
        for o in targets:
            o.layer = self
    
    def remove_object(self, obj: ObjectLikeType | list[ObjectLikeType]) -> None:
        self.objects.remove_object(obj)
        targets = obj if isinstance(obj, (list, tuple)) else [obj]
        for o in targets:
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
        return self
    
    def render(self, submit: Callable[[DrawCommand], Any]) -> Layer:
        self.objects.render(submit)
        return self
    
    # endregion
    
    def __iter__(self):
        return iter(self.objects)
    
    def __repr__(self) -> str:
        return f"Layer('{self._id}')"
    