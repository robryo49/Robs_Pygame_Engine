from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .behavior import ObjectBehavior, LayoutObjectBehavior
from ..animation import AdderAnimation, Animation, AnimationManager, MultiplierAnimation, SetterAnimation
from ..events import Event
from ..rendering import RectStyle
from ..utils import ObjectFlags, vec2, clamp, inf, lerp, EasingFunctionType, Callback, ValueOrGetter, Color, Anchor

if TYPE_CHECKING:
    from ..core import Camera
    from ..objects import PygameObject, LayoutObject
    from .object_factory import ObjectFactory


# region ACTION BEHAVIORS


class ActionOnEventBehavior(ObjectBehavior):
    def __init__(self, event: str | Event | tuple[str | Event, ...], action: Callback[[PygameObject], Any]):
        super().__init__()

        self._event = event

        self._action = action
    
    def on_event(self, event: str | Event) -> None:
        
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
    def __init__(self, action: Callback[[PygameObject], Any]):
        super().__init__()

        self._action = action

    def on_update(self, dt: float) -> None:
        self._exec(self._action, self.owner)

class ActionOnClickBehavior(ObjectBehavior):
    def __init__(self, button: int, on_click: Callback[[PygameObject], Any] = None, on_hold: Callback[[PygameObject], Any] = None, on_release: Callback[[PygameObject], Any] = None):
        super().__init__()

        self._button = button

        self._on_click = on_click
        self._on_hold = on_hold
        self._on_release = on_release
        
    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: vec2) -> None:
        self._exec(self._on_click, self.owner)
        
    def on_hold(self, button: int, pos: vec2) -> None:
        self._exec(self._on_hold, self.owner)
    
    def on_release(self, button: int, pos: vec2) -> None:
        self._exec(self._on_release, self.owner)
        
class ActionOnHoverBehavior(ObjectBehavior):
    def __init__(self, hover_start: Callback[[PygameObject], Any] = None, while_hovered: Callback[[PygameObject], Any] = None, hover_end: Callback[[PygameObject], Any] = None):
        super().__init__()

        self._on_hover_start = hover_start
        self._on_hover = while_hovered
        self._on_hover_end = hover_end
        
    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.HOVERABLE)
    
    def on_hover(self) -> None:
        self._exec(self._on_hover, self.owner)
        
    def on_hover_start(self) -> None:
        self._exec(self._on_hover_start, self.owner)
        
    def on_hover_end(self) -> None:
        self._exec(self._on_hover_end, self.owner)
        
class ActionOnScrollBehavior(ObjectBehavior):
    def __init__(self, action: Callback[[PygameObject, int, vec2], Any] = None):
        super().__init__()

        self._action = action

    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.SCROLLABLE)

    def on_scroll(self, scroll: int, pos: vec2) -> None:
        self._exec(self._action, self.owner, scroll, pos)

class ActionOnCollisionBehavior(ObjectBehavior):
    def __init__(self, on_collision: Callback[[PygameObject, PygameObject], Any] = None, while_colliding: Callback[[PygameObject, PygameObject], Any] = None, on_collision_end: Callback[[PygameObject, PygameObject], Any] = None,
                 condition_on_other: Optional[Callable[[PygameObject], bool]] = None):
        super().__init__()

        self._on_collision_action = on_collision
        self._while_colliding_action = while_colliding
        self._on_collision_end_action = on_collision_end

        self._condition_on_other = condition_on_other
        
        self._colliding_objects: list[PygameObject] = []
        
    def _validate(self, obj: PygameObject) -> bool:
        return self._condition_on_other is None or self._condition_on_other(obj)
        
    def on_collision(self, obj: PygameObject) -> None:
        if self._validate(obj):
            self._exec(self._on_collision_action, self.owner, obj)
            self._colliding_objects.append(obj)
        
    def on_update(self, dt: float) -> None:
        if self._colliding_objects:
            for obj in self._colliding_objects:
                self._exec(self._while_colliding_action, self.owner, obj)
        
    def on_collision_end(self, obj: PygameObject) -> None:
        if self._validate(obj):
            self._exec(self._on_collision_end_action, self.owner, obj)
            self._colliding_objects.remove(obj)

class ActionOnAttributeChangeBehavior(ObjectBehavior):
    def __init__(self, attribute: str, action: Callable[[PygameObject], Any]):
        super().__init__()

        self._attribute = attribute
        self._action = action

        self._previous_attribute_value = None

    def on_attach(self) -> None:
        self._previous_attribute_value = getattr(self.owner, self._attribute)

    def on_update(self, dt: float) -> None:
        current_attribute_value = getattr(self.owner, self._attribute)
        if current_attribute_value != self._previous_attribute_value:
            self._exec(self._action, self.owner)
            self._previous_attribute_value = current_attribute_value

# endregion


# region ANIMATION BEHAVIORS


class AnimationOnClickBehavior(ObjectBehavior):
    def __init__(self, button: int, click_animation: Optional[Callable[[], Animation]] = None, release_animation: Optional[Callable[[], Animation]] = None):
        super().__init__()
        
        self._button = button
        self._click_animation = click_animation
        self._release_animation = release_animation
        
        self._animation_manager: Optional[AnimationManager] = None
    
    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        self._animation_manager = owner.services.get_animation_manager()
        owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_click(self, button: int, pos: vec2) -> None:
        if not self._animation_manager or not self._click_animation: return
        if button == self._button:
            self._animation_manager.play(self._click_animation())
    
    def on_release(self, button: int, pos: vec2) -> None:
        if not self._animation_manager or not self._release_animation: return
        if button == self._button:
            self._animation_manager.play(self._release_animation())

class AnimationOnHoverBehavior(ObjectBehavior):
    def __init__(self, hover_start_animation: Optional[Callable[[], Animation]] = None, hover_end_animation: Optional[Callable[[], Animation]] = None):
        super().__init__()
        
        self._hover_start_animation = hover_start_animation
        self._hover_end_animation = hover_end_animation
        
        self._animation_manager: Optional[AnimationManager] = None
    
    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        self._animation_manager = owner.services.get_animation_manager()
        owner.add_flag(ObjectFlags.CLICKABLE)
    
    def on_hover_start(self) -> None:
        if not self._animation_manager or not self._hover_start_animation: return
        self._animation_manager.play(self._hover_start_animation())
    
    def on_hover_end(self) -> None:
        if not self._animation_manager or not self._hover_end_animation: return
        self._animation_manager.play(self._hover_end_animation())

class AnimationOnAttributeChangeBehavior(ActionOnAttributeChangeBehavior):
    def __init__(self, attribute: str, animation: Optional[Callable[[], Animation]]):
        super().__init__(attribute, lambda o: o.play_animation(animation()))



# endregion


# region ATTRIBUTE BEHAVIORS


class AddToAttributeOnHoverBehavior(AnimationOnHoverBehavior):
    def __init__(self, attribute: str, value, duration: float, easing_function: EasingFunctionType):
        super().__init__(
            lambda: AdderAnimation(self._owner, attribute, value, duration, easing_function),
            lambda: AdderAnimation(self._owner, attribute, -value, duration, easing_function)
        )

class MultiplyAttributeOnHoverBehavior(AnimationOnHoverBehavior):
    def __init__(self, attribute: str, multiplier, duration: float, easing_function: EasingFunctionType):
        super().__init__(
            lambda: MultiplierAnimation(self._owner, attribute, multiplier, duration, easing_function),
            lambda: MultiplierAnimation(self._owner, attribute, 1 / multiplier, duration, easing_function)
        )

class SetAttributeOnHoverBehavior(AnimationOnHoverBehavior):
    def __init__(self, attribute: str, start_value, end_value, duration: float, easing_function: EasingFunctionType):
        super().__init__(
            lambda: SetterAnimation(self._owner, attribute, end_value, duration, easing_function, start_value),
            lambda: SetterAnimation(self._owner, attribute, start_value, duration, easing_function, end_value)
        )


class AddToAttributeOnClickBehavior(AnimationOnClickBehavior):
    def __init__(self, button: int, attribute: str, value, duration: float, easing_function: EasingFunctionType):
        super().__init__(button,
                         lambda: AdderAnimation(self._owner, attribute, value, duration, easing_function),
                         lambda: AdderAnimation(self._owner, attribute, -value, duration, easing_function)
                         )

class MultiplyAttributeOnClickBehavior(AnimationOnClickBehavior):
    def __init__(self, button: int, attribute: str, multiplier, duration: float, easing_function: EasingFunctionType):
        super().__init__(button,
                         lambda: MultiplierAnimation(self._owner, attribute, multiplier, duration, easing_function),
                         lambda: MultiplierAnimation(self._owner, attribute, 1 / multiplier, duration, easing_function)
                         )

class SetAttributeOnClickBehavior(AnimationOnClickBehavior):
    def __init__(self, button: int, attribute: str, start_value, end_value, duration: float, easing_function: EasingFunctionType):
        super().__init__(button,
                         lambda: SetterAnimation(self._owner, attribute, end_value, duration, easing_function, start_value),
                         lambda: SetterAnimation(self._owner, attribute, start_value, duration, easing_function, end_value)
                         )
        

class DynamicAttributeBehavior(ObjectBehavior):
    def __init__(self, attribute: str, value_getter: ValueOrGetter[Any], template: Optional[str] = None, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr):
        super().__init__()
        
        self._attribute = attribute
        self._value_getter = value_getter
        self._template = template
        
        self._strength = strength
        
        self._get_attr = attr_getter
        self._set_attr = attr_setter

    def on_update(self, dt: float) -> None:
        if (owner := self.owner) is None: return
        
        value = self._evaluate(self._value_getter)
        attr_value = self._get_attr(owner, self._attribute)
        
        if self._template is not None:
            value = self._template.format(*(value if isinstance(value, tuple) and len(value) == self._template.count("{}") else (value, )))
        elif 0 < self._strength < 1:
            try:
                value = lerp(attr_value, value, self._strength)
            except TypeError:
                pass
            
        if value == attr_value:
            return
        
        self._set_attr(owner, self._attribute, value)

class AttributeValueSnappingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, values: list[float], offset: float = 0, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr):
        super().__init__()
        
        self._attribute = attribute
        self._values = values
        self._offset = offset
        
        self._strength = strength
        
        self._get_attr = attr_getter
        self._set_attr = attr_setter
    
    def on_update(self, dt: float) -> None:
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        value = min(self._values, key=lambda x: abs(x - (attr_value + self._offset)))
        
        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
            
        self._set_attr(owner, self._attribute, value)

class AttributeGridSnappingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, step: float, offset: float = 0, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr):
        super().__init__()
        self._attribute = attribute
        
        self._step = step
        self._offset = offset
        
        self._strength = strength
        
        self._get_attr = attr_getter
        self._set_attr = attr_setter
    
    def on_update(self, dt: float) -> None:
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        value = round((attr_value - self._offset) / self._step) * self._step + self._offset
        
        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
        
        self._set_attr(owner, self._attribute, value)

class AttributeClampingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, min_value: Optional[float | Callable[[],  float]] = None, max_value: Optional[float | Callable[[],  float]] = None, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr):
        super().__init__()
        self._attribute = attribute
        
        self._min_value = -inf if min_value is None else min_value
        self._max_value = inf if max_value is None else max_value
        self._strength = strength
        
        self._get_attr = attr_getter
        self._set_attr = attr_setter
    
    def on_update(self, dt: float) -> None:
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        
        current_min = self._evaluate(self._min_value)
        current_max = self._evaluate(self._max_value)
        
        target_value = clamp(attr_value, current_min, current_max)
        
        if 0 < self._strength < 1:
            target_value = lerp(attr_value, target_value, self._strength)
        
        self._set_attr(owner, self._attribute, target_value)

class AttributeFixingBehavior(ObjectBehavior):
    def __init__(self, attribute: str, value: Optional[Any | Callable[[], Any]] = None, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr):
        super().__init__()
        self._attribute = attribute
        self._value = value
        
        self._strength = strength
        
        self._get_attr = attr_getter
        self._set_attr = attr_setter
    
    def on_attach(self) -> None:
        self._value = self._value if self._value is not None else getattr(self.owner, self._attribute)
    
    def on_update(self, dt: float) -> None:
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        value = self._evaluate(self._value)
        
        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
        self._set_attr(owner, self._attribute, value)


# endregion


class HideOnCameraZoomBehavior(ObjectBehavior):
    def __init__(self, camera: Camera, min_zoom: Optional[float] = None, max_zoom: Optional[float] = None):
        super().__init__()
        
        self._min_zoom = min_zoom
        self._max_zoom = max_zoom
        
        self._camera = camera
    
    def on_update(self, dt: float) -> None:
        if (owner := self.owner) is None: return

        hide = False
        if self._max_zoom is not None and self._max_zoom < self._camera.zoom:
            hide = True
        if self._min_zoom is not None and self._min_zoom > self._camera.zoom:
            hide = True
        
        if hide:
            owner.add_flag(ObjectFlags.HIDDEN)
        else:
            owner.remove_flag(ObjectFlags.HIDDEN)


class DraggableBehavior(ObjectBehavior):
    def __init__(
            self, button: int = 1, target: Optional[PygameObject] = None,
            on_drag_start: Callback[[PygameObject], Any] = None,
            while_dragging: Callback[[PygameObject], Any] = None,
            on_drag_end: Callback[[PygameObject], Any] = None,
    ):
        super().__init__()
        self._button: int = button
        self._target: Optional[PygameObject] = target
        self._dragging: bool = False
        self._offset: vec2 = vec2(0, 0)

        self._on_drag_start: Callback[[PygameObject], Any] = on_drag_start
        self._while_dragging: Callback[[PygameObject], Any] = while_dragging
        self._on_drag_end: Callback[[PygameObject], Any] = on_drag_end
    
    @property
    def target(self) -> Optional[PygameObject]:
        return self._target if self._target is not None else self.owner
    
    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.DRAGGABLE)
    
    def on_click(self, button: int, pos: vec2) -> None:
        if (target := self.target) is None: return

        if button == self._button:
            self._dragging = True
            self._offset = target.pos - target.world_to_parent_children_local(pos)
            self._exec(self._on_drag_start, self.owner)
    
    def on_hold(self, button: int, pos: vec2) -> None:
        if (target := self.target) is None: return

        if self._dragging and button == self._button:
            target.pos = target.world_to_parent_children_local(pos) + self._offset
            self._exec(self._while_dragging, self.owner)
    
    def on_release(self, button: int, pos: vec2) -> None:
        if button == self._button:
            self._dragging = False
            self._exec(self._on_drag_end, self.owner)



class ActionOnObjectAdditionBehavior(LayoutObjectBehavior):
    def __init__(
            self,
            on_object_addition: Callback[[LayoutObject, PygameObject], Any] = None,
            on_object_removal: Callback[[LayoutObject, PygameObject], Any] = None,
    ):
        super().__init__()

        self._on_object_addition: Callback[[LayoutObject, PygameObject], Any] = on_object_addition
        self._on_object_removal: Callback[[LayoutObject, PygameObject], Any] = on_object_removal

    def on_object_addition(self, obj: PygameObject) -> None:
        self._exec(self._on_object_addition, self.owner, obj)

    def on_object_removal(self, obj: PygameObject) -> None:
        self._exec(self._on_object_removal, self.owner, obj)


class ReorderableLayoutBehavior(ActionOnObjectAdditionBehavior):
    def __init__(self, placeholder_style: RectStyle):
        super().__init__()

        self._placeholder_style = placeholder_style
        self._factory: Optional[ObjectFactory] = None

    def on_attach(self) -> None:
        super().on_attach()
        self._factory = self.owner.services.get_object_factory()

        for obj in self._owner._object_placements:
            self.on_object_addition(obj)

    def _start_dragging_object(self, obj: PygameObject):
        placeholder = self._factory.shape.rect(vec2(), obj.dims, RectStyle(Color(0, 0, 0, 100), 10, Color(0, 0, 0, 0), bd_radius=20))
        self.owner.replace_object(obj, placeholder, ignore_callbacks=True)
        self.owner.add_child(obj, Anchor.TL)
        obj.set_property("layout_placeholder", placeholder)
        obj.focus()

    def _while_dragging_object(self, obj: PygameObject):
        placeholder = obj.get_property("layout_placeholder")
        owner = self.owner

        x, y = obj.pos
        dx, dy = x - placeholder.pos.x, y - placeholder.pos.y

        col, row = owner.get_object_placement(placeholder)

        next_col, next_row = col + 1 if dx >= 0 else col - 1, row + 1 if dy >= 0 else row - 1

        if owner.mode == owner.GRID_MODE:
            if 0 <= next_col <= owner.max_col:
                next_col_width = owner.get_col_width(next_col)
                if abs(dx) > next_col_width * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(next_col, row))
            if 0 <= next_row <= owner.max_row:
                next_row_height = owner.get_row_height(next_row)
                if abs(dy) > next_row_height * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(col, next_row))

        if owner.mode == owner.COL_MODE:

            if 0 <= next_col <= owner.max_col:
                next_col_width = owner.get_col_width(next_col)
                if abs(dx) > next_col_width * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(next_col, row))

            if 0 <= next_row <= owner.max_row:
                next_row_height = owner.get_row_height(next_row, col)
                if abs(dy) > next_row_height * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(col, next_row))

    def _end_dragging_object(self, obj: PygameObject):
        placeholder = obj.remove_property("layout_placeholder")
        self.owner.replace_object(placeholder, obj, ignore_callbacks=True)
        obj.unfocus()

    def on_object_addition(self, obj: PygameObject) -> None:
        super().on_object_addition(obj)

        obj.make_draggable(
            on_drag_start=self._start_dragging_object,
            while_dragging=self._while_dragging_object,
            on_drag_end=self._end_dragging_object,
        )

    def on_object_removal(self, obj: PygameObject) -> None:
        super().on_object_removal(obj)
        obj.remove_behavior("draggable_behavior")

    