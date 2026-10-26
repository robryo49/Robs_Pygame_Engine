"""Bit flags for classifying game objects."""

from enum import IntFlag, auto


class ObjectTags(IntFlag):
    """Tags identifying broad object categories."""

    NONE = 0
    OBJECT = auto()
    FLOOR = auto()
    
    