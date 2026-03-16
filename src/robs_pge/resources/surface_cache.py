from collections import OrderedDict

from collections import OrderedDict
import pygame as pg

class SurfaceCache:
    def __init__(self, max_bytes: int = 2048 * 1024 * 1024):
        self._cache: OrderedDict = OrderedDict()
        self._max_bytes = max_bytes
        self._total_bytes = 0
    
    # region PROPERTIES
    
    @property
    def size(self) -> int:
        return len(self._cache)
    
    @property
    def max_bytes(self) -> int:
        return self._max_bytes
    
    @property
    def memory_bytes(self) -> int:
        return self._total_bytes
    
    @property
    def memory_size(self) -> float:
        return self._total_bytes / (1024 * 1024)
    
    # endregion
    
    @staticmethod
    def _get_surface_bytes(surface: pg.Surface) -> int:
        return surface.get_bytesize() * surface.get_width() * surface.get_height()
    
    def get(self, key):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None
    
    def has(self, key) -> bool:
        return key in self._cache
    
    def add(self, key, surface: pg.Surface):
        if key in self._cache:
            return
        
        self._cache[key] = surface
        self._cache.move_to_end(key)
        self._total_bytes += self._get_surface_bytes(surface)
        
        while self._total_bytes > self._max_bytes and self._cache:
            key, evicted = self._cache.popitem(last=False)
            self._total_bytes -= self._get_surface_bytes(evicted)
