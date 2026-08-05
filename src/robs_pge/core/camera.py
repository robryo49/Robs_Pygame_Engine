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
        
    def move(self, translation: vec2) -> "Camera":
        self.pos += translation
        return self
    
    def move_x(self, dx: float) -> "Camera":
        self.pos.x += dx
        return self
    
    def move_y(self, dy: float) -> "Camera":
        self.pos.y += dy
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
    
    # region Coordinates Conversion Methods
    
    # region Screen <-> Viewport
    
    def screen_to_viewport_pos(self, screen_pos: vec2) -> vec2:
        return self.display.screen_to_viewport_pos(screen_pos)
    
    def screen_to_viewport_vec(self, screen_vec: vec2) -> vec2:
        return self.display.screen_to_viewport_vec(screen_vec)
    
    def viewport_to_screen_pos(self, viewport_pos: vec2) -> vec2:
        return self.display.viewport_to_screen_pos(viewport_pos)
    
    def viewport_to_screen_vec(self, viewport_vec: vec2) -> vec2:
        return self.display.viewport_to_screen_vec(viewport_vec)
    
    # endregion
    
    # region Screen <-> World
    
    def screen_to_world_pos(self, screen_pos: vec2) -> vec2:
        viewport_pos = self.display.screen_to_viewport_pos(screen_pos)
        return self.viewport_to_world_pos(viewport_pos)
    
    def screen_to_world_vec(self, screen_vec: vec2) -> vec2:
        viewport_vec = self.display.screen_to_viewport_vec(screen_vec)
        return self.viewport_to_world_vec(viewport_vec)
    
    def world_to_screen_pos(self, world_pos: vec2) -> vec2:
        viewport_pos = self.world_to_viewport_pos(world_pos)
        return self.display.viewport_to_screen_pos(viewport_pos)
    
    def world_to_screen_vec(self, world_vec: vec2) -> vec2:
        viewport_vec = self.world_to_viewport_vec(world_vec)
        return self.display.viewport_to_screen_vec(viewport_vec)
    
    # endregion
    
    # region Screen <-> Camera
    
    def screen_to_camera_pos(self, screen_pos: vec2) -> vec2:
        viewport_pos = self.display.screen_to_viewport_pos(screen_pos)
        return self.viewport_to_camera_pos(viewport_pos)
    
    def screen_to_camera_vec(self, screen_vec: vec2) -> vec2:
        viewport_vec = self.display.screen_to_viewport_vec(screen_vec)
        return self.viewport_to_camera_vec(viewport_vec)
    
    def camera_to_screen_pos(self, camera_pos: vec2) -> vec2:
        viewport_pos = self.camera_to_viewport_pos(camera_pos)
        return self.display.viewport_to_screen_pos(viewport_pos)
    
    def camera_to_screen_vec(self, camera_vec: vec2) -> vec2:
        viewport_vec = self.camera_to_viewport_vec(camera_vec)
        return self.display.viewport_to_screen_vec(viewport_vec)
    
    # endregion
    
    # region Viewport <-> Camera
    
    def viewport_to_camera_pos(self, viewport_pos: vec2) -> vec2:
        return viewport_pos - self.viewport_center
    
    def viewport_to_camera_vec(self, viewport_vec: vec2) -> vec2:
        return viewport_vec
    
    def camera_to_viewport_pos(self, camera_pos: vec2) -> vec2:
        return camera_pos + self.viewport_center
    
    def camera_to_viewport_vec(self, camera_vec: vec2) -> vec2:
        return camera_vec
    
    # endregion
    
    # region Viewport <-> World
    
    def viewport_to_world_pos(self, viewport_pos: vec2) -> vec2:
        return self.camera_to_world_pos(self.viewport_to_camera_pos(viewport_pos))
    
    def viewport_to_world_vec(self, viewport_vec: vec2) -> vec2:
        return self.camera_to_world_vec(self.viewport_to_camera_vec(viewport_vec))
    
    def world_to_viewport_pos(self, world_pos: vec2) -> vec2:
        return self.camera_to_viewport_pos(self.world_to_camera_pos(world_pos))
    
    def world_to_viewport_vec(self, world_vec: vec2) -> vec2:
        return self.camera_to_viewport_vec(self.world_to_camera_vec(world_vec))
    
    # endregion
    
    # region Camera <-> World
    
    def camera_to_world_pos(self, camera_pos: vec2) -> vec2:
        return self.transform.apply_on_point(camera_pos)
    
    def camera_to_world_vec(self, camera_vec: vec2) -> vec2:
        return self.transform.apply_on_vec(camera_vec)
    
    def world_to_camera_pos(self, world_pos: vec2) -> vec2:
        return self.transform.apply_inverse_on_point(world_pos)
    
    def world_to_camera_vec(self, world_vec: vec2) -> vec2:
        return self.transform.apply_inverse_on_vec(world_vec)
    
    # endregion
    
    # endregion
    
    # endregion
    
    
    def update(self, dt: float) -> "Camera":
        return self
    
    def __repr__(self) -> str:
        return "Camera"