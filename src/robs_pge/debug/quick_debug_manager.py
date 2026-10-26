"""Provides named values and transient messages for a quick debug panel."""

from typing import Any, Callable


class QuickDebugManager:
    """Collect listener-provided and transient string values for debug display."""

    def __init__(self) -> None:
        """Initialize empty listener, queue, and resolved-value storage."""
        
        self._getters: list[tuple[str, str, Callable]] = []
        self._queue: list[tuple[str, str, float]] = []
        
        self._values: dict[str, str] = {}
    
    def register_listener(self, name: str, getter: Callable, template: str = "{}"):
        """Register a value getter for the debug panel.

        :param name: Display name for the value.
        :param getter: Callable that returns the value to display.
        :param template: Format template applied to the getter result.
        """
        self._getters.append((name, template, getter))
    
    def quick_debug(self, name, value: Any, duration: float = 1.0) -> None:
        """Queue a transient value for the debug panel.

        :param name: Display name for the value.
        :param value: Value to display; it is converted to a string.
        :param duration: Seconds to keep the value visible.
        """
        self._queue.append((name, str(value), duration))
        
        
    def _get_getter_values(self):
        """Resolve registered getters into formatted display values."""
        for name, template, getter in self._getters:
            
            v = getter()
            if isinstance(v, tuple) and template.count("{}") == len(v):
                self._values[name] = template.format(*v)
            else:
                self._values[name] = template.format(v)
    
    def _get_queued_values(self):
        for name, value, _ in self._queue:
            self._values[name] = value
            
            
    def clear_queue(self):
        """Remove all queued transient values."""
        self._queue.clear()
    
    def clear_values(self):
        """Remove all resolved display values."""
        self._values.clear()
        
    def clear_listeners(self):
        """Remove all registered value listeners."""
        self._getters.clear()
    
    def update(self, dt: float) -> None:
        """Rebuild display values and age queued transient values.

        :param dt: Elapsed time in seconds.
        """
        self.clear_values()
        
        self._get_queued_values()
        self._get_getter_values()
        
        self._queue = [(name, value, d-dt) for name, value, d in self._queue if d-dt > 0]
    
    def get_values(self):
        """Return a copy of the current display values.

        :return: Mapping of display names to formatted values.
        """
        return dict(self._values)
