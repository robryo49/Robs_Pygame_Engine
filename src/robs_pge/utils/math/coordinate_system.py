"""Coordinate frame with conversion helpers between local and world space."""

from dataclasses import dataclass, field
from typing import Any, Iterable, cast
from pyglm import glm
from glm import vec2

from .functions import apply_transformation_matrix_on_vec, apply_transformation_matrix_on_point


@dataclass
class CoordinateSystem:
    """Coordinate frame defined by an origin, x axis, and y axis."""

    origin: vec2 = field(default_factory=lambda: vec2(0, 0))
    x_axis: vec2 = field(default_factory=lambda: vec2(1, 0))
    y_axis: vec2 = field(default_factory=lambda: vec2(0, 1))
    
    def __eq__(self, other: Any) -> bool:
        """Return whether both coordinate systems share the same origin and axes.

        :param other: Object to compare against.
        :return: ``True`` when ``other`` is a coordinate system with identical fields.
        """
        return isinstance(other, CoordinateSystem) and self.origin == other.origin and self.x_axis == other.x_axis and self.y_axis == other.y_axis
    
    def get_matrix(self) -> glm.mat4:
        """Build a matrix that transforms local coordinates into world coordinates.

        :return: The local-to-world transformation matrix.
        """
        return glm.mat4(
            self.x_axis.x, self.x_axis.y, 0.0, 0.0,
            self.y_axis.x, self.y_axis.y, 0.0, 0.0,
            0.0,           0.0,           1.0, 0.0,
            self.origin.x, self.origin.y, 0.0, 1.0
        )
    
    def get_inverse_matrix(self) -> glm.mat4:
        """Build the inverse of the local-to-world matrix.

        :return: The world-to-local transformation matrix.
        """
        return cast(glm.mat4, cast(object, glm.inverse(self.get_matrix())))
    
    
    def local_to_world_pos(self, point: vec2) -> vec2:
        """Transform a local position into world space.

        :param point: Local-space position.
        :return: The position in world space.
        """
        return apply_transformation_matrix_on_point(self.get_matrix(), point)
    
    def local_to_world_positions(self, points: Iterable[vec2]) -> list[vec2]:
        """Transform multiple local positions into world space.

        :param points: Local-space positions.
        :return: The positions in world space.
        """
        m = self.get_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def local_to_world_vec(self, vec: vec2) -> vec2:
        """Transform a local direction vector into world space.

        :param vec: Local-space direction vector.
        :return: The direction vector in world space.
        """
        return apply_transformation_matrix_on_vec(self.get_matrix(), vec)
    
    def local_to_world_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        """Transform multiple local direction vectors into world space.

        :param vecs: Local-space direction vectors.
        :return: The direction vectors in world space.
        """
        m = self.get_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
    
    def world_to_local_pos(self, point: vec2) -> vec2:
        """Transform a world position into local space.

        :param point: World-space position.
        :return: The position in local space.
        """
        return apply_transformation_matrix_on_point(self.get_inverse_matrix(), point)
    
    def world_to_local_positions(self, points: Iterable[vec2]) -> list[vec2]:
        """Transform multiple world positions into local space.

        :param points: World-space positions.
        :return: The positions in local space.
        """
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def world_to_local_vec(self, vec: vec2) -> vec2:
        """Transform a world direction vector into local space.

        :param vec: World-space direction vector.
        :return: The direction vector in local space.
        """
        return apply_transformation_matrix_on_vec(self.get_inverse_matrix(), vec)
    
    def world_to_local_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        """Transform multiple world direction vectors into local space.

        :param vecs: World-space direction vectors.
        :return: The direction vectors in local space.
        """
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
