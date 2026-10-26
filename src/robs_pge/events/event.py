"""Provides an event payload with string identity and arbitrary keyword data."""

from __future__ import annotations

from typing import Any


class Event:
    """Lightweight event payload with arbitrary keyword data."""

    def __init__(self, event_type: str, **kwargs: Any) -> None:
        """Create an event with a type and optional payload fields.

        :param event_type: Event type identifier.
        :param kwargs: Arbitrary payload values exposed as attributes or items.
        """
        self._type = event_type
        self._data = kwargs

    @property
    def type(self) -> str:
        """Return the event type identifier."""
        return self._type

    @property
    def data(self) -> dict[str, Any]:
        """Return the event payload data."""
        return self._data

    def __getattr__(self, item: str) -> Any:
        """Return a payload value by name, or None when the name is absent.

        :param item: Payload field name.
        :return: The payload value, or None when the field is absent.
        """
        return self._data.get(item)

    def __getitem__(self, item: str) -> Any:
        """Return a payload value by key, or None when the key is absent.

        :param item: Payload field name.
        :return: The payload value, or None when the field is absent.
        """
        return self._data.get(item)

    def is_of_type(self, *event_type: str) -> bool:
        """Return whether this event matches any supplied type.

        :param event_type: Event type identifiers to compare against.
        :return: True if the event type matches any supplied identifier.
        """
        return any(self.type == candidate for candidate in event_type)

    @staticmethod
    def are_equal(first: str | Event, second: str | Event) -> bool:
        """Return whether two event values refer to the same event type.

        :param first: Event or event type identifier.
        :param second: Event or event type identifier.
        :return: True if both values refer to the same event type.
        """
        first_type = first if isinstance(first, str) else first.type
        second_type = second if isinstance(second, str) else second.type
        return first_type == second_type

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"Event({self.type!r}, {self.data!r})"
