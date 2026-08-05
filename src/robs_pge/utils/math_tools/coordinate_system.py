from dataclasses import dataclass, field
from typing import Any, Iterable, cast
from pyglm import glm
from glm import vec2

from .functions import apply_transformation_matrix_on_vec, apply_transformation_matrix_on_point


@dataclass
class CoordinateSystem:
    origin: vec2 = field(default_factory=lambda: vec2(0, 0))
    x_axis: vec2 = field(default_factory=lambda: vec2(1, 0))
    y_axis: vec2 = field(default_factory=lambda: vec2(0, 1))
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CoordinateSystem) and self.origin == other.origin and self.x_axis == other.x_axis and self.y_axis == other.y_axis
    
    def get_matrix(self) -> glm.mat4:
        return glm.mat4(
            self.x_axis.x, self.x_axis.y, 0.0, 0.0,
            self.y_axis.x, self.y_axis.y, 0.0, 0.0,
            0.0,           0.0,           1.0, 0.0,
            self.origin.x, self.origin.y, 0.0, 1.0
        )
    
    def get_inverse_matrix(self) -> glm.mat4:
        return cast(glm.mat4, cast(object, glm.inverse(self.get_matrix())))
    
    
    def local_to_world_pos(self, point: vec2) -> vec2:
        return apply_transformation_matrix_on_point(self.get_matrix(), point)
    
    def local_to_world_positions(self, points: Iterable[vec2]) -> list[vec2]:
        m = self.get_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def local_to_world_vec(self, vec: vec2) -> vec2:
        return apply_transformation_matrix_on_vec(self.get_matrix(), vec)
    
    def local_to_world_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        m = self.get_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
    
    def world_to_local_pos(self, point: vec2) -> vec2:
        return apply_transformation_matrix_on_point(self.get_inverse_matrix(), point)
    
    def world_to_local_positions(self, points: Iterable[vec2]) -> list[vec2]:
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def world_to_local_vec(self, vec: vec2) -> vec2:
        return apply_transformation_matrix_on_vec(self.get_inverse_matrix(), vec)
    
    def world_to_local_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
