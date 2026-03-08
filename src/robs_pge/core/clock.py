import pygame as pg


class Clock:
    def __init__(self):
        self._clock: pg.time.Clock = pg.time.Clock()
        
        self._time: float = 0
        self._tick_num: int = 0
        
        self._fps: float = 60
        self._dtime: float = 1/60
    
    # region PROPERTIES
    
    @property
    def clock(self) -> pg.time.Clock:
        return self._clock
    
    @property
    def time(self) -> float:
        return self._time
    
    @property
    def tick_num(self) -> int:
        return self._tick_num
    
    @property
    def fps(self) -> float:
        return self._fps
    
    @property
    def dtime(self) -> float:
        return self._dtime
    
    # endregion
    
    def tick(self) -> "Clock":
        self._clock.tick()
        self._dtime = self.clock.get_time() / 1000
        self._time += self.dtime
        self._tick_num += 1
        self._fps = self.clock.get_fps()
        
        return self

