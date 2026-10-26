"""Provides string constants for built-in engine event types."""


class Events:
    """Collect the built-in event type identifiers used by the engine."""

    WINDOW_OPENED ="window_opened"
    WINDOW_CLOSED = "window_closed"
    STATE_ENTER = "state_enter"
    STATE_EXIT = "state_exit"

    COLLISION_BEGIN = "collision_begin"
    COLLISION_END = "collision_end"
    TRIGGER_ENTER = "trigger_enter"
    TRIGGER_EXIT = "trigger_exit"

