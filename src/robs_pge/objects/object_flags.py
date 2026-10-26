"""Bit flags for object behavior and keybind activation state."""

from enum import IntFlag, auto


class ObjectFlags(IntFlag):
    """Flags controlling object interaction, rendering, updates, and physics."""

    NONE = 0
    INTERACTABLE = auto()

    _HOVER = auto()
    _CLICK = auto()
    _DRAG = auto()
    _SCROLL = auto()

    HOVERABLE = _HOVER | INTERACTABLE
    CLICKABLE = _CLICK | HOVERABLE
    SCROLLABLE = _SCROLL | HOVERABLE
    DRAGGABLE = _DRAG  | CLICKABLE

    HIDDEN = auto()
    SKIP_RENDERING = auto()

    FROZEN = auto()
    SKIP_UPDATE = auto()

    CULLABLE = auto()

    COLLIDABLE = auto()
    PHYSICS = auto()

