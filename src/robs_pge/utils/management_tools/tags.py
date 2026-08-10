from enum import IntFlag, auto


class ObjectTags(IntFlag):
    NONE = 0
    OBJECT = auto()
    FLOOR = auto()
    
    