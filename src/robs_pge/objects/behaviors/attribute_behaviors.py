"""Behaviors that react to events, input, collisions, and attribute changes on pygame objects."""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .behavior import ObjectBehavior
from .animation_behaviors import AnimationOnHoverBehavior, AnimationOnClickBehavior
from ...animation import AdderAnimation, MultiplierAnimation, SetterAnimation
from ...utils import clamp, inf, lerp, EasingFunctionType, ValueOrGetter

if TYPE_CHECKING:
    from ...objects import PygameObject


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

