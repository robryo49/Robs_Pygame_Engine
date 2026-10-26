"""Provides smoothed per-step frame timing collection for debug displays."""

import time
from typing import Any, Callable


class FrameTimer:
    """Collects smoothed per-step timings for debug display."""

    def __init__(self) -> None:
        """Initialize empty timing and category storage."""
        self._start_times: dict[str, float] = {}
        self._times: dict[str, float] = {}
        self._categories: dict[str, list[str]] = {}
        
        self._smoothing = 0.9
        
    # region PROPERTIES
    
    @property
    def times(self) -> dict[str, float]:
        """Return the smoothed duration in seconds for each timed step."""
        return self._times
    
    # endregion
    
    def start_step(self, name: str) -> None:
        """Record the start time for a step and register its category.

        :param name: Dotted step name such as ``Update.Events``.
        """
        category = name.rsplit(".", 1)[0]
        if category not in self._categories:
            self._categories[category] = []
        
        if name not in self._categories[category] and "." in name:
            self._categories[category].append(name)
            
        self._start_times[name] = time.perf_counter()
        
        
    def end_step(self, name: str) -> None:
        """Finish a step and update its smoothed duration.

        :param name: Dotted step name previously passed to start_step().
        """
        start = self._start_times.pop(name, None)
        if start is None:
            return
        elapsed = time.perf_counter() - start
        previous = self._times.get(name)
        self._times[name] = (
            elapsed if previous is None
            else elapsed * (1 - self._smoothing) + previous * self._smoothing
        )

    def time(self, step_name: str, function: Callable[[], Any]) -> None:
        """Run a function and record its duration under a step name.

        :param step_name: Dotted step name used for recording the duration.
        :param function: Callable to execute and time.
        """
        self.start_step(step_name)
        try:
            function()
        finally:
            self.end_step(step_name)

    def format(self) -> str:
        """Format a multiline summary of categories and step timings.

        :return: Human-readable timing report.
        """
        txt = []
        for category in self._categories:
            txt.append("{}:".format(category) if category not in self._times else "{} : {:.2f}ms".format(category, self._times[category]*1000))
            
            for step in self._categories[category]:
                name = step.rsplit(".", 1)[-1]
                t = self.times.get(step, 0)
                
                txt.append("    - {}: {:.2f}ms".format(name, t*1000))
                
        return "\n".join(txt)
    
    def get_time(self, step: str) -> float:
        """Return a step's smoothed duration in seconds, or zero if untimed.

        :param step: Dotted step name.
        :return: Smoothed duration in seconds.
        """
        return self._times.get(step, 0.0)

    def get_time_ms(self, step: str) -> float:
        """Return a step's smoothed duration in milliseconds, rounded to two decimals.

        :param step: Dotted step name.
        :return: Smoothed duration in milliseconds.
        """
        return round(self._times.get(step, 0.0) * 1000, 2)
