from typing import Any, Callable, Dict, List, Optional

from .event import Event
from ..utils import Callback


class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[tuple[Callback[[Event], Any], Optional[Callable[[Event], bool]]]]] = {}
        self._queue: List[Event] = []
        
        self._historic: list[tuple[Event, float]] = []
        self._max_historic_size: int = 10
        self._max_historic_time: float = 10

    def register(self, event_type: str, callback: Callback[[Event], Any], condition: Optional[Callable[[Event], bool]] = None):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append((callback, condition))

    def trigger(self, event: Event):
        self._queue.append(event)

    def update(self,  dt: float):
        current_queue = self._queue.copy()
        self._queue.clear()
        
        new_historic = []
        for event, t in self._historic:
            if t+ dt < self._max_historic_time:
                new_historic.append((event, t+dt))

        for event in current_queue:
            new_historic.insert(0, (event, 0.0))
            if event.type in self._listeners:
                for callback, condition in self._listeners[event.type]:
                    if condition is None or condition(event):
                        if callback is not None:
                            if isinstance(callback, tuple):
                                for cb in callback:
                                    cb(event)
                            else:
                                callback(event)
        
        self._historic = new_historic[:self._max_historic_size]