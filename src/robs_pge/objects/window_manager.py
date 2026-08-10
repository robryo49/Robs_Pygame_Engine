from typing import Optional

from ..events import Event, EventManager, Events
from ..objects import WindowObject
from ..utils import ObjectFlags, TypedDictCollection


class WindowManager:
    def __init__(self, event_manager: EventManager):
        self._event_manager = event_manager
        self._windows = TypedDictCollection(str, WindowObject)
        self._groups: dict[str, set[str]] = {}
        self._window_group: dict[str, str] = {}
    
    # region PROPERTIES
    
    @property
    def windows(self):
        return self._windows
    
    # endregion
    
    def register(self, window: WindowObject, group: Optional[str] = None) -> WindowObject:
        window_id = window.id
        self._windows.set(window_id, window)
        window.hide()
        if group:
            self._groups.setdefault(group, set()).add(window_id)
            self._window_group[window_id] = group
        return window
    
    def is_open(self, window_id: str) -> WindowObject:
        win = self._windows.get(window_id)
        return win is not None and win.opened
    
    def open(self, window_id: str) -> WindowObject:
        window = self._windows.get(window_id)
        if window is None:
            raise KeyError(f"Window with id {window_id} does not exist or isn't registered")
        
        group = self._window_group.get(window_id)
        if group is not None:
            for other_id in self._groups[group]:
                if other_id != window_id:
                    self.close(other_id)
        
        window.open()
        self._event_manager.trigger(Event(Events.WINDOW_OPENED, window_id=window_id))
        return window
    
    def close(self, window_id: str) -> WindowObject:
        window = self._windows.get(window_id)
        if window is None:
            raise KeyError(f"Window with id {window_id} does not exist or isn't registered")
        
        if window.opened:
            window.close()
            self._event_manager.trigger(Event(Events.WINDOW_CLOSED, window_id=window_id))
        return window
    
    def toggle(self, window_id: str):
        self.close(window_id) if self.is_open(window_id) else self.open(window_id)
        return self
    
    def close_all(self):
        for window_id in self._windows.keys():
            self.close(window_id)
        return self
    
    def unregister(self, window_id: str) -> WindowObject:
        window = self._windows.get(window_id)
        if window is None:
            raise KeyError(f"Window with id {window_id} does not exist or isn't registered")
        
        group = self._window_group.pop(window_id, None)
        if group is not None:
            self._groups[group].discard(window_id)
            if not self._groups[group]:
                self._groups.pop(group)
        
        self._windows.pop(window_id, None)
        return window
