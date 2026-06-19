from random import randrange
from typing import Callable, Optional

import numpy as np

from ...resources import Texture
from ...utils import Color, Colors, Vec2, random
from .particle import FadingTypes
from .particle_system import ParticleSystem


class ParticleEmitter:
    def emit(self, particle_system: ParticleSystem):
        raise NotImplementedError()
    
    
class BurstParticleEmitter(ParticleEmitter):
    def __init__(
            self,
            position: Vec2,
            rotation: float | tuple[float, float],
            count: int | tuple[int, int],
            size: float | tuple[float, float],
            speed: float | tuple[float, float],
            angular_speed: float | tuple[float, float],
            gravity: float | Vec2,
            angle: float,
            spread: float,
            lifetime: float | tuple[float, float],
            fade_duration: float = 0,
            fade_easing: Callable[[float], float] = lambda f: f,
            fade_type: int = FadingTypes.NONE,
            color: Optional[Color]=None,
            texture: Optional[Texture]=None
    ):
        
        self.position = position
        self.rotation = rotation
        
        self.count = count
        self.size = size
        
        self.speed = speed
        self.angular_speed = angular_speed
        self.gravity = gravity if isinstance(gravity, Vec2) else Vec2(0, gravity)
        
        self.angle = angle
        self.spread = spread
        
        self.lifetime = lifetime
        self.fade_duration = fade_duration
        self.fade_easing = fade_easing
        self.fade_type = fade_type
        
        self.color = color or Colors.WHITE
        self.texture = texture
    
    @staticmethod
    def _get_float(value: float | tuple[float, float]):
        return random(*value) if isinstance(value, tuple) else value
    
    @staticmethod
    def _get_floats(value: float | tuple[float, float], count: int):
        return np.random.uniform(value[0], value[1], count) if isinstance(value, tuple) else np.full(count, value)
    
    
    def emit(self, particle_system: ParticleSystem):
        count = randrange(self.count[0], self.count[1]) if isinstance(self.count, tuple) else self.count
        
        positions = np.tile(np.array(self.position), (count, 1))
        rotations = self._get_floats(self.rotation, count)
        sizes = self._get_floats(self.size, count)
        speeds = self._get_floats(self.speed, count)
        angles = self._get_floats((self.angle-self.spread, self.angle+self.spread) if self.spread else self.angle, count)
        angular_speeds = self._get_floats(self.angular_speed, count)
        velocities = np.stack([np.cos(angles), np.sin(angles)], axis=0).transpose() * np.array([speeds]).transpose()
        lifetimes = self._get_floats(self.lifetime, count)
        
        particle_system.emit_pool(positions, velocities, np.array(self.gravity), rotations, angular_speeds, sizes, lifetimes, self.texture, self.color)

    
