"""Provides an event queue that dispatches listeners and retains recent history."""

from __future__ import annotations

from typing import Any, Optional, Callable

from .event import Event
from ..utils import Callback


class EventManager:
    """Queues, dispatches, and retains recent events."""

    def __init__(self) -> None:
        """Initialize empty listener, queue, and history storage."""
        self._listeners: dict[str, list[tuple[Callback[[Event], Any], Optional[Callable[[Event], bool]]]]] = {}
        self._queue: list[Event] = []

        self._historic: list[tuple[Event, float]] = []
        self._max_historic_size: int = 10
        self._max_historic_time: float = 10.0

    @property
    def historic(self) -> list[tuple[Event, float]]:
        """Return recent events paired with their age in seconds."""
        return self._historic

    def register(
        self,
        event_type: str,
        callback: Callback[[Event], Any],
        condition: Optional[Callable[[Event], bool]] = None,
    ) -> EventManager:
        """Register a callback for an event type.

        :param event_type: Event type identifier to listen for.
        :param callback: Callback invoked with the matching event.
        :param condition: Optional predicate that must return True before dispatch.
        :return: This manager for chaining.
        """
        listeners = self._listeners.setdefault(event_type, [])
        if not any(existing_callback is callback for existing_callback, _ in listeners):
            listeners.append((callback, condition))
        return self

    def trigger(self, event: Event) -> EventManager:
        """Queue an event for the next update.

        :param event: Event to queue.
        :return: This manager for chaining.
        """
        self._queue.append(event)
        return self

    def update(self, dt: float) -> EventManager:
        """Dispatch queued events and age historic events.

        :param dt: Elapsed time in seconds.
        :return: This manager for chaining.
        """
        current_queue = self._queue.copy()
        self._queue.clear()

        new_historic: list[tuple[Event, float]] = []
        for event, age in self._historic:
            if age + dt < self._max_historic_time:
                new_historic.append((event, age + dt))

        for event in current_queue:
            new_historic.insert(0, (event, 0.0))
            for callback, condition in tuple(self._listeners.get(event.type, ())):
                if condition is not None and not condition(event):
                    continue
                self._invoke_callback(callback, event)

        self._historic = new_historic[: self._max_historic_size]
        return self

    @staticmethod
    def _invoke_callback(callback: Callback[[Event], Any], event: Event) -> None:
        """Invoke a callback, or each callback in a tuple, with the event.

        :param callback: Single callback or tuple of callbacks.
        :param event: Event passed to each callback.
        """
        if callback is None:
            return
        if isinstance(callback, tuple):
            for item in callback:
                item(event)
        else:
            callback(event)

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"EventManager(listeners={len(self._listeners)}, queued={len(self._queue)})"
