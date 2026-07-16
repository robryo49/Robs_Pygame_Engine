from __future__ import annotations

import inspect
from typing import Any, Callable, Optional, TYPE_CHECKING, overload

from ..utils import Vec2
from ..events import Event

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
    
    @overload
    def _normalize_action(self, action: Callable[..., Any]) -> Callable[..., Any]: ...
    
    @overload
    def _normalize_action(self, action: tuple[Callable[..., Any], ...]) -> tuple[Callable[..., Any], ...]: ...
    
    @overload
    def _normalize_action(self, action: None) -> None: ...
    
    def _normalize_action(self, action: Callable[..., Any] | tuple[Callable[..., Any], ...] | None) -> Callable[..., Any] | tuple[Callable[..., Any], ...] | None:
        if action is None:
            return None
        elif isinstance(action, tuple):
            return tuple(self._normalize_action(act) for act in action)
        elif len(inspect.signature(action).parameters) == 0:
            return lambda o: action()
        return action
    
    def _exec(self, action: Optional[Callable | tuple[Callable, ...]], *args, **kwargs) -> None:
        if action is not None:
            if isinstance(action, tuple):
                for action in action:
                    self._exec(action, *args, **kwargs)
            else:
                action(*args, **kwargs)
            
    
    def on_click(self, button: int, pos: Vec2): pass
    def on_hold(self, button: int, pos: Vec2): pass
    def on_release(self, button: int, pos: Vec2): pass
    
    def on_hover_start(self): pass
    def on_hover(self): pass
    def on_hover_end(self): pass
    
    def on_event(self, event: Event): pass
    
    def on_attach(self): pass
    def on_detach(self): pass
    
    def on_update(self, dt: float): pass
    
    def on_scroll(self, scroll: int, pos: Vec2): pass