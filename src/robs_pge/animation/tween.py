"""Tracks normalized progress over a fixed duration with configurable easing."""

from __future__ import annotations

from ..utils import Easing, EasingFunctionType, clamp


class Tween:
    """Tracks normalized animation progress over a duration."""

    def __init__(self, duration: float, easing_function: EasingFunctionType = Easing.LINEAR) -> None:
        """
        Initialize a tween.

        :param duration: total duration in seconds
        :param easing_function: easing function applied to the linear progress
        """
        self._duration = duration
        self._easing_function = easing_function

        self._time = 0.0
        self._progress = 0.0

    @property
    def duration(self) -> float:
        """Return the total duration in seconds."""
        return self._duration

    @property
    def time(self) -> float:
        """Return the elapsed time in seconds."""
        return self._time

    @property
    def progress(self) -> float:
        """Return the eased progress from 0 to 1."""
        return self._progress

    @property
    def easing_function(self) -> EasingFunctionType:
        """Return the easing function applied to the linear progress."""
        return self._easing_function

    @property
    def finished(self) -> bool:
        """Return whether the elapsed time has reached the duration."""
        return self._time >= self._duration

    def reset(self) -> None:
        """Restart the tween."""
        self._time = 0.0
        self._progress = 0.0

    def step(self, dt: float) -> float:
        """
        Advance the tween and return the change in eased progress.

        :param dt: elapsed time in seconds
        :return: the progress delta since the previous step
        """
        self._time += dt
        raw_progress = 1.0 if self._duration <= 0 else clamp(self._time / self._duration)
        previous_progress = self._progress
        self._progress = self._easing_function(raw_progress)
        return self._progress - previous_progress
