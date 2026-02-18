import pygame as pg


class Clock:
    def __init__(self, target_fps: float):
        self._clock: pg.time.Clock = pg.time.Clock()
        
        self._target_fps: float = target_fps
        self._target_dtime: float = 1/target_fps
        
        self._time: float = 0
        self._tick_num: int = 0
        
        self._fps: float = self._target_fps
        self._dtime: float = self._target_dtime
    
    # region PROPERTIES
    
    @property
    def clock(self) -> pg.time.Clock:
        return self._clock
    
    @property
    def target_fps(self) -> float:
        return self._target_fps
    
    @target_fps.setter
    def target_fps(self, value: float) -> None:
        self._target_fps = value
        self._target_dtime = 1/value
    
    @property
    def target_dtime(self) -> float:
        return self._target_dtime
    
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
        self._clock.tick(self.target_fps)
        self._dtime = self.clock.get_time() / 1000
        self._time += self.dtime
        self._tick_num += 1
        self._fps = self.clock.get_fps()
        
        return self

