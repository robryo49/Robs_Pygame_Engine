from dataclasses import dataclass
from math import cos, sin, radians, hypot
from typing import Optional, Union, cast

from .math_tools import vec2, Transform


@dataclass
class RectCollisionBox:
    center: vec2
    half_extents: vec2
    rotation: float = 0.0
    
    def get_axes(self) -> tuple[vec2, vec2]:
        rad = radians(self.rotation)
        x_axis = vec2(cos(rad), sin(rad))
        y_axis = vec2(-sin(rad), cos(rad))
        return x_axis, y_axis
    
    def get_corners(self) -> list[vec2]:
        x_axis, y_axis = self.get_axes()
        hx, hy = self.half_extents
        return [
            self.center + x_axis * hx + y_axis * hy,
            self.center - x_axis * hx + y_axis * hy,
            self.center - x_axis * hx - y_axis * hy,
            self.center + x_axis * hx - y_axis * hy,
            ]


@dataclass
class CircleCollisionBox:
    center: vec2
    radius: float


@dataclass
class CollisionBox:
    type: str  # "rect" or "circle"
    half_extents: Optional[vec2] = None
    radius: Optional[float] = None
    rotation_offset: float = 0.0
    
    def to_world_shape(self, world_pos: vec2, world_rotation: float, world_scale: float = 1.0) -> Union[RectCollisionBox, CircleCollisionBox]:
        if self.type == "circle" and self.radius is not None:
            return CircleCollisionBox(world_pos, self.radius * world_scale)
        elif self.type == "rect" and self.half_extents is not None:
            rotation = world_rotation + self.rotation_offset
            return RectCollisionBox(world_pos, self.half_extents * world_scale, rotation)
        raise ValueError(f"Cant create collision box of type {self.type} with dims {(self.half_extents.x, self.half_extents.y) if self.half_extents is not None else None} or radius {self.radius}")
    

def project_rect_onto_axis(corners: list[vec2], axis: vec2) -> tuple[float, float]:
    projections = [corner.dot(axis) for corner in corners]
    return min(projections), max(projections)


def test_intervals_overlap(a: tuple[float, float], b: tuple[float, float]) -> bool:
    a_min, a_max = a
    b_min, b_max = b
    return a_min <= b_max and b_min <= a_max


def test_collision_rect_rect(a: RectCollisionBox, b: RectCollisionBox) -> bool:
    a_axes = a.get_axes()
    b_axes = b.get_axes()
    
    a_corners = a.get_corners()
    b_corners = b.get_corners()
    
    for axis in (*a_axes, *b_axes):
        a_interval = project_rect_onto_axis(a_corners, axis)
        b_interval = project_rect_onto_axis(b_corners, axis)
        if not test_intervals_overlap(a_interval, b_interval):
            return False
    
    return True


def test_collision_circle_circle(a: CircleCollisionBox, b: CircleCollisionBox) -> bool:
    return hypot(*(a.center - b.center)) <= a.radius + b.radius


def test_collision_rect_circle(obb: RectCollisionBox, circle: CircleCollisionBox) -> bool:
    x_axis, y_axis = obb.get_axes()
    offset = circle.center - obb.center
    
    local_x = offset.dot(x_axis)
    local_y = offset.dot(y_axis)
    
    hx, hy = obb.half_extents
    clamped_x = max(-hx, min(hx, local_x))
    clamped_y = max(-hy, min(hy, local_y))
    
    dx = local_x - clamped_x
    dy = local_y - clamped_y
    
    return (dx * dx + dy * dy) <= circle.radius ** 2



def test_collision_box_overlap(box_a: CollisionBox, transform_a: Transform, box_b: CollisionBox, transform_b: Transform) -> bool:
    shape_a = box_a.to_world_shape(transform_a.pos, transform_a.rotation, transform_a.scale)
    shape_b = box_b.to_world_shape(transform_b.pos, transform_b.rotation, transform_b.scale)
    
    a_is_circle = isinstance(shape_a, CircleCollisionBox)
    b_is_circle = isinstance(shape_b, CircleCollisionBox)
    
    if a_is_circle and b_is_circle:
        return test_collision_circle_circle(cast(CircleCollisionBox, shape_a), cast(CircleCollisionBox, shape_b))
    if not a_is_circle and not b_is_circle:
        return test_collision_rect_rect(cast(RectCollisionBox, shape_a), cast(RectCollisionBox, shape_b))
    if a_is_circle:
        return test_collision_rect_circle(cast(RectCollisionBox, shape_a), cast(CircleCollisionBox, shape_a))
    return test_collision_rect_circle(cast(RectCollisionBox, shape_a), cast(CircleCollisionBox, shape_b))