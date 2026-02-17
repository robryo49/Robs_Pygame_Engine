from enum import IntFlag, auto



class ObjectFlags(IntFlag):
    NONE = 0
    INTERACTABLE = auto()
    
    _HOVER = auto()
    _CLICK = auto()
    _DRAG = auto()
    
    HOVERABLE = _HOVER | INTERACTABLE
    CLICKABLE = _CLICK | HOVERABLE
    DRAGGABLE = _DRAG  | CLICKABLE
    
    VISIBLE = auto()
    CULLABLE = auto()
    SKIP_RENDERING = auto()


class KeybindFlags(IntFlag):
    PRESS = auto()
    HOLD = auto()
    RELEASE = auto()


