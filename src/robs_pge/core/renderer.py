from typing import Optional

import pygame as pg

from .camera import Camera
from .display import Display
from ..rendering import DrawCommand
from ..resources import SurfaceCache
from ..utils import Vec2


class Renderer:
    def __init__(self, display: Display):
        
        self._display: Display = display
        
        self._surface_cache: SurfaceCache = SurfaceCache()
        self._font_cache: dict[tuple, pg.Font] = {}
        
        self._world_commands: list[DrawCommand] = []
        self._ui_commands: list[DrawCommand] = []
        self._debug_commands: list[DrawCommand] = []
        
        self._world_commands_count: int = 0
        self._ui_commands_count: int = 0
        self._debug_commands_count: int = 0
        
        self.blit_calls: list[tuple[pg.Surface, Vec2]] = []
    
    # region PROPERTIES
    
    @property
    def display(self):
        return self._display
    
    @property
    def world_commands(self):
        return self._world_commands
    
    @property
    def ui_commands(self):
        return self._ui_commands
    
    @property
    def debug_commands(self):
        return self._debug_commands
    
    @property
    def world_commands_count(self):
        return self._world_commands_count
    
    @property
    def ui_commands_count(self):
        return self._ui_commands_count
    
    @property
    def debug_commands_count(self):
        return self._debug_commands_count
    
    # endregion
    
    def draw_world(self, cmd: DrawCommand):
        self.world_commands.append(cmd)
    
    def draw_ui(self, cmd: DrawCommand):
        self.ui_commands.append(cmd)
    
    def draw_debug(self, cmd: DrawCommand):
        self.debug_commands.append(cmd)
    
    def render(self, camera: Camera):
        self.display.clear()
        
        for cmd in sorted(self.world_commands, key=lambda c: c.layer):
            self._execute_world(cmd, camera)
        
        for cmd in sorted(self.ui_commands, key=lambda c: c.layer):
            self._execute_ui(cmd)
        
        for cmd in sorted(self.debug_commands, key=lambda c: c.layer):
            self._execute_ui(cmd)
            
        self.display.surface.blits(self.blit_calls)
        
        self._world_commands_count = len(self._world_commands)
        self._ui_commands_count = len(self._ui_commands)
        self._debug_commands_count = len(self._debug_commands)
        
        self.world_commands.clear()
        self.ui_commands.clear()
        self.debug_commands.clear()
        self.blit_calls.clear()
    
    def _execute_world(self, cmd: DrawCommand, camera: Optional[Camera]):
        cmd.draw(self.blit_calls, camera, self._surface_cache, self._font_cache)
    
    def _execute_ui(self, cmd):
        self._execute_world(cmd, None)
    
    
