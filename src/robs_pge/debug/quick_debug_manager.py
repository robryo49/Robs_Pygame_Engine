from typing import Any, Callable


class QuickDebugManager:
    def __init__(self):
        
        self._getters: list[tuple[str, str, Callable]] = []
        self._queue: list[tuple[str, str]] = []
        
        self._values: dict[str, str] = {}
    
    def register_listener(self, name: str, getter: Callable, template: str = "{}"):
        self._getters.append((name, template, getter))
    
    def quick_debug(self, name, value: Any) -> None:
        self._queue.append((name, str(value)))
        
        
    def _get_getter_values(self):
        for name, template, getter in self._getters:
            
            v = getter()
            if isinstance(v, tuple) and template.count("{}") == len(v):
                self._values[name] = template.format(*v)
            else:
                self._values[name] = template.format(v)
    
    def _get_queued_values(self):
        for name, value in self._queue:
            self._values[name] = value
            
            
    def clear_queue(self):
        self._queue.clear()
    
    def clear_values(self):
        self._values.clear()
        
    def clear_listeners(self):
        self._getters.clear()
    
    def update_values(self):
        self.clear_values()
        
        self._get_queued_values()
        self._get_getter_values()
        
        self.clear_queue()
    
    def get_values(self):
        return dict(self._values)
