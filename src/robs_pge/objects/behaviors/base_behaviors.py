"""Behaviors that react to events, input, collisions, and attribute changes on pygame objects."""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from ..behavior import ObjectBehavior
from ...animation import AdderAnimation, Animation, AnimationManager, MultiplierAnimation, SetterAnimation
from ...events import Event
from ...utils import ObjectFlags, vec2, clamp, inf, lerp, EasingFunctionType, Callback, ValueOrGetter

if TYPE_CHECKING:
    from ...objects import PygameObject


# region ACTION BEHAVIORS

class ActionOnEventBehavior(ObjectBehavior):
    """Invoke a callback when one of the configured events is dispatched to the owner."""
    def __init__(self, event: str | Event | tuple[str | Event, ...], action: Callback[[PygameObject], Any]) -> None:
        """
        Store the event selector and the callback to run.

        :param event: Event or tuple of events that triggers the action.
        :param action: Callback invoked with the owner when the event matches.
        """
        super().__init__()

        self._event = event

        self._action = action

    def on_event(self, event: str | Event) -> None:

        """
        Run the action when the event matches the configured selector.

        :param event: Event being dispatched.
        """
        if isinstance(self._event, tuple):
            found = False
            for e in self._event:
                if Event.are_equal(e, event):
                    found = True
                    break
            if not found: return
        elif not Event.are_equal(self._event, event):
            return

        self._exec(self._action, self.owner)

class ActionOnUpdateBehavior(ObjectBehavior):
    """Invoke a callback on every update tick of the owner."""
    def __init__(self, action: Callback[[PygameObject], Any]) -> None:
        """
        Store the callback to run on each update.

        :param action: Callback invoked with the owner on every update.
        """
        super().__init__()

        self._action = action

    def on_update(self, dt: float) -> None:
        """
        Run the action for the current update tick.

        :param dt: Seconds elapsed since the previous update.
        """
        self._exec(self._action, self.owner)

class ActionOnClickBehavior(ObjectBehavior):
    """Invoke click, hold, and release callbacks for a mouse button."""
    def __init__(self, button: int, on_click: Callback[[PygameObject], Any] = None, on_hold: Callback[[PygameObject], Any] = None, on_release: Callback[[PygameObject], Any] = None) -> None:
        """
        Store the button and the click lifecycle callbacks.

        :param button: Mouse button that triggers the callbacks.
        :param on_click: Callback invoked when the button is pressed.
        :param on_hold: Callback invoked while the button is held.
        :param on_release: Callback invoked when the button is released.
        """
        super().__init__()

        self._button = button

        self._on_click = on_click
        self._on_hold = on_hold
        self._on_release = on_release

    def on_attach(self) -> None:
        """Mark the owner as clickable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.CLICKABLE)

    def on_click(self, button: int, pos: vec2) -> None:
        """
        Run the click callback when the configured button is pressed.

        :param button: Mouse button that was pressed.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._on_click, self.owner)

    def on_hold(self, button: int, pos: vec2) -> None:
        """
        Run the hold callback while the configured button is held.

        :param button: Mouse button currently held.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._on_hold, self.owner)

    def on_release(self, button: int, pos: vec2) -> None:
        """
        Run the release callback when the configured button is released.

        :param button: Mouse button that was released.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._on_release, self.owner)

class ActionOnHoverBehavior(ObjectBehavior):
    """Invoke hover callbacks as the pointer enters, stays over, and leaves the owner."""
    def __init__(self, hover_start: Callback[[PygameObject], Any] = None, while_hovered: Callback[[PygameObject], Any] = None, hover_end: Callback[[PygameObject], Any] = None) -> None:
        """
        Store the hover lifecycle callbacks.

        :param hover_start: Callback invoked when hovering begins.
        :param while_hovered: Callback invoked while the owner is hovered.
        :param hover_end: Callback invoked when hovering ends.
        """
        super().__init__()

        self._on_hover_start = hover_start
        self._on_hover = while_hovered
        self._on_hover_end = hover_end

    def on_attach(self) -> None:
        """Mark the owner as hoverable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.HOVERABLE)

    def on_hover(self) -> None:
        """Run the callback used while the owner is hovered."""
        self._exec(self._on_hover, self.owner)

    def on_hover_start(self) -> None:
        """Run the callback used when hovering begins."""
        self._exec(self._on_hover_start, self.owner)

    def on_hover_end(self) -> None:
        """Run the callback used when hovering ends."""
        self._exec(self._on_hover_end, self.owner)

class ActionOnScrollBehavior(ObjectBehavior):
    """Invoke a callback when the owner receives scroll input."""
    def __init__(self, action: Callback[[PygameObject, int, vec2], Any] = None) -> None:
        """
        Store the scroll callback.

        :param action: Callback invoked with the owner, scroll amount, and pointer position.
        """
        super().__init__()

        self._action = action

    def on_attach(self) -> None:
        """Mark the owner as scrollable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.SCROLLABLE)

    def on_scroll(self, scroll: int, pos: vec2) -> None:
        """
        Run the scroll callback for the current scroll input.

        :param scroll: Signed scroll amount.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._action, self.owner, scroll, pos)

class ActionOnCollisionBehavior(ObjectBehavior):
    """Invoke callbacks when the owner begins, continues, and ends collisions."""
    def __init__(self, on_collision: Callback[[PygameObject, PygameObject], Any] = None, while_colliding: Callback[[PygameObject, PygameObject], Any] = None, on_collision_end: Callback[[PygameObject, PygameObject], Any] = None,
                 condition_on_other: Optional[Callable[[PygameObject], bool]] = None) -> None:
        """
        Store the collision lifecycle callbacks and other-object filter.

        :param on_collision: Callback invoked when a collision starts.
        :param while_colliding: Callback invoked on every update while colliding.
        :param on_collision_end: Callback invoked when a collision ends.
        :param condition_on_other: Optional predicate that filters which other objects trigger callbacks.
        """
        super().__init__()

        self._on_collision_action = on_collision
        self._while_colliding_action = while_colliding
        self._on_collision_end_action = on_collision_end

        self._condition_on_other = condition_on_other

        self._colliding_objects: list[PygameObject] = []

    def _validate(self, obj: PygameObject) -> bool:
        return self._condition_on_other is None or self._condition_on_other(obj)

    def on_collision(self, obj: PygameObject) -> None:
        """
        Record a new collision and run the collision-start callback.

        :param obj: Other object involved in the collision.
        """
        if self._validate(obj):
            self._exec(self._on_collision_action, self.owner, obj)
            self._colliding_objects.append(obj)

    def on_update(self, dt: float) -> None:
        """
        Run the while-colliding callback for every active collision.

        :param dt: Seconds elapsed since the previous update.
        """
        if self._colliding_objects:
            for obj in self._colliding_objects:
                self._exec(self._while_colliding_action, self.owner, obj)

    def on_collision_end(self, obj: PygameObject) -> None:
        """
        Forget an ending collision and run the collision-end callback.

        :param obj: Other object whose collision ended.
        """
        if self._validate(obj):
            self._exec(self._on_collision_end_action, self.owner, obj)
            self._colliding_objects.remove(obj)

class ActionOnAttributeChangeBehavior(ObjectBehavior):
    """Invoke a callback when a watched owner attribute changes between updates."""
    def __init__(self, attribute: str, action: Callable[[PygameObject], Any]) -> None:
        """
        Store the watched attribute and the change callback.

        :param attribute: Name of the owner attribute to watch.
        :param action: Callback invoked with the owner when the attribute changes.
        """
        super().__init__()

        self._attribute = attribute
        self._action = action

        self._previous_attribute_value = None

    def on_attach(self) -> None:
        """Record the initial value of the watched attribute."""
        self._previous_attribute_value = getattr(self.owner, self._attribute)

    def on_update(self, dt: float) -> None:
        """
        Compare the watched attribute and run the callback when it changed.

        :param dt: Seconds elapsed since the previous update.
        """
        current_attribute_value = getattr(self.owner, self._attribute)
        if current_attribute_value != self._previous_attribute_value:
            self._exec(self._action, self.owner)
            self._previous_attribute_value = current_attribute_value

# endregion


# region ANIMATION BEHAVIORS

class AnimationOnClickBehavior(ObjectBehavior):
    """Play animations when the owner is clicked and released with a given mouse button."""
    def __init__(self, button: int, click_animation: Optional[Callable[[], Animation]] = None, release_animation: Optional[Callable[[], Animation]] = None) -> None:
        """
        Store the button and animation factories.

        :param button: Mouse button that triggers the animations.
        :param click_animation: Factory returning the animation to play on press.
        :param release_animation: Factory returning the animation to play on release.
        """
        super().__init__()

        self._button = button
        self._click_animation = click_animation
        self._release_animation = release_animation

        self._animation_manager: Optional[AnimationManager] = None

    def on_attach(self) -> None:
        """Cache the animation manager and mark the owner as clickable."""
        if (owner := self.owner) is None: return
        self._animation_manager = owner.services.get_animation_manager()
        owner.add_flag(ObjectFlags.CLICKABLE)

    def on_click(self, button: int, pos: vec2) -> None:
        """
        Play the click animation when the configured button is pressed.

        :param button: Mouse button that was pressed.
        :param pos: Pointer position in world coordinates.
        """
        if not self._animation_manager or not self._click_animation: return
        if button == self._button:
            self._animation_manager.play(self._click_animation())

    def on_release(self, button: int, pos: vec2) -> None:
        """
        Play the release animation when the configured button is released.

        :param button: Mouse button that was released.
        :param pos: Pointer position in world coordinates.
        """
        if not self._animation_manager or not self._release_animation: return
        if button == self._button:
            self._animation_manager.play(self._release_animation())

class AnimationOnHoverBehavior(ObjectBehavior):
    """Play animations when the pointer enters and leaves the owner."""
    def __init__(self, hover_start_animation: Optional[Callable[[], Animation]] = None, hover_end_animation: Optional[Callable[[], Animation]] = None) -> None:
        """
        Store the hover animation factories.

        :param hover_start_animation: Factory returning the animation to play when hovering begins.
        :param hover_end_animation: Factory returning the animation to play when hovering ends.
        """
        super().__init__()

        self._hover_start_animation = hover_start_animation
        self._hover_end_animation = hover_end_animation

        self._animation_manager: Optional[AnimationManager] = None

    def on_attach(self) -> None:
        """Cache the animation manager and mark the owner as clickable."""
        if (owner := self.owner) is None: return
        self._animation_manager = owner.services.get_animation_manager()
        owner.add_flag(ObjectFlags.CLICKABLE)

    def on_hover_start(self) -> None:
        """Play the animation configured for the start of hovering."""
        if not self._animation_manager or not self._hover_start_animation: return
        self._animation_manager.play(self._hover_start_animation())

    def on_hover_end(self) -> None:
        """Play the animation configured for the end of hovering."""
        if not self._animation_manager or not self._hover_end_animation: return
        self._animation_manager.play(self._hover_end_animation())

class AnimationOnAttributeChangeBehavior(ActionOnAttributeChangeBehavior):
    """Play an animation when a watched owner attribute changes."""
    def __init__(self, attribute: str, animation: Optional[Callable[[], Animation]]) -> None:
        """
        Store the watched attribute and animation factory.

        :param attribute: Name of the owner attribute to watch.
        :param animation: Factory returning the animation to play when the attribute changes.
        """
        super().__init__(attribute, lambda o: o.play_animation(animation()))

# endregion


# region ATTRIBUTE BEHAVIORS

class AddToAttributeOnHoverBehavior(AnimationOnHoverBehavior):
    """Add a value to an owner attribute on hover and subtract it when hover ends."""
    def __init__(self, attribute: str, value, duration: float, easing_function: EasingFunctionType) -> None:
        """
        Configure the hover adder animation.

        :param attribute: Name of the owner attribute to animate.
        :param value: Amount added on hover and subtracted on hover end.
        :param duration: Animation duration in seconds.
        :param easing_function: Easing function used for the animation.
        """
        super().__init__(
            lambda: AdderAnimation(self._owner, attribute, value, duration, easing_function),
            lambda: AdderAnimation(self._owner, attribute, -value, duration, easing_function)
        )

class MultiplyAttributeOnHoverBehavior(AnimationOnHoverBehavior):
    """Multiply an owner attribute on hover and restore it with the reciprocal on hover end."""
    def __init__(self, attribute: str, multiplier, duration: float, easing_function: EasingFunctionType) -> None:
        """
        Configure the hover multiplier animation.

        :param attribute: Name of the owner attribute to animate.
        :param multiplier: Factor applied on hover and inverted on hover end.
        :param duration: Animation duration in seconds.
        :param easing_function: Easing function used for the animation.
        """
        super().__init__(
            lambda: MultiplierAnimation(self._owner, attribute, multiplier, duration, easing_function),
            lambda: MultiplierAnimation(self._owner, attribute, 1 / multiplier, duration, easing_function)
        )

class SetAttributeOnHoverBehavior(AnimationOnHoverBehavior):
    """Animate an owner attribute to an end value on hover and back to its start value when hover ends."""
    def __init__(self, attribute: str, start_value, end_value, duration: float, easing_function: EasingFunctionType) -> None:
        """
        Configure the hover setter animation.

        :param attribute: Name of the owner attribute to animate.
        :param start_value: Value used when not hovered.
        :param end_value: Value used while hovered.
        :param duration: Animation duration in seconds.
        :param easing_function: Easing function used for the animation.
        """
        super().__init__(
            lambda: SetterAnimation(self._owner, attribute, end_value, duration, easing_function, start_value),
            lambda: SetterAnimation(self._owner, attribute, start_value, duration, easing_function, end_value)
        )


class AddToAttributeOnClickBehavior(AnimationOnClickBehavior):
    """Add a value to an owner attribute on click and subtract it again on release."""
    def __init__(self, button: int, attribute: str, value, duration: float, easing_function: EasingFunctionType) -> None:
        """
        Configure the click adder animation.

        :param button: Mouse button that triggers the animation.
        :param attribute: Name of the owner attribute to animate.
        :param value: Amount added on press and subtracted on release.
        :param duration: Animation duration in seconds.
        :param easing_function: Easing function used for the animation.
        """
        super().__init__(button,
                         lambda: AdderAnimation(self._owner, attribute, value, duration, easing_function),
                         lambda: AdderAnimation(self._owner, attribute, -value, duration, easing_function)
                         )

class MultiplyAttributeOnClickBehavior(AnimationOnClickBehavior):
    """Multiply an owner attribute on click and restore it with the reciprocal on release."""
    def __init__(self, button: int, attribute: str, multiplier, duration: float, easing_function: EasingFunctionType) -> None:
        """
        Configure the click multiplier animation.

        :param button: Mouse button that triggers the animation.
        :param attribute: Name of the owner attribute to animate.
        :param multiplier: Factor applied on press and inverted on release.
        :param duration: Animation duration in seconds.
        :param easing_function: Easing function used for the animation.
        """
        super().__init__(button,
                         lambda: MultiplierAnimation(self._owner, attribute, multiplier, duration, easing_function),
                         lambda: MultiplierAnimation(self._owner, attribute, 1 / multiplier, duration, easing_function)
                         )

class SetAttributeOnClickBehavior(AnimationOnClickBehavior):
    """Animate an owner attribute to an end value on click and back to its start value on release."""
    def __init__(self, button: int, attribute: str, start_value, end_value, duration: float, easing_function: EasingFunctionType) -> None:
        """
        Configure the click setter animation.

        :param button: Mouse button that triggers the animation.
        :param attribute: Name of the owner attribute to animate.
        :param start_value: Value used before the click animation.
        :param end_value: Value used while the button is held.
        :param duration: Animation duration in seconds.
        :param easing_function: Easing function used for the animation.
        """
        super().__init__(button,
                         lambda: SetterAnimation(self._owner, attribute, end_value, duration, easing_function, start_value),
                         lambda: SetterAnimation(self._owner, attribute, start_value, duration, easing_function, end_value)
                         )


class DynamicAttributeBehavior(ObjectBehavior):
    """Update an owner attribute every tick from a value or getter, optionally through a template."""
    def __init__(self, attribute: str, value_getter: ValueOrGetter[Any], template: Optional[str] = None, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr) -> None:
        """
        Store the attribute, value source, and optional formatting options.

        :param attribute: Name of the owner attribute to update.
        :param value_getter: Literal value or callable that produces the new value.
        :param template: Optional format string applied to the evaluated value.
        :param strength: Interpolation strength between the current and target value.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        """
        super().__init__()

        self._attribute = attribute
        self._value_getter = value_getter
        self._template = template

        self._strength = strength

        self._get_attr = attr_getter
        self._set_attr = attr_setter

    def on_update(self, dt: float) -> None:
        """
        Evaluate the value source and write the resulting attribute value.

        :param dt: Seconds elapsed since the previous update.
        """
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
    """Snap an owner attribute to the nearest value in a list every tick."""
    def __init__(self, attribute: str, values: list[float], offset: float = 0, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr) -> None:
        """
        Store the snap targets and interpolation options.

        :param attribute: Name of the owner attribute to snap.
        :param values: Candidate values to snap to.
        :param offset: Offset added to the attribute before choosing a target.
        :param strength: Interpolation strength between the current and snapped value.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        """
        super().__init__()

        self._attribute = attribute
        self._values = values
        self._offset = offset

        self._strength = strength

        self._get_attr = attr_getter
        self._set_attr = attr_setter

    def on_update(self, dt: float) -> None:
        """
        Snap the attribute to its nearest configured value.

        :param dt: Seconds elapsed since the previous update.
        """
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        value = min(self._values, key=lambda x: abs(x - (attr_value + self._offset)))

        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)

        self._set_attr(owner, self._attribute, value)

class AttributeGridSnappingBehavior(ObjectBehavior):
    """Snap an owner attribute to the nearest multiple of a grid step every tick."""
    def __init__(self, attribute: str, step: float, offset: float = 0, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr) -> None:
        """
        Store the grid step and interpolation options.

        :param attribute: Name of the owner attribute to snap.
        :param step: Grid step used for snapping.
        :param offset: Offset applied to the grid.
        :param strength: Interpolation strength between the current and snapped value.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        """
        super().__init__()
        self._attribute = attribute

        self._step = step
        self._offset = offset

        self._strength = strength

        self._get_attr = attr_getter
        self._set_attr = attr_setter

    def on_update(self, dt: float) -> None:
        """
        Snap the attribute to the nearest grid multiple.

        :param dt: Seconds elapsed since the previous update.
        """
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        value = round((attr_value - self._offset) / self._step) * self._step + self._offset

        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)

        self._set_attr(owner, self._attribute, value)

class AttributeClampingBehavior(ObjectBehavior):
    """Clamp an owner attribute between optional minimum and maximum bounds every tick."""
    def __init__(self, attribute: str, min_value: Optional[float | Callable[[],  float]] = None, max_value: Optional[float | Callable[[],  float]] = None, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr) -> None:
        """
        Store the clamp bounds and interpolation options.

        :param attribute: Name of the owner attribute to clamp.
        :param min_value: Lower bound or callable returning it.
        :param max_value: Upper bound or callable returning it.
        :param strength: Interpolation strength between the current and clamped value.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        """
        super().__init__()
        self._attribute = attribute

        self._min_value = -inf if min_value is None else min_value
        self._max_value = inf if max_value is None else max_value
        self._strength = strength

        self._get_attr = attr_getter
        self._set_attr = attr_setter

    def on_update(self, dt: float) -> None:
        """
        Clamp the attribute to the current bounds.

        :param dt: Seconds elapsed since the previous update.
        """
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)

        current_min = self._evaluate(self._min_value)
        current_max = self._evaluate(self._max_value)

        target_value = clamp(attr_value, current_min, current_max)

        if 0 < self._strength < 1:
            target_value = lerp(attr_value, target_value, self._strength)

        self._set_attr(owner, self._attribute, target_value)

class AttributeFixingBehavior(ObjectBehavior):
    """Force an owner attribute to a fixed value or getter result every tick."""
    def __init__(self, attribute: str, value: Optional[Any | Callable[[], Any]] = None, strength: float = 1,
                 attr_getter: Callable[[PygameObject, str], Any] = getattr, attr_setter: Callable[[PygameObject, str, Any], Any] = setattr) -> None:
        """
        Store the fixed value and interpolation options.

        :param attribute: Name of the owner attribute to fix.
        :param value: Fixed value or callable returning it.
        :param strength: Interpolation strength between the current and fixed value.
        :param attr_getter: Callable used to read the attribute.
        :param attr_setter: Callable used to write the attribute.
        """
        super().__init__()
        self._attribute = attribute
        self._value = value

        self._strength = strength

        self._get_attr = attr_getter
        self._set_attr = attr_setter

    def on_attach(self) -> None:
        """Capture the current attribute value when no explicit value was supplied."""
        self._value = self._value if self._value is not None else getattr(self.owner, self._attribute)

    def on_update(self, dt: float) -> None:
        """
        Move the attribute toward its fixed value.

        :param dt: Seconds elapsed since the previous update.
        """
        if (owner := self.owner) is None: return

        attr_value = self._get_attr(owner, self._attribute)
        value = self._evaluate(self._value)

        if 0 < self._strength < 1:
            value = lerp(attr_value, value, self._strength)
        self._set_attr(owner, self._attribute, value)

# endregion