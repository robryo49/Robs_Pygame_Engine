from typing import Optional

from .display import Display
from ..utils import FRect, Transform, Vec2, invert_y, Vec2Like


class Camera:
    def __init__(self, display: Display):
        
        self._display: Display = display
        
        self._display_dims: Vec2 = display.dims
        self._display_center: Vec2 = display.dims * 0.5
        
        self._transform: Transform = Transform()
        
        self._world_aabb: FRect = self._get_world_aabb()

    # region PROPERTIES
    
    @property
    def display(self) -> Display:
        return self._display
    
    @property
    def transform(self) -> Transform:
        return self._transform
    
    # region pos
    @property
    def pos(self) -> Vec2:
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: Vec2Like) -> None:
        self.transform.pos = Vec2(value)
        
    def move(self, value: Vec2Like) -> "Camera":
        self.pos += Vec2(value)
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
    def zoom(self, value: float) -> None:
        self.transform.scale = 1/value
    
    def zoom_in(self, fact: float, point: Optional[Vec2]) -> "Camera":
        if point is not None: self.pos = point - (point - self.pos) / fact
        self.zoom *= fact
        return self
    
    def zoom_out(self, fact: float, point: Optional[Vec2]) -> "Camera":
        if point is not None: self.pos = point - (point - self.pos) * fact
        self.zoom /= fact
        return self
    # endregion

    @property
    def display_dims(self) -> Vec2:
        return self._display_dims
    
    @property
    def display_width(self) -> float:
        return self.display_dims.x
    
    @property
    def display_height(self) -> float:
        return self.display_dims.y
    
    @property
    def display_center(self) -> Vec2:
        return self._display_center
    
    @property
    def world_aabb(self) -> FRect:
        return self._world_aabb
    
    @property
    def up(self) -> Vec2:
        return Vec2(0, 1).rotate(self.rotation) * self.transform.scale
    
    @property
    def right(self) -> Vec2:
        return Vec2(1, 0).rotate(self.rotation) * self.transform.scale
    
    @property
    def down(self) -> Vec2:
        return Vec2(0, -1).rotate(self.rotation) * self.transform.scale
    
    @property
    def left(self) -> Vec2:
        return Vec2(-1, 0).rotate(self.rotation) * self.transform.scale
    
    @property
    def top_left(self):
        return self.world_aabb.bottomleft
    
    @property
    def top_right(self):
        return self.world_aabb.bottomright
    
    @property
    def bottom_left(self):
        return self.world_aabb.topleft
    
    @property
    def bottom_right(self):
        return self.world_aabb.topright
    
    # endregion
    
    def _get_world_aabb(self) -> FRect:
        w, h = self.display_dims
        half = Vec2(w, h) / (2 * self.zoom)
        
        return FRect(
            self.pos.x - half.x,
            self.pos.y - half.y,
            half.x * 2,
            half.y * 2
        )
    
    def world_to_screen_pos(self, world_pos: Vec2) -> Vec2:
        x, y = self.transform.apply_inverse(world_pos) + self.display_center
        return Vec2(x, self.display_height - y)
    
    def screen_to_world_pos(self, screen_pos: Vec2) -> Vec2:
        y = self.display_height - screen_pos.y
        return self.transform.apply(Vec2(screen_pos.x, y) - self.display_center)
    
    def world_to_screen_vec(self, vec: Vec2) -> Vec2:
        return invert_y(vec) / self.transform.scale
    
    def screen_to_world_vec(self, vec: Vec2) -> Vec2:
        return invert_y(vec) * self.transform.scale
    
    
    def update(self, dt: float) -> "Camera":
        self._world_aabb = self._get_world_aabb()
        return self
    
    def __repr__(self) -> str:
        return "Camera"