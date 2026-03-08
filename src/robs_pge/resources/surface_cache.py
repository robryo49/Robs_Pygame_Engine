from collections import OrderedDict


class SurfaceCache:
    def __init__(self, max_size=256):
        
        self._cache = OrderedDict()
        self._max_size = max_size
        
    # region PROPERTIES
    
    @property
    def cache(self):
        return self._cache
    
    @property
    def max_size(self):
        return self._max_size
    
    @property
    def size(self):
        return len(self._cache)
    
    # endregion
    
    def get(self, key):
        if self.has(key):
            self._cache.move_to_end(key, False)
            return self._cache[key]
        return None
    
    def add(self, key, surface):
        self._cache[key] = surface
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
    
    def has(self, key):
        return key in self._cache
