from copy import copy
from typing import Any, Callable, Optional

from ..events import Event
from ..animation import AnimationManager, MultiplierAnimation
from ..utils import ObjectFlags, Vec2
from .behavior import ObjectBehavior



class ActionOnEventBehavior(ObjectBehavior):
    def __init__(self, event: str | Event | tuple[str | Event, ...], action: Callable | tuple[Callable, ...]):
        super().__init__()
        
        self._event = event
        
        self._action = action
    
    def on_event(self, event: str | Event):
        
        if isinstance(self._event, tuple):
            found = False
            for e in self._event:
                if Event.are_equal(e, event):
                    found = True
                    break
            if not found: return
        elif Event.are_equal(self._event, event): return
        elif self._action is None: return
        
        if isinstance(self._action, tuple):
            for action in self._action:
                action()
        else:
            self._action()
        

    
class ActionOnUpdateBehavior(ObjectBehavior):
    def __init__(self, action: Callable | tuple[Callable, ...]):
        super().__init__()
        
        self._action = action
        
    def on_update(self, dt: float):
        if self._action is None: return
        if isinstance(self._action, tuple):
            for action in self._action:
                action()
        else:
            self._action()
    

class ActionOnClickBehavior(ObjectBehavior):
    def __init__(self, button: int, action: Callable | tuple[Callable, ...]):
        super().__init__()
        
        self._button = button
        
        self._action = action
        
    def on_attach(self):
        self.owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: Vec2):
        if button == self._button:
            if isinstance(self._action, tuple):
                for action in self._action:
                    action()
            else:
                self._action()



class ScaleOnHoverBehavior(ObjectBehavior):
    def __init__(self, scaling: float, duration: float, easing_function: Callable[[float], float]):
        super().__init__()
        
        self._scaling = scaling
        self._duration = duration
        self._easing_function = easing_function
        
        self._animation_manager: Optional[AnimationManager] = None
        
    def on_attach(self):
        self._animation_manager = self.owner.get_service(AnimationManager)
        self.owner.add_flag(ObjectFlags.HOVERABLE)
    
    def on_hover_start(self):
        if not self._animation_manager: return
        self._animation_manager.play(MultiplierAnimation(self._object, "scale", self._scaling, self._duration, self._easing_function))
    
    def on_hover_end(self):
        if not self._animation_manager: return
        self._animation_manager.play(MultiplierAnimation(self._object, "scale", 1/self._scaling, self._duration, self._easing_function))


class ScaleOnClickBehavior(ObjectBehavior):
    def __init__(self, button: int, scaling: float, duration: float, easing_function: Callable[[float], float]):
        super().__init__()
        
        self._button = button
        
        self._scaling = scaling
        self._duration = duration
        self._easing_function = easing_function
        
        self._animation_manager: Optional[AnimationManager] = None
    
    def on_attach(self):
        self._animation_manager = self.owner.get_service(AnimationManager)
        self.owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: Vec2):
        if not self._animation_manager: return
        if button == self._button:
            self._animation_manager.play(MultiplierAnimation(self.owner, "scale", self._scaling, self._duration, self._easing_function))
    
    def on_release(self, button: int, pos: Vec2):
        if not self._animation_manager: return
        if button == self._button:
            self._animation_manager.play(MultiplierAnimation(self.owner, "scale", 1 / self._scaling, self._duration, self._easing_function))
            
            

class DynamicAttribute(ObjectBehavior):
    def __init__(self, attribute: str, getter: Callable[[], Any | tuple[Any, ...]], template: Optional[str] = None):
        super().__init__()
        
        self._attribute = attribute
        self._getter = getter
        self._template = template
        
        self._value = None
        
        
    def on_update(self, dt: float):
        if not self.owner:
            return
        
        value = self._getter()
        if value == self._value:
            return
        
        self._value = copy(value)
        
        if self._template is not None:
            value = self._template.format(*value if isinstance(value, tuple) else (value, ))
            
        setattr(self.owner, self._attribute, value)
