from typing import Any, Callable


class QuickDebugManager:
    def __init__(self):
        
        self._getters: list[tuple[str, Callable]] = []
        
        self._queue: list[str] = []
    
    def register_listener(self, getter: Callable, template: str = "{}"):
        self._getters.append((template, getter))
    
    def quick_debug(self, *infos: Any) -> None:
        self._queue.append(" ".join(str(info) for info in infos))
        
    def get_getter_values(self) -> list[str]:
        values = []
        for template, getter in self._getters:
            
            v = getter()
            if isinstance(v, tuple) and template.count("{}") == len(v):
                values.append(template.format(*v))
            else:
                values.append(template.format(v))
                
        return values
    
    def clear_queue(self):
        self._queue.clear()
    
    def get_values(self):
        values = self._queue + self.get_getter_values()
        self._queue.clear()
        return values
    
    def has_values(self) -> bool:
        return len(self._queue) > 0 or len(self._getters) > 0
