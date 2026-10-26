"""Coordinates animation playback and time-delayed animation and callback scheduling."""

from __future__ import annotations

from typing import Any

from .animation import Animation
from ..utils import Callback


class AnimationManager:
    """Updates active animations and schedules delayed animations/callbacks."""

    def __init__(self) -> None:
        """Initialize an animation manager with no active or scheduled work."""
        self._time = 0.0
        self._active_animations: list[Animation] = []
        self._scheduled_animations: list[tuple[Animation, float]] = []
        self._scheduled_callbacks: list[tuple[Callback[..., Any], float]] = []

    @property
    def active(self) -> list[Animation]:
        """Return the animations currently being updated."""
        return self._active_animations

    @property
    def scheduled(self) -> list[tuple[Animation, float]]:
        """Return the animations waiting to start, paired with their start times."""
        return self._scheduled_animations

    @property
    def scheduled_callbacks(self) -> list[tuple[Callback[..., Any], float]]:
        """Return the callbacks waiting to fire, paired with their fire times."""
        return self._scheduled_callbacks

    @property
    def time(self) -> float:
        """Return the total time advanced by the manager, in seconds."""
        return self._time

    def play(self, anim: Animation) -> AnimationManager:
        """
        Schedule an animation to start on the next update.

        :param anim: animation to play
        :return: this manager
        """
        self._scheduled_animations.append((anim, self.time))
        return self

    def update(self, dt: float) -> AnimationManager:
        """
        Advance animations and fire newly due callbacks.

        :param dt: elapsed time in seconds
        :return: this manager
        """
        self._time += dt

        newly_active: list[Animation] = []
        for anim, start_time in tuple(self._scheduled_animations):
            if self.time < start_time:
                continue

            self._scheduled_animations.remove((anim, start_time))
            anim.start()
            anim.update(self.time - start_time)
            self._active_animations.append(anim)
            newly_active.append(anim)

            for linked_anim, delay in anim.linked_animations:
                self._scheduled_animations.append((linked_anim, self.time + delay))

            for linked_callback, delay in anim.linked_callbacks:
                self._scheduled_callbacks.append((linked_callback, self.time + delay))

        for anim in tuple(self._active_animations):
            if anim not in newly_active:
                anim.update(dt)

            if anim.finished:
                self._active_animations.remove(anim)

        pending_callbacks: list[tuple[Callback[..., Any], float]] = []
        for callback, fire_time in self._scheduled_callbacks:
            if self.time >= fire_time:
                self._invoke_callback(callback)
            else:
                pending_callbacks.append((callback, fire_time))
        self._scheduled_callbacks = pending_callbacks
        return self

    @staticmethod
    def _invoke_callback(callback: Callback[..., Any]) -> None:
        """
        Invoke a callback, expanding a tuple of callbacks into individual calls.

        :param callback: callback or tuple of callbacks to invoke
        """
        if isinstance(callback, tuple):
            for item in callback:
                item()
        elif callback is not None:
            callback()
