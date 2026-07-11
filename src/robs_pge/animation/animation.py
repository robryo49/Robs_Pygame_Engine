from typing import Callable, Optional

from .tween import Tween
from ..utils import Easing


class Animation:
    def __init__(self, obj: object, attr: str, duration: float, easing_function: Callable[[float], float] = Easing.LINEAR):
        self._obj = obj
        self._attr = attr
        
        self._tween = Tween(duration, easing_function)
        
        self._linked_animations: list[tuple[Animation, float]] = []
        
    # region PROPERTIES
    
    @property
    def obj(self):
        return self._obj
    
    @property
    def attr(self):
        return self._attr
    
    @property
    def duration(self):
        return self.tween.duration
    
    @property
    def tween(self):
        return self._tween
    
    @property
    def linked_animations(self):
        return self._linked_animations
    
    @property
    def finished(self):
        return self.tween.finished
    
    # endregion
    
    def __str__(self):
        return f"Animation({str(self.obj)}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"
    
    def followed_by(self, anim: "Animation", delay=0.0):
        self._linked_animations.append((anim, self.duration + delay))
        return self
    
    def plus(self, anim, delay):
        self._linked_animations.append((anim, delay))
        return self
        
    def set_attr(self, value):
        setattr(self.obj, self.attr, value)
        
    def get_attr(self):
        return getattr(self.obj, self.attr)
        
    def update(self, dt: float):
        self.tween.step(dt)
    
    def start(self):
        self.tween.reset()
        


class AdderAnimation(Animation):
    def __init__(self, obj: object, attr: str, value, duration: float, easing_function: Callable[[float], float] = Easing.LINEAR):
        super().__init__(obj, attr, duration, easing_function)
        
        self._adder = value
        
        self._start_value = self.get_attr()
        self._end_value = self.start_value + self._adder
    
    # region PROPERTIES
    
    @property
    def start_value(self):
        return self._start_value
    
    @property
    def end_value(self):
        return self._end_value
    
    # endregion
    
    def __str__(self):
        return f"AdderAnimation({str(self.obj)}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"
    
    def get_inverse(self):
        return AdderAnimation(self.obj, self.attr, -self._adder, self.duration)
    
    def start(self):
        super().start()
        
        self._start_value = self.get_attr()
        self._end_value = self.start_value + self._adder
        
    def update(self, dt: float):
        self.set_attr(self.get_attr() + self._adder * self.tween.step(dt))
        

class SetterAnimation(AdderAnimation):
    def __init__(self, obj: object, attr: str, value, duration: float, easing_function: Callable[[float], float] = Easing.LINEAR, start_value: Optional[float] = None):
        super().__init__(obj, attr, value - getattr(obj, attr), duration, easing_function)
        
        self._target = value
        self._forced_start_value = start_value
        
    # region PROPERTIES
    
    @property
    def target(self):
        return self._target
    
    # endregion
    
    def __str__(self):
        return f"SetterAnimation({str(self.obj)}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"
    
    def start(self):
        self._adder = self.target - (self.get_attr() if self._forced_start_value is None else self._forced_start_value)
        super().start()
    
        

class MultiplierAnimation(Animation):
    def __init__(self, obj: object, attr: str, value, duration: float, easing_function: Callable[[float], float] = Easing.LINEAR):
        super().__init__(obj, attr, duration, easing_function)
        
        self._multiplier = value
        
        self._start_value = self.get_attr()
        self._end_value = self.start_value * self._multiplier
    
    # region PROPERTIES
    
    @property
    def start_value(self):
        return self._start_value
    
    @property
    def end_value(self):
        return self._end_value
    
    # endregion
    
    def __str__(self):
        return f"MultiplierAnimation({str(self.obj)}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"
    
    def get_inverse(self):
        return AdderAnimation(self.obj, self.attr, 1/self._multiplier, self.duration)
    
    def start(self):
        super().start()
        
        self._start_value = self.get_attr()
        self._end_value = self.start_value * self._multiplier
        
    def update(self, dt: float):
        self.set_attr(self.get_attr() * (self._multiplier ** self.tween.step(dt)))
    