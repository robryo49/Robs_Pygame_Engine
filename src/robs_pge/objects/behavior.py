from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from ..events import Event
from ..utils import vec2

if TYPE_CHECKING:
    from ..objects import PygameObject


class ObjectBehavior:
    def __init__(self):
        self._owner: Optional[PygameObject] = None
    
    # region PROPERTIES
    
    # region object
    @property
    def owner(self):
        return self._owner
    
    @owner.setter
    def owner(self, value):
        self._owner = value
    # endregion
    
    # endregion
    
    def _exec(self, action: Optional[Callable | tuple[Callable, ...]], *args, **kwargs) -> None:
        if action is not None:
            if isinstance(action, tuple):
                for action in action:
                    self._exec(action, *args, **kwargs)
            else:
                action(*args, **kwargs)
    
    @staticmethod
    def _evaluate(val_or_getter):
        return val_or_getter() if callable(val_or_getter) else val_or_getter
    
    def on_click(self, button: int, pos: vec2): pass
    def on_hold(self, button: int, pos: vec2): pass
    def on_release(self, button: int, pos: vec2): pass
    
    def on_hover_start(self): pass
    def on_hover(self): pass
    def on_hover_end(self): pass
    
    def on_event(self, event: Event): pass
    
    def on_attach(self): pass
    def on_detach(self): pass
    
    def on_update(self, dt: float): pass
    
    def on_scroll(self, scroll: int, pos: vec2): pass
    
    def on_collision(self, obj: PygameObject):
        pass
    def on_collision_end(self, obj: PygameObject):
        pass