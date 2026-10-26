"""Renderer that executes queued draw commands and presents the scaled viewport."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pygame as pg

from ..rendering import DrawCommand
from ..resources import SurfaceCache
from ..utils import vec2

if TYPE_CHECKING:
    from ..core import Camera, Display


class Renderer:
    """Collects draw commands, renders them to the viewport, and scales to the display."""

    def __init__(self, display: Display, default_camera: Camera, max_cache_size: int = 2048 * 1024 * 1024) -> None:
        """Initialize the renderer, caches, and per-frame counters.

        :param display: Display that owns the target screen surface.
        :param default_camera: Camera retained as the renderer's default camera.
        :param max_cache_size: Maximum surface-cache size in bytes.
        """
        self._display: Display = display
        self._default_camera: Camera = default_camera
        
        self._draw_surface: pg.Surface = pg.Surface(self.display.viewport_dims)
        
        self._surface_cache: SurfaceCache = SurfaceCache(max_cache_size)
        self._font_cache: dict[tuple, pg.Font] = {}
        
        self._commands: list[DrawCommand] = []
        
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._cache_skips: int = 0
        
        self._total_commands_count: int = 0
        self._blit_count: int = 0
        
        self._blit_calls: list[tuple[pg.Surface, vec2]] = []
    
    # region PROPERTIES
    
    @property
    def display(self) -> Display:
        """Return the display rendered to by this renderer."""
        return self._display
    
    @property
    def commands(self) -> list[DrawCommand]:
        """Return the commands currently queued for the next render."""
        return self._commands
    
    @property
    def total_commands_count(self) -> int:
        """Return the number of commands executed during the last render."""
        return self._total_commands_count
    
    @property
    def blit_count(self) -> int:
        """Return the number of surface blits issued during the last render."""
        return self._blit_count

    @property
    def cache_hits(self) -> int:
        """Return the number of surface-cache hits during the last render."""
        return self._cache_hits

    @property
    def cache_misses(self) -> int:
        """Return the number of surface-cache misses during the last render."""
        return self._cache_misses

    @property
    def cache_skips(self) -> int:
        """Return the number of commands that skipped caching during the last render."""
        return self._cache_skips

    @property
    def surface_cache_size(self) -> int:
        """Return the number of surfaces currently stored in the surface cache."""
        return self._surface_cache.size

    @property
    def surface_cache_memory_size(self) -> float:
        """Return the approximate memory used by cached surfaces in bytes."""
        return self._surface_cache.memory_size

    @property
    def font_cache_size(self) -> int:
        """Return the number of fonts currently stored in the font cache."""
        return len(self._font_cache)
    
    # endregion
    
    def draw(self, cmd: DrawCommand) -> Renderer:
        """Queue a draw command for the next render.

        :param cmd: Draw command to queue.
        :return: This renderer for method chaining.
        """
        self._commands.append(cmd)
        return self

    def clear(self) -> Renderer:
        """Clear the viewport surface to the display clear color.

        :return: This renderer for method chaining.
        """
        self._draw_surface.fill(self.display.clear_color)
        return self

    def render(self, _camera: Optional[Camera] = None) -> Renderer:
        """Execute queued commands and present the scaled viewport.

        Commands already carry their layer cameras, so ``_camera`` is retained
        for API compatibility and is intentionally unused.

        :param _camera: Optional camera retained for API compatibility.
        :return: This renderer for method chaining.
        """
        self.clear()
        
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_skips = 0
        
        self._commands.sort(key=lambda c: (c.layer.layer_value, c.sub_layer))
        for cmd in self._commands:
            self._execute_command(cmd)
        
        self._draw_surface.fblits(self._blit_calls)
        pg.transform.scale(self._draw_surface, self.display.screen_dims, self.display.surface)
        
        self._total_commands_count = len(self._commands)
        self._blit_count = len(self._blit_calls)
        
        self._commands.clear()
        self._blit_calls.clear()
        
        return self
    
    def _execute_command(self, cmd: DrawCommand) -> Renderer:
        """Execute one command and update cache statistics.

        :param cmd: Draw command to execute.
        :return: This renderer.
        """
        cache_hit = cmd.draw(self._blit_calls, self._surface_cache, self._font_cache)
        
        if cache_hit is None:
            self._cache_skips += 1
        else:
            self._cache_hits += cache_hit
            self._cache_misses += not cache_hit
        
        return self