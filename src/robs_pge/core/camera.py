from typing import Optional

from pyglm import glm

from .display import Display
from ..utils import FRect, Transform, rotate, vec2


class Camera:
    def __init__(self, display: Display):
        
        self._display: Display = display
        
        self._display_dims: vec2 = display.viewport_dims
        self._display_center: vec2 = display.viewport_dims * 0.5
        
        self._transform: Transform = Transform()
        
        self._min_zoom: Optional[float] = None
        self._max_zoom: Optional[float] = None

        self._cached_bounding_radius: float = 0.0
        self._cached_bounding_radius_squared: float = 0.0
        self._bounding_radius_dirty: bool = True

    # region PROPERTIES
    
    @property
    def display(self) -> Display:
        return self._display
    
    @property
    def transform(self) -> Transform:
        return self._transform
    
    # region dimensions
    
    @property
    def screen_dims(self):
        return self.display.screen_dims
    
    @property
    def screen_width(self):
        return self.display.screen_width
    
    @property
    def screen_height(self):
        return self.display.screen_height
    
    @property
    def screen_center_x(self):
        return self.display.screen_center_x
    
    @property
    def screen_center_y(self):
        return self.display.screen_center_y
    
    @property
    def screen_center(self):
        return self.display.screen_center
    
    
    
    @property
    def viewport_dims(self):
        return self.display.viewport_dims
    
    @property
    def viewport_width(self):
        return self.display.viewport_width
    
    @property
    def viewport_height(self):
        return self.display.viewport_height
    
    @property
    def viewport_center_x(self):
        return self.display.viewport_center_x
    
    @property
    def viewport_center_y(self):
        return self.display.viewport_center_y
    
    @property
    def viewport_center(self):
        return self.display.viewport_center
    
    # endregion
    
    # region pos
    @property
    def pos(self) -> vec2:
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: vec2) -> None:
        self.transform.pos = value
        
    # region x_pos
    @property
    def x_pos(self):
        return self.transform.x_pos
    
    @x_pos.setter
    def x_pos(self, value):
        self.transform.x_pos = value
    # endregion
    
    # region y_pos
    @property
    def y_pos(self):
        return self.transform.y_pos
    
    @y_pos.setter
    def y_pos(self, value):
        self.transform.y_pos = value
    # endregion
        
    def move(self, translation: vec2) -> "Camera":
        self.pos += translation
        return self
    
    def move_x(self, dx: float) -> "Camera":
        self.x_pos += dx
        return self
    
    def move_y(self, dy: float) -> "Camera":
        self.y_pos += dy
        return self
    # endregion
        
    # region rotation
    @property
    def rotation(self) -> float:
        return self.transform.rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        self.transform.rotation = value
        
    def rotate(self, value: float) -> "Camera":
        self.rotation += value
        return self
    # endregion
    
    # region zoom
    @property
    def zoom(self) -> float:
        return 1/self.transform.scale
    
    @zoom.setter
    def zoom(self, value: float | int) -> None:
        max_zoom = self.max_zoom
        min_zoom = self.min_zoom
        if max_zoom is not None and value > max_zoom:
            value = max_zoom
        if min_zoom is not None and value < min_zoom:
            value = min_zoom
        self.transform.scale = 1 / value
        self._invalidate_bounding_radius()
    
    def zoom_in(self, fact: float, point: Optional[vec2]=None) -> "Camera":
        prev = self.zoom
        self.zoom *= fact
        fact = prev / self.zoom
        if point is not None: self.pos = point - (point - self.pos) * fact
        return self
    
    def zoom_out(self, fact: float, point: Optional[vec2]=None) -> "Camera":
        prev = self.zoom
        self.zoom /= fact
        fact = prev / self.zoom
        if point is not None: self.pos = point - (point - self.pos) * fact
        return self
    # endregion
    
    # region min_zoom
    @property
    def min_zoom(self):
        return self._min_zoom
    
    @min_zoom.setter
    def min_zoom(self, value):
        self._min_zoom = value
    # endregion
    
    # region max_zoom
    @property
    def max_zoom(self):
        return self._max_zoom
    
    @max_zoom.setter
    def max_zoom(self, value):
        self._max_zoom = value
    # endregion
    
    @property
    def bounding_radius(self) -> float:
        if self._bounding_radius_dirty:
            self._cached_bounding_radius = glm.length(self.viewport_dims * self.transform.scale) * 0.5
            self._cached_bounding_radius_squared = self._cached_bounding_radius ** 2
            self._bounding_radius_dirty = False
        return self._cached_bounding_radius

    def _invalidate_bounding_radius(self):
        self._bounding_radius_dirty = True
        
    @property
    def bounding_radius_squared(self):
        return self._cached_bounding_radius_squared

    @property
    def up(self) -> vec2:
        return self.transform.apply_on_vec(vec2(0, -1))
    
    @property
    def right(self) -> vec2:
        return self.transform.apply_on_vec(vec2(1, 0))
    
    @property
    def down(self) -> vec2:
        return self.transform.apply_on_vec(vec2(0, 1))
    
    @property
    def left(self) -> vec2:
        return self.transform.apply_on_vec(vec2(-1, 0))
    
    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # region From Screen
    def screen_to_viewport_pos(self, pos: vec2) -> vec2: return self.display.screen_to_viewport_pos(pos)
    def screen_to_viewport_vec(self, vec: vec2) -> vec2: return self.display.screen_to_viewport_vec(vec)
    def screen_to_camera_pos(self, pos: vec2) -> vec2: return self.viewport_to_camera_pos(self.screen_to_viewport_pos(pos))
    def screen_to_camera_vec(self, vec: vec2) -> vec2: return self.viewport_to_camera_vec(self.screen_to_viewport_vec(vec))
    def screen_to_world_pos(self, pos: vec2) -> vec2: return self.viewport_to_world_pos(self.screen_to_viewport_pos(pos))
    def screen_to_world_vec(self, vec: vec2) -> vec2: return self.viewport_to_world_vec(self.screen_to_viewport_vec(vec))
    # endregion
    
    # region From Viewport
    def viewport_to_screen_pos(self, pos: vec2) -> vec2: return self.display.viewport_to_screen_pos(pos)
    def viewport_to_screen_vec(self, vec: vec2) -> vec2: return self.display.viewport_to_screen_vec(vec)
    def viewport_to_camera_pos(self, pos: vec2) -> vec2: return pos - self.viewport_center
    def viewport_to_camera_vec(self, vec: vec2) -> vec2: return vec
    def viewport_to_world_pos(self, pos: vec2) -> vec2: return self.camera_to_world_pos(self.viewport_to_camera_pos(pos))
    def viewport_to_world_vec(self, vec: vec2) -> vec2: return self.camera_to_world_vec(self.viewport_to_camera_vec(vec))
    # endregion
    
    # region From Camera
    def camera_to_screen_pos(self, pos: vec2) -> vec2: return self.display.viewport_to_screen_pos(self.camera_to_viewport_pos(pos))
    def camera_to_screen_vec(self, vec: vec2) -> vec2: return self.display.viewport_to_screen_vec(self.camera_to_viewport_vec(vec))
    def camera_to_viewport_pos(self, pos: vec2) -> vec2: return pos + self.viewport_center
    def camera_to_viewport_vec(self, vec: vec2) -> vec2: return vec
    def camera_to_world_pos(self, pos: vec2) -> vec2: return self.transform.apply_on_point(pos)
    def camera_to_world_vec(self, vec: vec2) -> vec2: return self.transform.apply_on_vec(vec)
    # endregion
    
    # region From World
    def world_to_screen_pos(self, pos: vec2) -> vec2: return self.display.viewport_to_screen_pos(self.world_to_viewport_pos(pos))
    def world_to_screen_vec(self, vec: vec2) -> vec2: return self.display.viewport_to_screen_vec(self.world_to_viewport_vec(vec))
    def world_to_viewport_pos(self, pos: vec2) -> vec2: return self.camera_to_viewport_pos(self.world_to_camera_pos(pos))
    def world_to_viewport_vec(self, vec: vec2) -> vec2: return self.camera_to_viewport_vec(self.world_to_camera_vec(vec))
    def world_to_camera_pos(self, pos: vec2) -> vec2: return self.transform.apply_inverse_on_point(pos)
    def world_to_camera_vec(self, vec: vec2) -> vec2: return self.transform.apply_inverse_on_vec(vec)
    # endregion
    
    # endregion
    
    # endregion
    
    
    def update(self, dt: float) -> "Camera":
        return self
    
    def __repr__(self) -> str:
        return "Camera"