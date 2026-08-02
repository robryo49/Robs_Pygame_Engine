import operator
from dataclasses import dataclass, field
from random import random as rand

from pygame import Vector2 as Vec2, Vector3 as Vec3, Rect, FRect, Color
from math import cos, sin, pi, log10, inf


def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, mini=0.0, maxi=1.0):
    return min(maxi, max(x, mini))


def round_sig(x: float, digits: int) -> float:
    if x == 0:
        return 0.0
    return round(x, digits - 1 - int(log10(abs(x))))


def invert_y(vec: Vec2):
    return Vec2(vec.x, -vec.y)

def invert_uv_y(uv: Vec2):
    return Vec2(uv.x, 1-uv.y)


def invert_x(vec: Vec2):
    return Vec2(-vec.x, vec.y)

def invert_uv_x(uv: Vec2):
    return Vec2(1-uv.x, uv.y)

def rotated_surface_dims(dims: Vec2, rotation: float):
    return Vec2(
        abs(dims.x * cos(rotation*pi/180)) + abs(dims.y * sin(rotation*pi/180)),
        abs(dims.y * cos(rotation*pi/180)) + abs(dims.x * sin(rotation*pi/180))
    )


def surface_pos_from_pixel_pos(pixel_pos: Vec2, dims: Vec2, rotation: float=0):
    if rotation:
        return ((pixel_pos - dims/2).rotate(-rotation) + rotated_surface_dims(dims, rotation) / 2).elementwise()
    else:
        return pixel_pos


def surface_pos_from_uv_pos(uv: Vec2, dims: Vec2, rotation: float=0):
    return surface_pos_from_pixel_pos(uv.elementwise() * dims, dims, rotation)

def random(a, b):
    return rand() * (b - a) + a


@dataclass
class Transform:
    pos: Vec2 = field(default_factory=lambda: Vec2())
    rotation: float = 0
    scale: float = 1
    
    def translate(self, vec: Vec2):
        self.pos += vec
        
    def rotate(self, angle: float):
        self.rotation += angle
        
    def scale_by(self, factor: float):
        self.scale *= factor
    
    def __add__(self, other: "Transform"):
        return Transform(self.pos + other.pos, self.rotation + other.rotation, self.scale * other.scale)
    
    def __sub__(self, other: "Transform"):
        return Transform(self.pos - other.pos, self.rotation - other.rotation, self.scale / other.scale)
    
    def __mul__(self, other: "Transform"):
        return Transform(self.apply(other.pos), self.rotation + other.rotation, self.scale * other.scale)
        
    
    def __round__(self, n=0):
        return Transform(self.pos, round(self.rotation, n), round(self.scale, n))

    def __eq__(self, other: "Transform"):
        return self.pos == other.pos and self.rotation == other.rotation and self.scale == other.scale
    
    def apply(self, point: Vec2) -> Vec2:
        return (point * self.scale).rotate(self.rotation) + self.pos
    
    def apply_on_rect(self, rect: FRect):
        corners = [
            self.apply(Vec2(rect.left, rect.top)),
            self.apply(Vec2(rect.right, rect.top)),
            self.apply(Vec2(rect.right, rect.bottom)),
            self.apply(Vec2(rect.left, rect.bottom)),
        ]
        xs = [c.x for c in corners]
        ys = [c.y for c in corners]
        
        return FRect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    
    def apply_inverse(self, point):
        return (point - self.pos).rotate(-self.rotation) / self.scale


class Easing:
    JUMP = lambda x: int(clamp(x))
    LINEAR = lambda x: x
    
    EASE_IN_SINE = lambda x: (1 - cos((x * pi) / 2))
    EASE_OUT_SINE = lambda x: (sin((x * pi) / 2))
    EASE_IN_OUT_SINE = lambda x: (-(cos(pi * x) - 1) / 2)
    EASE_IN_QUAD = lambda x: (x**2)
    EASE_OUT_QUAD = lambda x: (1 - (1 - x) * (1 - x))
    EASE_IN_OUT_QUAD = lambda x: (2 * x**2 if x < 0.5 else 1 - (-2 * x + 2)**2 / 2)
    EASE_IN_CUBIC = lambda x: (x**3)
    EASE_OUT_CUBIC = lambda x: (1 - (1 - x)**3)
    EASE_IN_OUT_CUBIC = lambda x: (4 * x**3 if x < 0.5 else 1 - (-2 * x + 2)**3 / 2)
    EASE_IN_QUART = lambda x: (x**4)
    EASE_OUT_QUART = lambda x: (1 - (1 - x)**4)
    EASE_IN_OUT_QUART = lambda x: (8 * x**4 if x < 0.5 else 1 - (-2 * x + 2)**4 / 2)
    EASE_IN_QUINT = lambda x: (x**4 * x)
    EASE_OUT_QUINT = lambda x: (1 - (1 - x)**5)
    EASE_IN_OUT_QUINT = lambda x: (16 * x**4 * x if x < 0.5 else 1 - (-2 * x + 2)**5 / 2)
    EASE_IN_BACK = lambda x: (2.70158 * x**3 - 1.70158 * x**2)
    EASE_OUT_BACK = lambda x: (1 + 2.70158 * (x - 1)**3 + 1.70158 * (x - 1)**2)
    EASE_IN_OUT_BACK = lambda x: (((2 * x)**2 * (3.59491 * 2 * x - 2.59491)) / 2 if x < 0.5 else ((2 * x - 2)**2 * (3.59491 * (x * 2 - 2) + 2.59491) + 2) / 2)
    EASE_IN_ELASTIC = lambda x: (0 if x == 0 else 1 if x == 1 else -(2**(10 * x - 10)) * sin((x * 10 - 10.75) * ((2 * pi) / 3)) if x < 0.5 else (2**(-10 * x + 10)) * sin((x * 10 - 10.75) * ((2 * pi) / 3)) + 1)
    EASE_OUT_ELASTIC = lambda x: (0 if x == 0 else 1 if x == 1 else (2**(-10 * x)) * sin((x * 10 - 0.75) * ((2 * pi) / 3)) + 1)
    EASE_IN_OUT_ELASTIC = lambda x: (0 if x == 0 else 1 if x == 1 else (-(2**(20 * x - 10)) * sin((20 * x - 11.125) * ((2 * pi) / 4.5))) / 2 if x < 0.5 else ((2**(-20 * x + 10)) * sin((20 * x - 11.125) * ((2 * pi) / 4.5))) / 2 + 1)


class Anchor:
    TL =    Vec2(0,     0)
    T =     Vec2(0.5,   0)
    TR =    Vec2(1,     0)
    L =     Vec2(0,     0.5)
    C =     Vec2(0.5,   0.5)
    R =     Vec2(1,     0.5)
    BL =    Vec2(0,     1)
    B =     Vec2(0.5,   1)
    BR =    Vec2(1,     1)
    

class ScreenAnchor:
    TL =    Vec2(0,     0)
    T =     Vec2(0.5,   0)
    TR =    Vec2(1,     0)
    L =     Vec2(0,     0.5)
    C =     Vec2(0.5,   0.5)
    R =     Vec2(1,     0.5)
    BL =    Vec2(0,     1)
    B =     Vec2(0.5,   1)
    BR =    Vec2(1,     1)
    
    @staticmethod
    def set_screen_dims(dims: Vec2):
        ScreenAnchor.TL =    Vec2(0,     0).elementwise() * dims
        ScreenAnchor.T =     Vec2(0.5,   0).elementwise() * dims
        ScreenAnchor.TR =    Vec2(1,     0).elementwise() * dims
        ScreenAnchor.L =     Vec2(0,     0.5).elementwise() * dims
        ScreenAnchor.C =     Vec2(0.5,   0.5).elementwise() * dims
        ScreenAnchor.R =     Vec2(1,     0.5).elementwise() * dims
        ScreenAnchor.BL =    Vec2(0,     1).elementwise() * dims
        ScreenAnchor.B =     Vec2(0.5,   1).elementwise() * dims
        ScreenAnchor.BR =    Vec2(1,     1).elementwise() * dims
    


# region GENERIC ARITHMETIC

def _is_color(value) -> bool:
    return isinstance(value, Color)

def _is_math_iterable(value) -> bool:
    return isinstance(value, (Color, Vec2, Vec3, tuple, list))

def _clamp_channel(value: float) -> int:
    return max(0, min(255, int(round(value))))

def _cast(blueprint, values, clamp_color=True):
    vals = list(values)
    
    if _is_color(blueprint):
        if clamp_color:
            return Color(*[_clamp_channel(v) for v in vals][:4])
        return tuple(vals)
    
    if isinstance(blueprint, (Vec2, Vec3)):
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

# endregion
