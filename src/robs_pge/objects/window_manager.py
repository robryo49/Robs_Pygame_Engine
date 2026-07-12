from typing import Optional

from ..events import EventManager, Events, Event
from ..objects import PygameObject
from ..utils import DictCollection


class WindowManager:
    def __init__(self, event_manager: EventManager):
        self._event_manager = event_manager
        self._windows: DictCollection = DictCollection()
        self._groups: dict[str, set[str]] = {}
    
    @property
    def windows(self):
        return self._windows
    
    def register(self, window_id: str, window: PygameObject, group: Optional[str] = None):
        self._windows.set(window_id, window)
        window.hide()
        if group:
            self._groups.setdefault(group, set()).add(window_id)
        return self
    
    def is_open(self, window_id: str) -> bool:
        win = self._windows.get(window_id)
        return win is not None and win.visible
    
    def open(self, window_id: str):
        window = self._windows.get(window_id)
        if window is None:
            return self
        
        for group, ids in self._groups.items():
            if window_id in ids:
                for other_id in ids:
                    if other_id != window_id:
                        self.close(other_id)
        
        window.show()
        self._event_manager.trigger(Event(Events.WINDOW_OPENED, window_id=window_id))
        return self
    
    def close(self, window_id: str):
        window = self._windows.get(window_id)
        if window is not None and window.visible:
            window.hide()
            self._event_manager.trigger(Event(Events.WINDOW_CLOSED, window_id=window_id))
        return self
    
    def toggle(self, window_id: str):
        self.close(window_id) if self.is_open(window_id) else self.open(window_id)
        return self
    
    def close_all(self):
        for window_id in self._windows.keys:
            self.close(window_id)
        return self

