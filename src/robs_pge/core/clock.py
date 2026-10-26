"""Provides a frame clock that tracks elapsed time, delta time, and FPS."""

import pygame as pg


class Clock:
    """Track frame timing and accumulated runtime for the engine."""

    def __init__(self) -> None:
        """Initialize the clock with a 60 FPS default step."""
        self._clock: pg.time.Clock = pg.time.Clock()
        
        self._time: float = 0
        self._tick_num: int = 0
        
        self._fps: float = 60
        self._dtime: float = 1/60
    
    # region PROPERTIES
    
    @property
    def clock(self) -> pg.time.Clock:
        """Return the underlying pygame clock."""
        return self._clock
    
    @property
    def time(self) -> float:
        """Return the total elapsed time in seconds."""
        return self._time
    
    @property
    def tick_num(self) -> int:
        """Return the number of completed ticks."""
        return self._tick_num
    
    @property
    def fps(self) -> float:
        """Return the measured frames per second."""
        return self._fps
    
    @property
    def dtime(self) -> float:
        """Return the duration of the last tick in seconds."""
        return self._dtime
    
    # endregion
    
    def tick(self) -> "Clock":
        """Advance the clock and update timing values.

        :return: This clock for chaining.
        """
        self._clock.tick(120)
        self._dtime = self.clock.get_time() / 1000
        self._time += self.dtime
        self._tick_num += 1
        self._fps = self.clock.get_fps()
        
        return self

