import time


class FrameTimer:
    def __init__(self):
        self._times: dict[str, float] = {}
        self._starts: dict[str, float] = {}
        
    # region PROPERTIES
    
    @property
    def times(self):
        return self._times
    
    @property
    def starts(self):
        return self._starts
        
    # endregion
    
    def reset(self):
        self.times.clear()
        self.starts.clear()
        
    def start(self, name: str):
        self.starts[name] = time.perf_counter()
        
    def end(self, name: str):
        if name in self.starts:
            self.times[name] = time.perf_counter() - self.starts[name]
    
    def get(self, name: str):
        return self.times.get(name, 0.0)