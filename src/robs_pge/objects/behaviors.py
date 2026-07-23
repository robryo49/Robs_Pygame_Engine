from __future__ import annotations
from copy import copy
from typing import Any, Callable, Optional, TYPE_CHECKING

from ..events import Event
from ..animation import AnimationManager, MultiplierAnimation, Animation
from ..utils import ObjectFlags, Vec2, clamp, inf, Vec3, lerp
from .behavior import ObjectBehavior

if TYPE_CHECKING:
    from ..core import Camera
    from ..objects import PygameObject
    
    ObjectCallBackType = Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...] | Callable | tuple[Callable, ...]]


# region ACTION BEHAVIORS


class ActionOnEventBehavior(ObjectBehavior):
    def __init__(self, event: str | Event | tuple[str | Event, ...], action: ObjectCallBackType):
        super().__init__()
        
        self._event = event
        
        self._action = self._normalize_action(action) # type: ignore
    
    def on_event(self, event: str | Event):
        
        if isinstance(self._event, tuple):
            found = False
            for e in self._event:
                if Event.are_equal(e, event):
                    found = True
                    break
            if not found: return
        elif Event.are_equal(self._event, event): return
        
        self._exec(self._action, self.owner)
        

class ActionOnUpdateBehavior(ObjectBehavior):
    def __init__(self, action: ObjectCallBackType):
        super().__init__()
        
        self._action = self._normalize_action(action) # type: ignore
        
    def on_update(self, dt: float):
        self._exec(self._action, self.owner)
    

class ActionOnClickBehavior(ObjectBehavior):
    def __init__(self, button: int, on_click: ObjectCallBackType = None, on_hold: ObjectCallBackType = None, on_release: ObjectCallBackType = None):
        super().__init__()
        
        self._button = button
        
        self._on_click = self._normalize_action(on_click) # type: ignore
        self._on_hold = self._normalize_action(on_hold) # type: ignore
        self._on_release = self._normalize_action(on_release) # type: ignore
        
    def on_attach(self):
        self.owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: Vec2):
        self._exec(self._on_click, self.owner)
        
    def on_hold(self, button: int, pos: Vec2):
        self._exec(self._on_hold, self.owner)
    
    def on_release(self, button: int, pos: Vec2):
        self._exec(self._on_release, self.owner)
        
                
class ActionOnHoverBehavior(ObjectBehavior):
    def __init__(self, hover_start: ObjectCallBackType = None, while_hovered: ObjectCallBackType = None, hover_end: ObjectCallBackType = None):
        super().__init__()
        
        self._on_hover_start = self._normalize_action(hover_start) # type: ignore
        self._on_hover = self._normalize_action(while_hovered) # type: ignore
        self._on_hover_end = self._normalize_action(hover_end) # type: ignore
        
    def on_attach(self):
        self.owner.add_flag(ObjectFlags.HOVERABLE)
    
    def on_hover(self):
        self._exec(self._on_hover, self.owner)
        
    def on_hover_start(self):
        self._exec(self._on_hover_start, self.owner)
        
    def on_hover_end(self):
        self._exec(self._on_hover_end, self.owner)
        
class ActionOnScrollBehavior(ObjectBehavior):
    def __init__(self, action: Optional[Callable[[PygameObject, int, Vec2], Any] | tuple[Callable[[PygameObject, int, Vec2], Any], ...]] = None):
        super().__init__()
        
        self._action = action
        
    def on_attach(self):
        self.owner.add_flag(ObjectFlags.SCROLLABLE)
        
    def on_scroll(self, scroll: int, pos: Vec2):
        self._exec(self._action, self.owner, scroll, pos)


# endregion


# region ANIMATION BEHAVIORS


class AnimationOnClickBehavior(ObjectBehavior):
    def __init__(self, button: int, click_animation: Optional[Callable[[], Animation]] = None, release_animation: Optional[Callable[[], Animation]] = None):
        super().__init__()
        
        self._button = button
        self._click_animation = click_animation
        self._release_animation = release_animation
        
        self._animation_manager: Optional[AnimationManager] = None
    
    def on_attach(self):
        self._animation_manager = self.owner.get_service(AnimationManager)
        self.owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: Vec2):
        if not self._animation_manager or not self._click_animation: return
        if button == self._button:
            self._animation_manager.play(self._click_animation())
    
    def on_release(self, button: int, pos: Vec2):
        if not self._animation_manager or not self._release_animation: return
        if button == self._button:
            self._animation_manager.play(self._release_animation())


class AnimationOnHoverBehavior(ObjectBehavior):
    def __init__(self, hover_start_animation: Optional[Callable[[], Animation]] = None, hover_end_animation: Optional[Callable[[], Animation]] = None):
        super().__init__()
        
        self._hover_start_animation = hover_start_animation
        self._hover_end_animation = hover_end_animation
        
        self._animation_manager: Optional[AnimationManager] = None
    
    def on_attach(self):
        self._animation_manager = self.owner.get_service(AnimationManager)
        self.owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_hover_start(self):
        if not self._animation_manager or not self._hover_start_animation: return
        self._animation_manager.play(self._hover_start_animation())
    
    def on_hover_end(self):
        if not self._animation_manager or not self._hover_end_animation: return
        self._animation_manager.play(self._hover_end_animation())



class ScaleOnHoverBehavior(AnimationOnHoverBehavior):
    def __init__(self, scaling: float, duration: float, easing_function: Callable[[float], float]):
        super().__init__(
            lambda: MultiplierAnimation(self._owner, "scale", scaling, duration, easing_function),
            lambda: MultiplierAnimation(self._owner, "scale", 1 / scaling, duration, easing_function)
        )


class ScaleOnClickBehavior(AnimationOnClickBehavior):
    def __init__(self, button: int, scaling: float, duration: float, easing_function: Callable[[float], float]):
        super().__init__(button, lambda: MultiplierAnimation(self.owner, "scale", scaling, duration, easing_function),
                         lambda: MultiplierAnimation(self.owner, "scale", 1 / scaling, duration, easing_function))
        

# endregion


# region ATTRIBUTE BEHAVIORS


class DynamicAttributeBehavior(ObjectBehavior):
    def __init__(self, attribute: str, getter: Any | Callable[[], Any | tuple[Any]], template: Optional[str] = None, strength: float = 1):
        super().__init__()
        
        self._attribute = attribute
        self._getter = getter
        self._template = template
        
        self._strength = strength
    
    
    def on_update(self, dt: float):
        if not self.owner:
            return
        
        value = self._evaluate(self._getter)
        attr_value = getattr(self.owner, self._attribute)
        
        
        if self._template is not None:
            value = self._template.format(*(value if isinstance(value, tuple) else (value, )))
        elif 0 < self._strength < 1:
            try:
                value = lerp(attr_value, value, self._strength)
            except TypeError:
                pass
            
        if value == attr_value:
            return
        
        setattr(self.owner, self._attribute, value)


class AttributeValueSnappingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, values: list[float], offset: float = 0, strength: float = 1):
        super().__init__()
        
        self._attribute = attribute
        self._values = values
        self._offset = offset
        
        self._strength = strength
    
    def on_update(self, dt):
        attr_value = getattr(self.owner, self._attribute)
        value = min(self._values, key=lambda x: abs(x - (attr_value + self._offset)))
        
        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
            
        setattr(self.owner, self._attribute, value)


class AttributeGridSnappingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, step: float, offset: float = 0, strength: float = 1):
        super().__init__()
        self._attribute = attribute
        
        self._step = step
        self._offset = offset
        
        self._strength = strength
    
    def on_update(self, dt: float):
        
        attr_value = getattr(self.owner, self._attribute)
        value = round((attr_value - self._offset) / self._step) * self._step + self._offset
        
        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
        
        setattr(self.owner, self._attribute, value)


class AttributeClampingBehavior(ObjectBehavior):
    def __init__(
            self,
            attribute: str,
            min_value: Optional[float | Callable[[],  float]] = None,
            max_value: Optional[float | Callable[[],  float]] = None,
            strength: float = 1
    ):
        super().__init__()
        self._attribute = attribute
        
        self._min_value = -inf if min_value is None else min_value
        self._max_value = inf if max_value is None else max_value
        self._strength = strength
    
    def on_update(self, dt: float):
        attr_value = getattr(self.owner, self._attribute)
        
        # Dynamically evaluate the bounds every frame
        current_min = self._evaluate(self._min_value)
        current_max = self._evaluate(self._max_value)
        
        target_value = clamp(attr_value, current_min, current_max)
        
        # Apply strength interpolation if necessary
        if 0 < self._strength < 1:
            target_value = lerp(attr_value, target_value, self._strength)
        
        setattr(self.owner, self._attribute, target_value)


class AttributeFixingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, value = Optional[Any | Callable[[], Any]], strength: float = 1):
        super().__init__()
        self._attribute = attribute
        self._value = value
        
        self._strength = strength
    
    def on_attach(self):
        self._value = self._value if self._value is not None else getattr(self.owner, self._attribute)
    
    def on_update(self, dt: float):
        attr_value = getattr(self.owner, self._attribute)
        value = self._evaluate(self._value)
        
        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
        setattr(self.owner, self._attribute, value)


# endregion


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
            self._offset = self.owner.pos - self.owner.world_to_parent_local(pos)
    
    def on_hold(self, button: int, pos: Vec2):
        if self._dragging and button == self._button:
            self.owner.pos = self.owner.world_to_parent_local(pos) + self._offset
    
    def on_release(self, button: int, pos: Vec2):
        if button == self._button:
            self._dragging = False
    
    