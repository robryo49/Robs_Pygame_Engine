import time
from typing import Callable


class FrameTimer:
    def __init__(self):
        self.start_times = {}
        self._times = {}
        
    # region PROPERTIES
    
    @property
    def times(self):
        return self._times
    
    # endregion
    
    def start_step(self, name: str):
        self.start_times[name] = time.time()
        
    def end_step(self, name: str):
        self.times[name] = ((time.time() - self.start_times[name]) + self._times.get(name, 0)) * 0.5
        self.start_times.pop(name)
        
    def time(self, step_name: str,  function: Callable):
        self.start_step(step_name)
        function()
        self.end_step(step_name)
        
    def format(self):
        txt = ""
        for name, t in sorted(self.times.items()):
            txt += f"{name}: {round(t*1000, 2)}ms\n"
        
        return txt