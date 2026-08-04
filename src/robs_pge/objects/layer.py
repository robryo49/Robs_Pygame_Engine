from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Callable, Any

from .object_collection import ObjectCollection
from ..rendering import DrawCommand
from ..utils import ObjectLikeType, CoordinateSystem, Vec2, FRect

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
    def id(self):
        return self._id
    
    @property
    def layer_value(self):
        return self._layer_value
    
    @property
    def camera(self):
        return self._camera
    
    @property
    def interactable(self):
        return self._interactable
    
    @interactable.setter
    def interactable(self, value: bool):
        self._interactable = value
        
    @property
    def objects(self):
        return self._objects
    
    @property
    def coordinate_system(self):
        return self._coordinate_system
    
    # endregion
    
    def get_camera_world_aabb(self) -> FRect:
        corners = [
            Vec2(self.camera.top_left),
            Vec2(self.camera.top_right),
            Vec2(self.camera.bottom_left),
            Vec2(self.camera.bottom_right)
        ]
        
        world_corners = [self.camera_to_world_pos(corner) for corner in corners]
        
        min_x = min(corner.x for corner in world_corners)
        max_x = max(corner.x for corner in world_corners)
        min_y = min(corner.y for corner in world_corners)
        max_y = max(corner.y for corner in world_corners)
        
        return FRect(min_x, min_y, max_x - min_x, max_y - min_y)
    
    # region Coordinates Conversion Methods
    
    def screen_to_camera_pos(self, screen_point: Vec2):
        return self.camera.screen_to_camera_pos(screen_point)
    
    def screen_to_camera_vec(self, screen_vec: Vec2):
        return self.camera.screen_to_camera_vec(screen_vec)
    
    
    def screen_to_world_pos(self, screen_point: Vec2):
        return self.camera_to_world_pos(self.screen_to_camera_pos(screen_point))
    
    def screen_to_world_vec(self, screen_vec: Vec2):
        return self.camera_to_world_vec(self.screen_to_camera_vec(screen_vec))
    
    
    
    def world_to_camera_pos(self, world_point: Vec2):
        return (world_point.x - self.coordinate_system.origin.x) * self.coordinate_system.x_axis + (world_point.y - self.coordinate_system.origin.y) * self.coordinate_system.y_axis

    def world_to_camera_vec(self, world_vec: Vec2):
        return world_vec.x * self.coordinate_system.x_axis + world_vec.y * self.coordinate_system.y_axis
    
    
    def world_to_screen_pos(self, world_point: Vec2):
        return self.camera_to_screen_pos(self.world_to_camera_pos(world_point))

    def world_to_screen_vec(self, world_vec: Vec2):
        return self.camera_to_screen_vec(self.world_to_camera_vec(world_vec))
    
    
    
    def camera_to_screen_pos(self, camera_point: Vec2):
        return self.camera.camera_to_screen_pos(camera_point)

    def camera_to_screen_vec(self, camera_vec: Vec2):
        return self.camera.camera_to_screen_vec(camera_vec)
    
    
    def camera_to_world_pos(self, camera_point: Vec2):
        local_point = camera_point - self.coordinate_system.origin
    
        a1, a2 = self.coordinate_system.x_axis.x, self.coordinate_system.x_axis.y
        b1, b2 = self.coordinate_system.y_axis.x, self.coordinate_system.y_axis.y
        c1, c2 = local_point.x, local_point.y
        
        det = a1 * b2 - a2 * b1
        if det == 0:
            raise ValueError("Basis vectors are collinear and cannot form a coordinate system!")
        
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        
        return Vec2(x, y)

    def camera_to_world_vec(self, camera_vec: Vec2):
        return Vec2(camera_vec.dot(self.coordinate_system.x_axis), camera_vec.dot(self.coordinate_system.y_axis))
    
    # endregion
    
    def freeze(self):
        self.objects.freeze()
    
    def unfreeze(self):
        self.objects.unfreeze()
        
    def toggle_frozen(self):
        self.objects.toggle_frozen()
        
        
    def enable_rendering(self):
        self.objects.enable_rendering()
        
    def disable_rendering(self):
        self.objects.disable_rendering()
        
    def toggle_rendering(self):
        self.objects.toggle_rendering()
        
    
    def add_object(self, obj: ObjectLikeType | list[ObjectLikeType]):
        self.objects.add_object(obj)
        
        if isinstance(obj, list):
            for o in obj:
                o.layer = self
        else:
            obj.layer = self
        
    def remove_object(self, obj: ObjectLikeType | list[ObjectLikeType]):
        self.objects.remove_object(obj)
        
        if isinstance(obj, list):
            for o in obj:
                o.layer = None
    
    def render(self, submit: Callable[[DrawCommand], Any]) -> "Layer":
        self.objects.render(submit)
        return self
    
    def update(self, dt: float) -> "Layer":
        self.objects.update(dt)
        return self
    
    def __iter__(self):
        return self.objects.__iter__()
    
    def __repr__(self):
        return f"Layer('{self._id}', z={self._layer_value})"