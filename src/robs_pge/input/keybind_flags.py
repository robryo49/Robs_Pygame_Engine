"""Bit flags for object behavior and keybind activation state."""

from enum import IntFlag, auto


class KeybindFlags(IntFlag):
    """Flags describing keybind activation phases."""

    PRESS = auto()
    HOLD = auto()
    RELEASE = auto()


