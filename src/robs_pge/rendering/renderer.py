from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame as pg

from ..rendering import DrawCommand
from ..resources import SurfaceCache
from ..utils import Vec2

if TYPE_CHECKING:
    from ..core import Camera, Display


class Renderer:
    def __init__(self, display: Display, default_camera: Camera, max_cache_size: int = 2048 * 1024 * 1024):
        
        self._display: Display = display
        self._default_camera: Camera = default_camera
        
        self._surface_cache: SurfaceCache = SurfaceCache(max_cache_size)
        self._font_cache: dict[tuple, pg.Font] = {}
        
        self._commands: list[DrawCommand] = []
        
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._cache_skips: int = 0
        
        self._total_commands_count: int = 0
        self._blit_count: int = 0
        
        self._blit_calls: list[tuple[pg.Surface, Vec2]] = []
    
    # region PROPERTIES
    
    @property
    def display(self) -> Display:
        return self._display
    
    @property
    def commands(self) -> list[DrawCommand]:
        return self._commands
    
    @property
    def total_commands_count(self) -> int:
        return self._total_commands_count
    
    @property
    def blit_count(self):
        return self._blit_count
    
    @property
    def cache_hits(self):
        return self._cache_hits
    
    @property
    def cache_misses(self):
        return self._cache_misses
    
    @property
    def cache_skips(self):
        return self._cache_skips
    
    @property
    def surface_cache_size(self):
        return self._surface_cache.size
    
    @property
    def surface_cache_memory_size(self):
        return self._surface_cache.memory_size
    
    @property
    def font_cache_size(self):
        return len(self._font_cache)
    
    # endregion
    
    def draw(self, cmd: DrawCommand) -> "Renderer":
        self._commands.append(cmd)
        return self
    
    def render(self, _camera: Optional[Camera] = None) -> "Renderer":
        self.display.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_skips = 0
        
        self._commands.sort(key=lambda c: (c.layer.layer_value, c.sub_layer))
        for cmd in self._commands:
            self._execute_command(cmd)
        
        self.display.surface.fblits(self._blit_calls)
        
        self._total_commands_count = len(self._commands)
        self._blit_count = len(self._blit_calls)
        
        self._commands.clear()
        self._blit_calls.clear()
        
        return self
    
    def _execute_command(self, cmd: DrawCommand) -> "Renderer":
        cache_hit = cmd.draw(self._blit_calls, self._surface_cache, self._font_cache)
        
        if cache_hit is None:
            self._cache_skips += 1
        else:
            self._cache_hits += cache_hit
            self._cache_misses += not cache_hit
        
        return self