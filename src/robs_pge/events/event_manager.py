from typing import Any, Callable, Dict, List, Optional

from .event import Event


class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[tuple[Callable[[Event], Any], Optional[Callable[[Event], bool]]]]] = {}
        self._queue: List[Event] = []
    
    def register(self, event_type: str, callback: Callable[[Event], Any], condition: Optional[Callable[[Event], bool]] = None):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append((callback, condition))
    
    def trigger(self, event: Event):
        self._queue.append(event)
    
    def update(self):
        current_queue = self._queue.copy()
        self._queue.clear()
        
        for event in current_queue:
            if event.type in self._listeners:
                for callback, condition in self._listeners[event.type]:
                    if condition is None or condition(event):
                        callback(event)
    