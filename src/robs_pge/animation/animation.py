"""Defines tween-based animations that mutate object attributes over time."""

from __future__ import annotations

from typing import Any, Optional

from .tween import Tween
from ..utils import Easing, EasingFunctionType, add, multiply, power, subtract, Callback


class Animation:
    """Animates a named attribute from its current value over a duration."""

    def __init__(self, obj: object, attr: str, duration: float, easing_function: EasingFunctionType = Easing.LINEAR) -> None:
        """
        Initialize an animation targeting an object attribute.

        :param obj: object containing the attribute to animate
        :param attr: name of the attribute to animate
        :param duration: duration of the animation in seconds
        :param easing_function: easing function applied to the animation progress
        """
        self._obj = obj
        self._attr = attr
        self._tween = Tween(duration, easing_function)

        self._linked_animations: list[tuple[Animation, float]] = []
        self._linked_callbacks: list[tuple[Callback[..., Any], float]] = []

    @property
    def obj(self) -> object:
        """Return the object containing the animated attribute."""
        return self._obj

    @property
    def attr(self) -> str:
        """Return the name of the animated attribute."""
        return self._attr

    @property
    def duration(self) -> float:
        """Return the duration of the animation in seconds."""
        return self.tween.duration

    @property
    def tween(self) -> Tween:
        """Return the tween tracking the animation progress."""
        return self._tween

    @property
    def linked_animations(self) -> list[tuple[Animation, float]]:
        """Return the animations scheduled relative to this animation, with their delay times."""
        return self._linked_animations

    @property
    def linked_callbacks(self) -> list[tuple[Callback[..., Any], float]]:
        """Return the callbacks scheduled relative to this animation, with their delay times."""
        return self._linked_callbacks

    @property
    def finished(self) -> bool:
        """Return whether the animation has reached its full duration."""
        return self.tween.finished

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"Animation({self.obj}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"

    def followed_by(self, anim: Animation, delay: float = 0.0) -> Animation:
        """
        Schedule another animation to start after this one finishes.

        :param anim: animation to schedule
        :param delay: additional delay after this animation ends before the other starts
        :return: this animation
        """
        self._linked_animations.append((anim, self.duration + delay))
        return self

    def plus(self, anim: Animation, delay: float = 0.0) -> Animation:
        """
        Schedule another animation to start alongside this one.

        :param anim: animation to schedule
        :param delay: delay after this animation starts before the other starts
        :return: this animation
        """
        self._linked_animations.append((anim, delay))
        return self

    def with_end_callback(self, callback: Callback[[], Any], delay: float = 0.0) -> Animation:
        """
        Register a callback to run relative to this animation's end.

        :param callback: callback to execute
        :param delay: additional delay after this animation ends before the callback runs
        :return: this animation
        """
        self._linked_callbacks.append((callback, self.duration + delay))
        return self

    def with_start_callback(self, callback: Callback[[], Any], delay: float = 0.0) -> Animation:
        """
        Register a callback to run relative to this animation's start.

        :param callback: callback to execute
        :param delay: delay after this animation starts before the callback runs
        :return: this animation
        """
        self._linked_callbacks.append((callback, delay))
        return self

    def set_attr(self, value: Any) -> None:
        """
        Set the animated attribute to a value.

        :param value: value to assign to the attribute
        """
        setattr(self.obj, self.attr, value)

    def get_attr(self) -> Any:
        """
        Return the current value of the animated attribute.

        :return: the attribute's current value
        """
        return getattr(self.obj, self.attr)

    def update(self, dt: float) -> None:
        """
        Advance the underlying tween.

        :param dt: elapsed time in seconds
        """
        self.tween.step(dt)

    def start(self) -> None:
        """Restart the tween."""
        self.tween.reset()


class AdderAnimation(Animation):
    """Animates an attribute by adding a fixed value over time."""

    def __init__(self, obj: object, attr: str, value: Any, duration: float, easing_function: EasingFunctionType = Easing.LINEAR) -> None:
        """
        Initialize an additive animation.

        :param obj: object containing the attribute to animate
        :param attr: name of the attribute to animate
        :param value: amount added to the attribute over the animation
        :param duration: duration of the animation in seconds
        :param easing_function: easing function applied to the animation progress
        """
        super().__init__(obj, attr, duration, easing_function)
        self._adder = value
        self._start_value = self.get_attr()
        self._end_value = add(self.start_value, self._adder)

    @property
    def start_value(self) -> Any:
        """Return the attribute value when the animation started."""
        return self._start_value

    @property
    def end_value(self) -> Any:
        """Return the attribute value when the animation finishes."""
        return self._end_value

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"AdderAnimation({self.obj}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"

    def get_inverse(self) -> AdderAnimation:
        """
        Return an animation that applies the opposite change.

        :return: an additive animation with the negated value
        """
        return AdderAnimation(
            self.obj,
            self.attr,
            multiply(self._adder, -1),
            self.duration,
            self.tween.easing_function,
        )

    def start(self) -> None:
        """Restart the tween and recapture the start and end values."""
        super().start()
        self._start_value = self.get_attr()
        self._end_value = add(self.start_value, self._adder)

    def update(self, dt: float) -> None:
        """
        Advance the animation and add the elapsed portion of the value.

        :param dt: elapsed time in seconds
        """
        progress_delta = self.tween.step(dt)
        self.set_attr(add(self.get_attr(), multiply(self._adder, progress_delta)))


class SetterAnimation(AdderAnimation):
    """Animates an attribute to a target value."""

    def __init__(self, obj: object, attr: str, value: Any, duration: float, easing_function: EasingFunctionType = Easing.LINEAR, start_value: Optional[Any] = None) -> None:
        """
        Initialize a setter animation.

        :param obj: object containing the attribute to animate
        :param attr: name of the attribute to animate
        :param value: target value for the attribute
        :param duration: duration of the animation in seconds
        :param easing_function: easing function applied to the animation progress
        :param start_value: optional value to start from instead of the attribute's current value
        """
        super().__init__(
            obj,
            attr,
            subtract(value, getattr(obj, attr)),
            duration,
            easing_function,
        )
        self._target = value
        self._forced_start_value = start_value

    @property
    def target(self) -> Any:
        """Return the target value for the animated attribute."""
        return self._target

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"SetterAnimation({self.obj}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"

    def start(self) -> None:
        """Restart the tween and recompute the change needed to reach the target."""
        current = self.get_attr() if self._forced_start_value is None else self._forced_start_value
        self._adder = subtract(self.target, current)
        super().start()


class MultiplierAnimation(Animation):
    """Animates an attribute by multiplying it by a factor over time."""

    def __init__(self, obj: object, attr: str, value: Any, duration: float, easing_function: EasingFunctionType = Easing.LINEAR) -> None:
        """
        Initialize a multiplicative animation.

        :param obj: object containing the attribute to animate
        :param attr: name of the attribute to animate
        :param value: factor by which the attribute is multiplied over the animation
        :param duration: duration of the animation in seconds
        :param easing_function: easing function applied to the animation progress
        """
        super().__init__(obj, attr, duration, easing_function)
        self._multiplier = value
        self._start_value = self.get_attr()
        self._end_value = multiply(self.start_value, self._multiplier)

    @property
    def start_value(self) -> Any:
        """Return the attribute value when the animation started."""
        return self._start_value

    @property
    def end_value(self) -> Any:
        """Return the attribute value when the animation finishes."""
        return self._end_value

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"MultiplierAnimation({self.obj}.{self.attr}, {round(self.tween.time, 2)}/{round(self.duration, 2)})"

    def get_inverse(self) -> MultiplierAnimation:
        """
        Return an animation that applies the inverse multiplier.

        :return: a multiplicative animation with the reciprocal factor
        :raises ValueError: if the multiplier is zero
        """
        if self._multiplier == 0:
            raise ValueError("Cannot invert a multiplier animation with a zero multiplier")
        return MultiplierAnimation(
            self.obj,
            self.attr,
            1 / self._multiplier,
            self.duration,
            self.tween.easing_function,
        )

    def start(self) -> None:
        """Restart the tween and recapture the start and end values."""
        super().start()
        self._start_value = self.get_attr()
        self._end_value = multiply(self.start_value, self._multiplier)

    def update(self, dt: float) -> None:
        """
        Advance the animation and multiply the attribute by the elapsed portion of the factor.

        :param dt: elapsed time in seconds
        """
        factor = power(self._multiplier, self.tween.step(dt))
        self.set_attr(multiply(self.get_attr(), factor))
