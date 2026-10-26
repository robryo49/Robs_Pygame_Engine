"""Position, rotation, and scale transform with cached conversion matrices."""

from typing import Any, Iterable, Optional, cast

from glm import vec2
from pygame import FRect
from pyglm import glm

from .functions import apply_transformation_matrix_on_point, apply_transformation_matrix_on_vec, get_inverse_transformation_matrix, get_transformation_matrix


class Transform:
    """Position, rotation, and uniform scale with cached forward and inverse matrices."""

    def __init__(self, pos: Optional[vec2] = None, rotation: float = 0, scale: float = 1) -> None:
        """Create a transform.

        :param pos: Translation offset, defaulting to the origin.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        """
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
        """Return the translation offset."""
        return self._pos
    
    @pos.setter
    def pos(self, value: vec2):
        """Set the translation offset and invalidate cached matrices.

        :param value: New translation offset.
        """
        self._pos = value
        self.mark_dirty()
    
    # region x_pos
    @property
    def x_pos(self):
        """Return the x component of the translation offset."""
        return self.pos.x
    
    @x_pos.setter
    def x_pos(self, value):
        """Set the x component of the translation offset and invalidate cached matrices.

        :param value: New x offset.
        """
        self.pos.x = value
        self.mark_dirty()
    # endregion
    
    # region y_pos
    @property
    def y_pos(self):
        """Return the y component of the translation offset."""
        return self.pos.y
    
    @y_pos.setter
    def y_pos(self, value):
        """Set the y component of the translation offset and invalidate cached matrices.

        :param value: New y offset.
        """
        self.pos.y = value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    # region rotation
    @property
    def rotation(self):
        """Return the rotation angle in degrees."""
        return self._rotation
    
    @rotation.setter
    def rotation(self, value):
        """Set the rotation angle and invalidate cached matrices.

        :param value: New rotation angle in degrees.
        """
        self._rotation = value
        self.mark_dirty()
    # endregion

    # region scale
    @property
    def scale(self):
        """Return the uniform scale factor."""
        return self._scale

    @scale.setter
    def scale(self, value):
        """Set the uniform scale factor and invalidate cached matrices.

        :param value: New scale factor.
        """
        self._scale = value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def __add__(self, other: "Transform") -> "Transform":
        """Return a transform whose components are combined with another transform.

        :param other: Transform to add.
        :return: A transform with added positions and rotations and multiplied scales.
        """
        return Transform(self.pos + other.pos, self.rotation + other.rotation, self.scale * other.scale)
    
    def __sub__(self, other: "Transform") -> "Transform":
        """Return a transform formed by subtracting another transform's components.

        :param other: Transform to subtract.
        :return: A transform with subtracted positions and rotations and divided scales.
        """
        return Transform(self.pos - other.pos, self.rotation - other.rotation, self.scale / other.scale)
    
    def __mul__(self, other: "Transform") -> "Transform":
        """Compose this transform with another transform.

        :param other: Transform to compose with.
        :return: A transform that applies this transform to ``other``'s position and combines their
            rotation and scale.
        """
        return Transform(self.apply_on_point(other.pos), self.rotation + other.rotation, self.scale * other.scale)
    
    def __eq__(self, other: Any) -> bool:
        """Return whether both transforms have equal position, rotation, and scale.

        :param other: Object to compare against.
        :return: ``True`` when ``other`` is a transform with identical fields.
        """
        return isinstance(other, Transform) and self.pos == other.pos and self.rotation == other.rotation and self.scale == other.scale
    
    def with_position(self, pos: vec2) -> "Transform":
        """Return a copy with a different position.

        :param pos: Position for the new transform.
        :return: A new transform using the given position.
        """
        return Transform(pos, self.rotation, self.scale)
    
    def with_rotation(self, rotation: float) -> "Transform":
        """Return a copy with a different rotation.

        :param rotation: Rotation angle in degrees for the new transform.
        :return: A new transform using the given rotation.
        """
        return Transform(self.pos, rotation, self.scale)
    
    def with_scale(self, scale: float) -> "Transform":
        """Return a copy with a different scale.

        :param scale: Scale factor for the new transform.
        :return: A new transform using the given scale.
        """
        return Transform(self.pos, self.rotation, scale)
    
    def translate(self, vec: vec2) -> "Transform":
        """Move the transform by an offset.

        :param vec: Translation offset to add.
        :return: This transform for chained calls.
        """
        self.pos += vec
        return self
        
    def rotate(self, angle: float) -> "Transform":
        """Rotate the transform by an additional angle.

        :param angle: Rotation offset in degrees.
        :return: This transform for chained calls.
        """
        self.rotation += angle
        return self
    
    def scale_by(self, factor: float) -> "Transform":
        """Multiply the transform's scale by a factor.

        :param factor: Scale multiplier.
        :return: This transform for chained calls.
        """
        self.scale *= factor
        return self
    
    def update_matrices(self):
        """Recompute the cached forward and inverse matrices from the current fields."""
        self._matrix = get_transformation_matrix(self.pos, -self.rotation, self.scale)
        self._inverse_matrix = get_inverse_transformation_matrix(self.pos, -self.rotation, self.scale)
        self._dirty = False
    
    def mark_dirty(self):
        """Mark the cached matrices as stale so they are recomputed on next access."""
        self._dirty = True
    
    def get_matrix(self) -> glm.mat4:
        """Return the transform's local-to-world matrix, recomputing it when stale.

        :return: The forward transformation matrix.
        """
        if self._dirty or self._matrix is None:
            self.update_matrices()
        return cast(glm.mat4, self._matrix)
    
    def get_inverse_matrix(self) -> glm.mat4:
        """Return the transform's world-to-local matrix, recomputing it when stale.

        :return: The inverse transformation matrix.
        """
        if self._dirty or self._inverse_matrix is None:
            self.update_matrices()
        return cast(glm.mat4, self._inverse_matrix)
    
    
    def apply_on_point(self, point: vec2) -> vec2:
        """Transform a point by this transform's matrix.

        :param point: Point to transform.
        :return: The transformed point.
        """
        return apply_transformation_matrix_on_point(self.get_matrix(), point)
    
    def apply_on_vec(self, vec: vec2) -> vec2:
        """Transform a direction vector by this transform's matrix.

        :param vec: Direction vector to transform.
        :return: The transformed direction vector.
        """
        return apply_transformation_matrix_on_vec(self.get_matrix(), vec)
    
    
    def apply_inverse_on_point(self, point: vec2) -> vec2:
        """Transform a point by this transform's inverse matrix.

        :param point: Point to transform.
        :return: The inverse-transformed point.
        """
        return apply_transformation_matrix_on_point(self.get_inverse_matrix(), point)
    
    def apply_inverse_on_vec(self, vec: vec2) -> vec2:
        """Transform a direction vector by this transform's inverse matrix.

        :param vec: Direction vector to transform.
        :return: The inverse-transformed direction vector.
        """
        return apply_transformation_matrix_on_vec(self.get_inverse_matrix(), vec)
    
    
    def apply_on_points(self, points: Iterable[vec2]) -> list[vec2]:
        """Transform multiple points by this transform's matrix.

        :param points: Points to transform.
        :return: The transformed points.
        """
        m = self.get_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def apply_on_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        """Transform multiple direction vectors by this transform's matrix.

        :param vecs: Direction vectors to transform.
        :return: The transformed direction vectors.
        """
        m = self.get_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
    
    def apply_inverse_on_points(self, points: Iterable[vec2]) -> list[vec2]:
        """Transform multiple points by this transform's inverse matrix.

        :param points: Points to transform.
        :return: The inverse-transformed points.
        """
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_point(m, p) for p in points]
    
    def apply_inverse_on_vecs(self, vecs: Iterable[vec2]) -> list[vec2]:
        """Transform multiple direction vectors by this transform's inverse matrix.

        :param vecs: Direction vectors to transform.
        :return: The inverse-transformed direction vectors.
        """
        m = self.get_inverse_matrix()
        return [apply_transformation_matrix_on_vec(m, v) for v in vecs]
    
    def apply_on_rect(self, rect: FRect) -> Any:
        """Transform a rectangle and return its axis-aligned bounding box.

        :param rect: Rectangle to transform.
        :return: The transformed rectangle's bounding box.
        """
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
        """Inverse-transform a rectangle and return its axis-aligned bounding box.

        :param rect: Rectangle to transform.
        :return: The inverse-transformed rectangle's bounding box.
        """
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
    