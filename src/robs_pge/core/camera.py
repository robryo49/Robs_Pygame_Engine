from typing import Optional

from .display import Display
from ..utils import FRect, Transform, Vec2, invert_y


class Camera:
    def __init__(self, display: Display):
        
        self._display = display
        
        self._display_dims = display.dims
        self._display_center = display.dims * 0.5
        
        self._transform = Transform(Vec2())
        
        self._world_aabb = self._get_world_aabb()

    # region PROPERTIES
    
    @property
    def display(self):
        return self._display
    
    @property
    def transform(self):
        return self._transform
    
    # region pos
    @property
    def pos(self):
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: Vec2):
        self.transform.pos = value
        
    def move(self, value):
        self.pos += value
    
    def move_x(self, dx):
        self.pos.x += dx
    
    def move_y(self, dy):
        self.pos.y += dy
    # endregion
        
    # region rotation
    @property
    def rotation(self):
        return self.transform.rotation
    
    @rotation.setter
    def rotation(self, value: float):
        self.transform.rotation = value
        
    def rotate(self, value: float):
        self.rotation += value
    # endregion
    
    # region zoom
    @property
    def zoom(self):
        return 1/self.transform.scale
    
    @zoom.setter
    def zoom(self, value: float):
        self.transform.scale = 1/value
    # endregion

    @property
    def display_dims(self):
        return self._display_dims
    
    @property
    def display_width(self):
        return self.display_dims.x
    
    @property
    def display_height(self):
        return self.display_dims.y
    
    @property
    def display_center(self):
        return self._display_center
    
    @property
    def world_aabb(self):
        return self._world_aabb
    
    @property
    def up(self):
        return Vec2(0, 1).rotate(self.rotation) * self.transform.scale
    
    @property
    def right(self):
        return Vec2(1, 0).rotate(self.rotation) * self.transform.scale
    
    @property
    def down(self):
        return Vec2(0, -1).rotate(self.rotation) * self.transform.scale
    
    @property
    def left(self):
        return Vec2(-1, 0).rotate(self.rotation) * self.transform.scale
    
    # endregion
    
    def _get_world_aabb(self):
        w, h = self.display_dims
        half = Vec2(w, h) / (2 * self.zoom)
        
        return FRect(
            self.pos.x - half.x,
            self.pos.y - half.y,
            half.x * 2,
            half.y * 2
        )
    
    def zoom_in(self, fact: float, point: Optional[Vec2]):
        if point is not None: self.pos = point - (point - self.pos) / fact
        self.zoom *= fact
    
    def zoom_out(self, fact: float, point: Optional[Vec2]):
        if point is not None: self.pos = point - (point - self.pos) * fact
        self.zoom /= fact
    
    def world_to_screen_pos(self, world_pos: Vec2):
        x, y = self.transform.apply_inverse(world_pos) + self.display_center
        return Vec2(x, self.display_height - y)
    
    def screen_to_world_pos(self, screen_pos: Vec2):
        y = self.display_height - screen_pos.y
        return self.transform.apply(Vec2(screen_pos.x, y) - self.display_center)
    
    def world_to_screen_vec(self, vec: Vec2):
        return invert_y(vec) / self.transform.scale
    
    def screen_to_world_vec(self, vec: Vec2):
        return invert_y(vec) * self.transform.scale
    
    def update(self, dt: float):
        self._world_aabb = self._get_world_aabb()
    
    def __str__(self):
        return "Camera"