from .animation import Animation
from ..utils import Callback
from typing import Any


class AnimationManager:
    def __init__(self):
        self._time = 0.0
        
        self._active_animations: list[Animation] = []
        self._scheduled_animations: list[tuple[Animation, float]] = []
        
        self._scheduled_callbacks: list[tuple[Callback[..., Any], float]] = []
        
    # region PROPERTIES
    
    @property
    def active(self):
        return self._active_animations
    
    @property
    def scheduled(self):
        return self._scheduled_animations
    
    @property
    def scheduled_callbacks(self):
        return self._scheduled_callbacks
    
    @property
    def time(self):
        return self._time
    
    # endregion
    
    def play(self, anim: Animation):
        self.scheduled.append((anim, self.time))
    
    def update(self, dt: float):
        self._time += dt
        
        newly_active = []
        for anim, start_time in self.scheduled[:]:
            if self.time >= start_time :
                self._scheduled_animations.remove((anim, start_time))
                
                anim.start()
                anim.update(self.time - start_time)
                
                self.active.append(anim)
                newly_active.append(anim)
                
                for linked_anim, delay in anim.linked_animations:
                    self.scheduled.append((linked_anim, self.time + delay))
                    
                for linked_callback, delay in anim.linked_callbacks:
                    self.scheduled_callbacks.append((linked_callback, delay))
        
        for anim in self.active[:]:
            if anim not in newly_active:
                anim.update(dt)
            
            if anim.finished:
                self.active.remove(anim)
                
        for callback, time in self.scheduled_callbacks[:]:
            if self.time >= time:
                if isinstance(callback, tuple):
                    for cb in callback:
                        cb()
                elif callback is not None:
                    callback()
