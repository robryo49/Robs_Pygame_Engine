from __future__ import annotations

from typing import TYPE_CHECKING

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
        
        self._world_commands: list[DrawCommand] = []
        self._ui_commands: list[DrawCommand] = []
        self._debug_commands: list[DrawCommand] = []
        
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._cache_skips: int = 0
        
        self._world_commands_count: int = 0
        self._ui_commands_count: int = 0
        self._debug_commands_count: int = 0
        self._commands_count = (0, 0, 0)
        self._blit_count: int = 0
        
        self._blit_calls: list[tuple[pg.Surface, Vec2]] = []
    
    # region PROPERTIES
    
    @property
    def display(self) -> Display:
        return self._display
    
    @property
    def world_commands(self) -> list[DrawCommand]:
        return self._world_commands
    
    @property
    def ui_commands(self) -> list[DrawCommand]:
        return self._ui_commands
    
    @property
    def debug_commands(self) -> list[DrawCommand]:
        return self._debug_commands
    
    @property
    def world_commands_count(self) -> int:
        return self._world_commands_count
    
    @property
    def ui_commands_count(self) -> int:
        return self._ui_commands_count
    
    @property
    def debug_commands_count(self) -> int:
        return self._debug_commands_count
    
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
    def commands_count(self) -> tuple[int, int, int]:
        return self._commands_count
    
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
    
    def draw_world(self, cmd: DrawCommand) -> "Renderer":
        self.world_commands.append(cmd)
        return self
    
    def draw_ui(self, cmd: DrawCommand) -> "Renderer":
        self.ui_commands.append(cmd)
        return self
    
    def draw_debug(self, cmd: DrawCommand) -> "Renderer":
        self.debug_commands.append(cmd)
        return self
    
    def render(self, camera: Camera) -> "Renderer":
        self.display.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_skips = 0
        
        for cmd in sorted(self.world_commands, key=lambda c: c.layer):
            self._execute_command(cmd, camera)
        
        for cmd in sorted(self.ui_commands, key=lambda c: c.layer):
            self._execute_command(cmd, self._default_camera)
        
        for cmd in sorted(self.debug_commands, key=lambda c: c.layer):
            self._execute_command(cmd, self._default_camera)
        
        self.display.surface.blits(self._blit_calls)
        
        self._world_commands_count = len(self._world_commands)
        self._ui_commands_count = len(self._ui_commands)
        self._debug_commands_count = len(self._debug_commands)
        self._commands_count = (self._world_commands_count, self._ui_commands_count, self._debug_commands_count)
        self._blit_count = len(self._blit_calls)
        
        self.world_commands.clear()
        self.ui_commands.clear()
        self.debug_commands.clear()
        self._blit_calls.clear()
        
        return self
    
    def _execute_command(self, cmd: DrawCommand, camera: Camera) -> "Renderer":
        cache_hit = cmd.draw(self._blit_calls, camera, self._surface_cache, self._font_cache)
        
        if cache_hit is None:
            self._cache_skips += 1
        else:
            self._cache_hits += cache_hit
            self._cache_misses += not cache_hit
        
        return self
    
    
