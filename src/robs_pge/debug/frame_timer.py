import time


class FrameTimer:
    def __init__(self):
        self._times: dict[str, float] = {}
        self._starts: dict[str, float] = {}
        
    # region PROPERTIES
    
    @property
    def times(self) -> dict[str, float]:
        return self._times
    
    @property
    def starts(self) -> dict[str, float]:
        return self._starts
        
    # endregion
    
    def reset(self) -> "FrameTimer":
        self.times.clear()
        self.starts.clear()
        return self
        
    def start(self, name: str) -> "FrameTimer":
        self.starts[name] = time.perf_counter()
        return self
        
    def end(self, name: str) -> "FrameTimer":
        if name in self.starts:
            self.times[name] = time.perf_counter() - self.starts[name]
        return self
    
    def get(self, name: str) -> float:
        return self.times.get(name, 0.0)
    