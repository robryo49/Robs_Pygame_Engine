from typing import Any, Iterable, Optional, cast

from glm import vec2
from pygame import FRect
from pyglm import glm

from .functions import apply_transformation_matrix_on_point, apply_transformation_matrix_on_vec, get_inverse_transformation_matrix, get_transformation_matrix


class Transform:
    def __init__(self, pos: Optional[vec2] = None, rotation: float = 0, scale: float = 1):
        self._pos = pos or vec2()
        self._rotation = rotation
        self._scale = scale
        
        self._dirty = True
        self._matrix: Optional[glm.mat4] = None
        self._inverse_matrix: Optional[glm.mat4] = None
        
    # region PROPERTIES
    
    # region pos
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, value: vec2):
        self._pos = value
        self.mark_dirty()
    
    # region x_pos
    @property
    def x_pos(self):
        return self.pos.x
    
    @x_pos.setter
    def x_pos(self, value):
        self.pos.x = value
        self.mark_dirty()
    # endregion
    
    # region y_pos
    @property
    def y_pos(self):
        return self.pos.y
    
    @y_pos.setter
    def y_pos(self, value):
        self.pos.y = value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    # region rotation
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.mark_dirty()
    # endregion

    # region scale
    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def __add__(self, other: "Transform") -> "Transform":
        return Transform(self.pos + other.pos, self.rotation + other.rotation, self.scale * other.scale)
    
    def __sub__(self, other: "Transform") -> "Transform":
        return Transform(self.pos - other.pos, self.rotation - other.rotation, self.scale / other.scale)
    
    def __mul__(self, other: "Transform") -> "Transform":
        return Transform(self.apply_on_point(other.pos), self.rotation + other.rotation, self.scale * other.scale)
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Transform) and self.pos == other.pos and self.rotation == other.rotation and self.scale == other.scale
    
    def with_position(self, pos: vec2) -> "Transform":
        return Transform(pos, self.rotation, self.scale)
    
    def with_rotation(self, rotation: float) -> "Transform":
        return Transform(self.pos, rotation, self.scale)
    
    def with_scale(self, scale: float) -> "Transform":
        return Transform(self.pos, self.rotation, scale)
    
    def translate(self, vec: vec2) -> "Transform":
        self.pos += vec
        return self
        
    def rotate(self, angle: float) -> "Transform":
        self.rotation += angle
        return self
    
    def scale_by(self, factor: float) -> "Transform":
        self.scale *= factor
        return self
    
    def update_matrices(self):
        self._matrix = get_transformation_matrix(self.pos, -self.rotation, self.scale)
        self._inverse_matrix = get_inverse_transformation_matrix(self.pos, -self.rotation, self.scale)
        self._dirty = False
    
    def mark_dirty(self):
        self._dirty = True
    
    def get_matrix(self) -> glm.mat4:
        if self._dirty or self._matrix is None:
            self.update_matrices()
        return cast(glm.mat4, self._matrix)
    
    def get_inverse_matrix(self) -> glm.mat4:
        if self._dirty or self._inverse_matrix is None:
            self.update_matrices()
        return cast(glm.mat4, self._inverse_matrix)
    
    
    def apply_on_point(self, point: vec2) -> vec2:
        return apply_transformation_matrix_on_point(self.get_matrix(), point)
    
    def apply_on_vec(self, vec: vec2) -> vec2:
        return apply_transformation_matrix_on_vec(self.get_matrix(), vec)
    
    
    def apply_inverse_on_point(self, point: vec2) -> vec2:
        return apply_transformation_matrix_on_point(self.get_inverse_matrix(), point)
    
    def apply_inverse_on_vec(self, vec: vec2) -> vec2:
        return apply_transformation_matrix_on_vec(self.get_inverse_matrix(), vec)
    
    
    def apply_on_points(self, points: Iterable[vec2]) -> list[vec2]:
        m = self.get_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def apply_on_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        m = self.get_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
    
    def apply_inverse_on_points(self, points: Iterable[vec2]) -> list[vec2]:
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def apply_inverse_on_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
    def apply_on_rect(self, rect: FRect) -> Any:
        tl = vec2(rect.left, rect.top)
        tr = vec2(rect.right, rect.top)
        bl = vec2(rect.left, rect.bottom)
        br = vec2(rect.right, rect.bottom)
        
        t_points = self.apply_on_points((tl, tr, bl, br))
        
        min_x = min(p.x for p in t_points)
        max_x = max(p.x for p in t_points)
        min_y = min(p.y for p in t_points)
        max_y = max(p.y for p in t_points)
        
        return FRect(min_x, min_y, max_x - min_x, max_y - min_y)
    
    
    def apply_inverse_on_rect(self, rect: FRect) -> Any:
        tl = vec2(rect.left, rect.top)
        tr = vec2(rect.right, rect.top)
        bl = vec2(rect.left, rect.bottom)
        br = vec2(rect.right, rect.bottom)
        
        t_points = self.apply_inverse_on_points((tl, tr, bl, br))
        
        min_x = min(p.x for p in t_points)
        max_x = max(p.x for p in t_points)
        min_y = min(p.y for p in t_points)
        max_y = max(p.y for p in t_points)
        
        return FRect(min_x, min_y, max_x - min_x, max_y - min_y)
    