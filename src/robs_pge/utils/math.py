from dataclasses import dataclass, field
from random import random as rand
from pygame import Vector2 as Vec2, Vector3 as Vec3, Rect, FRect
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
    return Vec2(vec.x, -vec.y)

def invert_uv_x(uv: Vec2):
    return Vec2(uv.x, 1-uv.y)


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
    
    def apply(self, point: Vec2):
        return (point * self.scale).rotate(self.rotation) + self.pos
    
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
    C =     Vec2(0.5,   0.5)
    L =     Vec2(0,     0.5)
    TL =    Vec2(0,     1)
    T =     Vec2(0.5,   1)
    TR =    Vec2(1,     1)
    R =     Vec2(1,     0.5)
    BR =    Vec2(1,     0)
    B =     Vec2(0.5,   0)
    BL =    Vec2(0,     0)
