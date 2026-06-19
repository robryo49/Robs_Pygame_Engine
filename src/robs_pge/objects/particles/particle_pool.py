from dataclasses import dataclass
from typing import Callable

import numpy as np

from .particle import FadingTypes
from ...resources import Texture
from ...utils import inf, Easing, Color


@dataclass
class ParticlePool:
    positions: np.ndarray
    velocities: np.ndarray
    gravity: np.ndarray
    rotations: np.ndarray
    angular_speeds: np.ndarray
    sizes: np.ndarray
    lifetimes: np.ndarray
    
    texture: Texture
    color: Color = None
    
    fade_duration: float = 0
    fade_easing: Callable[[float], float] = Easing.EASE_IN_QUAD
    fade_type: int = FadingTypes.NONE
    
    layer: int = inf
    
    def update(self, dt):
        self.lifetimes -= dt
        alive = self.lifetimes > 0
        
        self.velocities = self.velocities[alive] + self.gravity * dt
        self.positions = self.positions[alive] + self.velocities * dt
        self.angular_speeds = self.angular_speeds[alive]
        self.rotations = self.rotations[alive] + self.angular_speeds * dt
        self.lifetimes = self.lifetimes[alive]

