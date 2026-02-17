from .animation import Animation


class AnimationManager:
    def __init__(self):
        self._time = 0.0
        
        self._active: list[Animation] = []
        self._scheduled: list[tuple[Animation, float]] = []
        
    # region PROPERTIES
    
    @property
    def active(self):
        return self._active
    
    @property
    def scheduled(self):
        return self._scheduled
    
    @property
    def time(self):
        return self._time
    
    # endregion
    
    def play(self, anim: Animation):
        anim.start()
        self.scheduled.append((anim, self.time))
    
    def update(self, dt: float):
        self._time += dt
        
        newly_active = []
        for anim, start_time in self.scheduled[:]:
            if self.time >= start_time :
                self._scheduled.remove((anim, start_time))
                
                anim.start()
                anim.update(self.time - start_time)
                
                self.active.append(anim)
                newly_active.append(anim)
                
                for linked_anim, delay in anim.linked_animations:
                    self.scheduled.append((linked_anim, self.time + delay))
        
        for anim in self.active[:]:
            if anim not in newly_active:
                anim.update(dt)
            
            if anim.finished:
                self.active.remove(anim)
