from dataclasses import dataclass, field
from typing import Any, Iterable

from glm import vec2
from pyglm import glm
from pygame import FRect

from .functions import apply_transformation_matrix_on_point, apply_transformation_matrix_on_vec, get_inverse_transformation_matrix, get_transformation_matrix


@dataclass
class Transform:
    pos: vec2 = field(default_factory=lambda : vec2())
    rotation: float = 0
    scale: float = 1
    
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
    

    def get_matrix(self) -> glm.mat4:
        return get_transformation_matrix(self.pos, -self.rotation, self.scale)
    
    def get_inverse_matrix(self) -> glm.mat4:
        return get_inverse_transformation_matrix(self.pos, -self.rotation, self.scale)
    
    
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
    