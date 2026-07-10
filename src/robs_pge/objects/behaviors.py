from __future__ import annotations
from copy import copy
from typing import Any, Callable, Optional, TYPE_CHECKING

from ..events import Event
from ..animation import AnimationManager, MultiplierAnimation
from ..utils import ObjectFlags, Vec2, clamp, inf
from .behavior import ObjectBehavior

if TYPE_CHECKING:
    from ..core import Camera



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
    def __init__(self, button: int, action: Optional[Callable | tuple[Callable, ...]]):
        super().__init__()
        
        self._button = button
        
        self._action = action
        
    def on_attach(self):
        self.owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: Vec2):
        if button == self._button:
            if isinstance(self._action, tuple):
                for action in self._action:
                    if action is not None: action()
            elif self._action is not None:
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
        self._animation_manager.play(MultiplierAnimation(self._owner, "scale", self._scaling, self._duration, self._easing_function))
    
    def on_hover_end(self):
        if not self._animation_manager: return
        self._animation_manager.play(MultiplierAnimation(self._owner, "scale", 1 / self._scaling, self._duration, self._easing_function))


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



class HideOnCameraZoomBehavior(ObjectBehavior):
    def __init__(self, camera: Camera, min_zoom: Optional[float] = None, max_zoom: Optional[float] = None):
        super().__init__()
        
        self._min_zoom = min_zoom
        self._max_zoom = max_zoom
        
        self._camera = camera
    
    def on_update(self, dt: float):
        hide = False
        if self._max_zoom is not None:
            if self._max_zoom < self._camera.zoom:
                hide = True
        if self._min_zoom is not None:
            if self._min_zoom > self._camera.zoom:
                hide = True
                
        if hide:
            self.owner.add_flag(ObjectFlags.HIDDEN)
        else:
            self.owner.remove_flag(ObjectFlags.HIDDEN)
            

class DynamicAttributeBehavior(ObjectBehavior):
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


class DraggableBehavior(ObjectBehavior):
    def __init__(self, button: int = 1):
        super().__init__()
        self._button = button
        self._dragging = False
        self._offset = Vec2(0, 0)
    
    def on_attach(self):
        self.owner.add_flag(ObjectFlags.DRAGGABLE)
    
    def on_click(self, button: int, pos: Vec2):
        if button == self._button:
            self._dragging = True
            self._offset = self.owner.pos - pos
    
    def on_hold(self, button: int, pos: Vec2):
        if self._dragging and button == self._button:
            self.owner.pos = pos + self._offset
    
    def on_release(self, button: int, pos: Vec2):
        if button == self._button:
            self._dragging = False


class AttributeValueSnappingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, values: list[float], offset: float = 0):
        super().__init__()
        
        self._attribute = attribute
        self._values = values
        self._offset = offset
    
    def on_update(self, dt):
        setattr(self.owner, self._attribute, min(
            self._values,
            key=lambda x: abs(x - (getattr(self.owner, self._attribute) + self._offset))
        ))


class AttributeGridSnappingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, step: float, offset: float = 0):
        super().__init__()
        self._attribute = attribute
        
        self._step = step
        self._offset = offset
        
    def on_update(self, dt: float):
        setattr(self.owner, self._attribute, round((getattr(self.owner, self._attribute)-self._offset) / self._step)*self._step+self._offset)


class AttributeClampingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, min_value: Optional[float] = -inf, max_value: Optional[float] = inf):
        super().__init__()
        self._attribute = attribute
        self._min_value = min_value if min_value is not None else -inf
        self._max_value = max_value if max_value is not None else inf
    
    def on_update(self, dt: float):
        setattr(self.owner, self._attribute, clamp(getattr(self.owner, self._attribute), self._min_value, self._max_value))


class AttributeFixingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, value = None):
        super().__init__()
        self._attribute = attribute
        self._value = value
    
    def on_attach(self):
        self._value = self._value if self._value is not None else getattr(self.owner, self._attribute)
    
    def on_update(self, dt: float):
        setattr(self.owner, self._attribute, self._value)
    
    