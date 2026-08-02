from dataclasses import dataclass
from enum import IntFlag, auto
from typing import Optional

from ...resources import Texture
from ...utils import Color, Easing, EasingFunctionType, Transform, Vec2


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
    
    texture: Optional[Texture] = None
    color: Optional[Color] = None
    
    fade_duration: float = 0
    fade_easing: EasingFunctionType = Easing.EASE_IN_QUAD
    fade_type: int = FadingTypes.NONE
    
    layer: int = 0
