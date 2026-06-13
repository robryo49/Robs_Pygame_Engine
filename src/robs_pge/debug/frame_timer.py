import time
from typing import Callable


class FrameTimer:
    def __init__(self):
        self._start_times = {}
        self._times = {}
        self._categories = {}
        
        self._smoothing = 0.9
        
    # region PROPERTIES
    
    @property
    def times(self):
        return self._times
    
    # endregion
    
    def start_step(self, name: str):
        category = name.rsplit(".", 1)[0]
        if category not in self._categories:
            self._categories[category] = []
        
        if name not in self._categories[category] and "." in name:
            self._categories[category].append(name)
            
        self._start_times[name] = time.time()
        
        
    def end_step(self, name: str):
        self.times[name] = (time.time() - self._start_times[name]) * (1 - self._smoothing) + self._times.get(name, 0) * self._smoothing
        self._start_times.pop(name)
        
    def time(self, step_name: str,  function: Callable):
        self.start_step(step_name)
        function()
        self.end_step(step_name)
        
    def format(self):
        txt = []
        for category in self._categories:
            txt.append("{}:".format(category) if category not in self._times else "{} : {:.2f}ms".format(category, self._times[category]*1000))
            
            for step in self._categories[category]:
                name = step.rsplit(".", 1)[-1]
                t = self.times.get(step, 0)
                
                txt.append("    - {}: {:.2f}ms".format(name, t*1000))
                
        return "\n".join(txt)
    
    def get_time(self, step):
        return self.times.get(step, 0)
    
    def get_time_ms(self, step):
        return round(self.times.get(step, 0)*1000, 2)