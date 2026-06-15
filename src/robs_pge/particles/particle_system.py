from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from utils import Vec2, Transform, Anchor
from rendering import DrawTexture

from .particle import Particle, FadingTypes
from .particle_pool import ParticlePool

if TYPE_CHECKING:
    from core import Camera


class ParticleSystem:
    def __init__(self):

        self._particles: list[Particle] = []
        self._particle_pools: list[ParticlePool] = []
        
        self.count = 0
        
    # region PROPERTIES
    
    @property
    def particles(self):
        return self._particles
    
    # endregion
    
    def emit_pool(self, positions, velocities, gravity, rotations, angular_speeds, sizes, lifetimes, texture):
        pool = ParticlePool(
            positions=positions,
            velocities=velocities,
            gravity=gravity,
            rotations=rotations,
            angular_speeds=angular_speeds,
            sizes=sizes,
            lifetimes=lifetimes,
            texture=texture
        )
        
        self._particle_pools.append(pool)
    
    def emit_particle(self, particle: Particle):
        self._particles.append(particle)
        
    def update_particles(self, dt):
        alive: list[Particle] = []
        
        for p in self.particles:
            p.life -= dt
            
            if p.life > 0:
                p.vel += p.gravity * dt
                if p.vel:
                    p.transform.translate(p.vel * dt)
                if p.ang_vel:
                    p.transform.rotate(p.ang_vel * dt)
                
                alive.append(p)
        
        self._particles = alive
    
    def update_pools(self, dt):
        for pool in self._particle_pools:
            pool.update(dt)
    
    def update(self, dt):
        self.update_particles(dt)
        self.update_pools(dt)
        
        
    def render(self, submit, camera: Optional[Camera] = None):
        self.count = 0
        
        for p in self.particles:
            self.count += 1
            
            transform = Transform(p.transform.pos, p.transform.rotation, p.transform.scale)
            
            if p.fade_type is not FadingTypes.NONE and p.fade_duration > 0 and p.life < p.fade_duration:
                factor = 1 - p.fade_easing(1 - p.life / p.fade_duration) if p.life < p.fade_duration else 1
                
                if p.fade_type & FadingTypes.SCALE:
                    transform.scale *= factor
                    
            submit(DrawTexture(p.texture, transform, p.layer, Anchor.C))

        for pool in self._particle_pools:
            for i, pos in enumerate(pool.positions):
                submit(DrawTexture(pool.texture, Transform(Vec2(pos), pool.rotations[i], pool.sizes[i]), pool.layer, Anchor.C))
                self.count += 1