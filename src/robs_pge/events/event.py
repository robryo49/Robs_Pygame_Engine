

class Event:
    def __init__(self, event_type: str, **kwargs):
        self._type = event_type
        self._data = kwargs
        
    @property
    def type(self):
        return self._type

    @property
    def data(self):
        return self._data
    
    def __getattr__(self, item):
        return self._data.get(item)
    
    def __getitem__(self, item):
        return self._data.get(item)
    
    def is_of_type(self, event_type: str):
        return self.type == event_type

    