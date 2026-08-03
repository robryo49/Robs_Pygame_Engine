from __future__ import annotations
from typing import Optional, TYPE_CHECKING

import numpy as np

from ...utils import Vec2, Transform, Anchor, Colors
from ...rendering import CircleStyle, DrawCircle, DrawTexture

from .particle import Particle, FadingTypes
from .particle_pool import ParticlePool

if TYPE_CHECKING:
    from ...objects import Layer


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
    
    def emit_pool(self, positions, velocities, gravity, rotations, angular_speeds, sizes, lifetimes, texture, color):
        pool = ParticlePool(
            positions=positions,
            velocities=velocities,
            gravity=gravity,
            rotations=rotations,
            angular_speeds=angular_speeds,
            sizes=sizes,
            lifetimes=lifetimes,
            texture=texture,
            color=color
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
    
    
    def render(self, submit, layer: Layer):
        self.count = 0
    
        for p in self.particles:
            self.count += 1
            transform = Transform(p.transform.pos, p.transform.rotation, p.transform.scale)
            
            if p.fade_type is not FadingTypes.NONE and p.fade_duration > 0 and p.life < p.fade_duration:
                factor = 1 - p.fade_easing(1 - p.life / p.fade_duration) if p.life < p.fade_duration else 1
                if p.fade_type & FadingTypes.SCALE:
                    transform.scale *= factor
            
            if p.texture is not None:
                submit(DrawTexture(transform, p.layer, Anchor.C, False, p.texture))
            else:
                submit(DrawCircle(
                    Transform(transform.pos, transform.rotation, 1),
                    layer,
                    p.layer, Anchor.C, False,
                    round(4*transform.scale),
                    CircleStyle(bg_color=p.color or Colors.WHITE)
                ))
        
        for pool in self._particle_pools:
            scale_factors = np.ones(len(pool.positions), dtype=np.float32)
            
            if pool.fade_type is not FadingTypes.NONE and pool.fade_duration > 0:
                fading = pool.lifetimes < pool.fade_duration
                if np.any(fading):
                    progress = 1 - pool.lifetimes[fading] / pool.fade_duration
                    eased = np.vectorize(pool.fade_easing)(progress)
                    factor = 1 - eased
                    
                    if pool.fade_type & FadingTypes.SCALE:
                        scale_factors[fading] = factor
            
            for i, pos in enumerate(pool.positions):
                submit(DrawTexture(
                    Transform(Vec2(pos), pool.rotations[i], pool.sizes[i] * scale_factors[i]),
                    pool.layer, Anchor.C, True,
                    pool.texture
                ))
                self.count += 1