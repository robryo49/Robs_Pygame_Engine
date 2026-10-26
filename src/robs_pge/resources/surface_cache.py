"""Provides a size-bounded least-recently-used cache for generated pygame surfaces."""

from __future__ import annotations

from collections import OrderedDict
from typing import Hashable, Optional

import pygame as pg


class SurfaceCache:
    """LRU cache for generated surfaces, bounded by an approximate byte budget."""

    def __init__(self, max_bytes: int = 2048 * 1024 * 1024) -> None:
        """
        Initialize an empty surface cache.

        :param max_bytes: approximate memory budget in bytes before eviction begins
        """
        self._cache: OrderedDict[Hashable, pg.Surface] = OrderedDict()
        self._max_bytes = max_bytes
        self._total_bytes = 0
    
    # region PROPERTIES
    
    @property
    def size(self) -> int:
        """Return the number of cached surfaces."""
        return len(self._cache)
    
    @property
    def max_bytes(self) -> int:
        """Return the approximate memory budget in bytes."""
        return self._max_bytes
    
    @property
    def memory_bytes(self) -> int:
        """Return the approximate memory currently used by cached surfaces."""
        return self._total_bytes
    
    @property
    def memory_size(self) -> float:
        """Return the approximate memory currently used, in mebibytes."""
        return self._total_bytes / (1024 * 1024)
    
    # endregion
    
    @staticmethod
    def _get_surface_bytes(surface: pg.Surface) -> int:
        return surface.get_bytesize() * surface.get_width() * surface.get_height()
    
    def get(self, key: Hashable) -> Optional[pg.Surface]:
        """
        Return the cached surface for a key and mark it most-recently used.

        :param key: cache key to look up
        :return: the cached surface, or ``None`` when absent
        """
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def has(self, key: Hashable) -> bool:
        """
        Return whether a key is currently cached.

        :param key: cache key to check
        :return: ``True`` if the key is cached
        """
        return key in self._cache

    def add(self, key: Hashable, surface: pg.Surface) -> None:
        """
        Cache a surface under a key, evicting least-recently used entries if needed.

        :param key: cache key to store the surface under
        :param surface: surface to cache
        """
        if key in self._cache:
            return
        
        self._cache[key] = surface
        self._cache.move_to_end(key)
        self._total_bytes += self._get_surface_bytes(surface)
        
        while self._total_bytes > self._max_bytes and self._cache:
            evicted_key, evicted = self._cache.popitem(last=False)
            self._total_bytes -= self._get_surface_bytes(evicted)
