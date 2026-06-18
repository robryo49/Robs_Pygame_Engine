from dataclasses import dataclass, field
from enum import IntFlag, auto
from typing import Callable

from resources import Texture
from utils import Vec2, Transform, inf, Easing, Color


class FadingTypes(IntFlag):
    NONE = auto()
    SCALE = auto()


@dataclass
class Particle:
    transform: Transform
    vel: Vec2
    ang_vel: float
    
    gravity: Vec2
    
    life: float
    
    texture: Texture = None
    color: Color = None
    
    fade_duration: float = 0
    fade_easing: Callable[[float], float] = Easing.EASE_IN_QUAD
    fade_type: int = FadingTypes.NONE
    
    layer: int = inf
