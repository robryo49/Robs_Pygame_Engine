from typing import Callable

from utils import Easing, clamp


class Tween:
    def __init__(self, duration: float, easing_function: Callable = Easing.LINEAR):
        
        self._duration = duration
        self._easing_function = easing_function
        
        self._time = 0
        self._progress = 0
    
    # region PROPERTIES
    
    @property
    def duration(self):
        return self._duration
    
    @property
    def time(self):
        return self._time
    
    @property
    def progress(self):
        return self._progress
    
    @property
    def easing_function(self):
        return self._easing_function
    
    @property
    def finished(self):
        return self._time >= self._duration
    
    # endregion
    
    def reset(self):
        self._time = 0.0
        self._progress = 0
        
    def step(self, dt: float):
        self._time += dt
        p, self._progress = self._progress, self.easing_function(clamp(self.time / self.duration))
        return self.progress - p
        