from typing import Any, Callable, Dict, List

from .event import Event


class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Event], Any]]] = {}
        self._queue: List[Event] = []
    
    def register_listener(self, event_type: str, callback: Callable[[Event], Any]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
    
    def remover_listener(self, event_type: str, callback: Callable[[Event], Any]):
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)
    
    def trigger(self, event: Event):
        self._queue.append(event)
    
    def update(self):
        current_queue = self._queue.copy()
        self._queue.clear()
        
        for event in current_queue:
            if event.type in self._listeners:
                for callback in self._listeners[event.type]:
                    callback(event)
    