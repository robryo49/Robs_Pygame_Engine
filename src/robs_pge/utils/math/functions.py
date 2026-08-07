import operator
from math import cos, pi, sin
from random import random as rand
from typing import cast

from glm import vec1, vec2, vec3, vec4
from pygame import Color
from pyglm import glm


def lerp[T](a: T, b: T, t: float) -> T:
    if isinstance(a, Color) and isinstance(b, Color):
        return Color(
            int(a.r + (b.r - a.r) * t),
            int(a.g + (b.g - a.g) * t),
            int(a.b + (b.b - a.b) * t),
            int(a.a + (b.a - a.a) * t)
        )
    return glm.lerp(a, b, t)

def clamp[T](v: T, mini: float=0, maxi: float=1) -> T:
    return glm.clamp(v, mini, maxi)

def round_sig(x: float, digits: int) -> float:
    if x == 0:
        return 0.0
    return round(x, digits - 1 - int(glm.log(abs(x))))


def invert_y(vec: vec2):
    return vec2(vec.x, -vec.y)

def invert_uv_y(uv: vec2):
    return vec2(uv.x, 1-uv.y)

def invert_x(vec: vec2):
    return vec2(-vec.x, vec.y)

def invert_uv_x(uv: vec2):
    return vec2(1-uv.x, uv.y)


def rotated_surface_dims(dims: vec2, rotation: float):
    return vec2(
        abs(dims.x * cos(rotation*pi/180)) + abs(dims.y * sin(rotation*pi/180)),
        abs(dims.y * cos(rotation*pi/180)) + abs(dims.x * sin(rotation*pi/180))
    )


def surface_pos_from_pixel_pos(pixel_pos: vec2, dims: vec2, rotation: float=0):
    if rotation:
        return rotate(pixel_pos - dims/2, -rotation) + rotated_surface_dims(dims, rotation) / 2
    else:
        return pixel_pos

def surface_pos_from_uv_pos(uv_pos: vec2, dims: vec2, rotation: float=0):
    return surface_pos_from_pixel_pos(uv_pos*dims, dims, rotation)


def random[T](a: T = 0.0, b: T = 1.0) -> T:
    return a + rand() * (b - a)


def rotate(vec: vec2, angle_degrees: float) -> vec2:
    return rotate_rad(vec, glm.radians(angle_degrees))

def rotate_rad(vec: vec2, angle_rad: float) -> vec2:
    return glm.rotateZ(vec3(vec.x, vec.y, 0), angle_rad).xy

def length(v) -> float:
    return glm.length(v)


def get_transformation_matrix(translation: vec2, rotation: float, scale: float) -> glm.mat4:
    mat = glm.mat4(1.0)
    mat = glm.translate(mat, glm.vec3(translation.x, translation.y, 0.0))
    mat = glm.rotate(mat, glm.radians(rotation), glm.vec3(0.0, 0.0, 1.0))
    mat = glm.scale(mat, glm.vec3(scale, scale, 1.0))
    return mat

def get_inverse_transformation_matrix(translation: vec2, rotation: float, scale: float) -> glm.mat4:
    return cast(glm.mat4, cast(object, glm.inverse(get_transformation_matrix(translation, rotation, scale))))

def apply_transformation_matrix_on_point(mat: glm.mat4, point: vec2):
    return cast(vec4, cast(object, mat * vec4(point.x, point.y, 0, 1))).xy

def apply_transformation_matrix_on_vec(mat: glm.mat4, vec: vec2):
    return cast(vec4, cast(object, mat * vec4(vec.x, vec.y, 0, 0))).xy


def _is_color(value) -> bool:
    return isinstance(value, Color)

def _is_math_iterable(value) -> bool:
    return isinstance(value, (Color, vec1, vec2, vec3, vec4, tuple, list))

def _clamp_channel(value: float) -> int:
    return max(0, min(255, int(round(value))))

def _cast(blueprint, values, clamp_color=True):
    vals = list(values)
    
    if _is_color(blueprint):
        if clamp_color:
            return Color(*[_clamp_channel(v) for v in vals][:4])
        return tuple(vals)
    
    if isinstance(blueprint, (vec1, vec2, vec3, vec4)):
        return type(blueprint)(*vals[:len(blueprint)])
    
    if isinstance(blueprint, (tuple, list)):
        return type(blueprint)(vals)
    
    return vals

def _universal_op(a, b, op, clamp_color=True):
    a_is_iter = _is_math_iterable(a)
    b_is_iter = _is_math_iterable(b)
    
    if a_is_iter and b_is_iter:
        blueprint = a if _is_color(a) else (b if _is_color(b) else a)
        return _cast(blueprint, (op(v1, v2) for v1, v2 in zip(a, b)), clamp_color)
    
    if a_is_iter and isinstance(b, (int, float)):
        return _cast(a, (op(v, b) for v in a), clamp_color)
    
    if isinstance(a, (int, float)) and b_is_iter:
        return _cast(b, (op(a, v) for v in b), clamp_color)
    
    return op(a, b)


def add(a, b):
    return _universal_op(a, b, operator.add, clamp_color=True)

def subtract(a, b):
    is_delta = _is_math_iterable(a) and _is_math_iterable(b)
    return _universal_op(a, b, operator.sub, clamp_color=not is_delta)

def multiply(a, b):
    return _universal_op(a, b, operator.mul, clamp_color=True)

def divide(a, b):
    if isinstance(b, (int, float)) and b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return _universal_op(a, b, operator.truediv, clamp_color=True)

def power(a, b):
    return _universal_op(a, b, operator.pow, clamp_color=True)

