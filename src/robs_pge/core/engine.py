import sys

import pygame as pg
import logging

from .camera import Camera
from .clock import Clock
from .display import Display
from .renderer import Renderer
from ..debug import FrameTimer
from ..input import InputManager
from ..objects import InteractionManager, DebugOverlay, ObjectFactory, ObjectFlags
from ..resources import ResourceManager
from ..rendering import GraphStyle, ProgressBarStyle, RectStyle
from ..states import StateManager
from ..utils import Vec2, Colors, Anchor, Color


class Engine:
    def __init__(self, name: str):
        self._name: str = name
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(name)s - %(levelname)s : %(message)s')
        
        self._display: Display = Display(Vec2(1920, 1080))
        
        self._clock: Clock = Clock()
        self._input: InputManager = InputManager()
        self._interaction_manager: InteractionManager = InteractionManager(self.input)
        
        self._resources: ResourceManager = ResourceManager()
        
        self._frame_timer: FrameTimer = FrameTimer()
        
        self._default_camera: Camera = Camera(self._display).move(self._display.dims*0.5).update(self.clock.dtime)
        
        self._state_manager: StateManager = StateManager()
        self._renderer: Renderer = Renderer(self.display, self._default_camera, 2048 * 1024*1024)
        
        self._running: bool = True
        
        self.init_resources()
        
    # region PROPERTIES
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def display(self) -> Display:
        return self._display
    
    @property
    def clock(self) -> Clock:
        return self._clock
    
    @property
    def input(self) -> InputManager:
        return self._input
    
    @property
    def interaction_manager(self) -> InteractionManager:
        return self._interaction_manager
    
    @property
    def resources(self) -> ResourceManager:
        return self._resources
    
    @property
    def frame_timer(self) -> FrameTimer:
        return self._frame_timer
    
    @property
    def state_manager(self) -> StateManager:
        return self._state_manager
    
    @property
    def renderer(self) -> Renderer:
        return self._renderer
    
    @property
    def state(self):
        return self.state_manager.state
    
    @property
    def default_camera(self) -> Camera:
        return self._default_camera
    
    @property
    def running(self) -> bool:
        return self._running
    
    # endregion
    
    def init_color_palettes(self):
        logging.info("Initializing color palettes")
        self.resources.create_color_palette(
            "default",
            single_colors=Colors.ALL
        )
        
        self.resources.create_color_palette(
            "debug",
            colors= {
                "gray":     Colors.SLATE_BLUE,
                "blue":     Colors.BRIGHT_BLUE,
                "yellow":   Colors.AMBER,
                "red":      Colors.DARK_RED,
                "teal":     Colors.CARIBBEAN_GREEN,
                "orange":   Colors.ORANGE,
                "green":    Colors.GREEN,
                "purple":   Colors.PURPLE,
                "pink":     Colors.PINK,
                "cyan":     Colors.CYAN,
            },
            shades = {
                "light_{}": 1.2,
                "medium_{}": 0.6,
                "dark_{}": 0.2
            },
            single_colors={
                "white":    Colors.LIGHT_GRAY,
            }
        )
    
    def init_fonts(self):
        logging.info("Initializing fonts")
        
        sizes = [10, 14, 18]
        self.resources.create_fonts("dejavu", "dejavusansmono", sizes, ["white", "black"])
        
        debug = self.resources.get_color_palette("debug")
        self.resources.create_fonts("debug", "dejavusansmono", [("small", 10), ("text", 14), ("title", 20)], {
            "white":  debug.white,
            "gray":   debug.gray,
            "blue":   debug.blue,
            "yellow": debug.yellow,
            "red":    debug.red,
            "teal":   debug.teal,
            "orange": debug.orange,
            "green":  debug.green,
            "purple": debug.purple,
            "pink":   debug.pink,
            "cyan":   debug.cyan
        })
        
    def init_textures(self):
        logging.info("Initializing textures")
    
    def init_styles(self):
        logging.info("Initializing styles")
        
        self.init_debug_styles()
    
    def init_debug_styles(self) -> "Engine":
        logging.info("Initializing debug styles")
    
        debug = self.resources.get_color_palette("debug")
        
        self.resources.set(RectStyle, "debug_panel_style", RectStyle(bg_color=Colors.with_alpha(debug.dark_gray, 200), bd_color=Colors.with_alpha(debug.medium_gray, 200), bd=1))
        self.resources.set(RectStyle, "debug_title_panel_style", RectStyle(bg_color=Colors.with_alpha(debug.medium_gray, 200)))
        self.resources.set(RectStyle, "debug_bar_track_style", RectStyle(bg_color=Colors.with_alpha(debug.dark_gray, 150), bd=0))
        
        for name, color in {
            "green":  debug.green,
            "teal":   debug.teal,
            "blue":   debug.blue,
            "orange": debug.orange,
            "red":    debug.red,
            "yellow": debug.yellow,
            "purple": debug.purple,
            "pink":   debug.pink,
            "cyan":   debug.cyan,
            "gray":   debug.gray,
        }.items():
            self.resources.set(RectStyle, f"debug_{name}_header_style", RectStyle(bg_color=color, bd=0))
        
        for name, color in {
            "teal":         debug.teal,
            "green":        debug.green,
            "blue":         debug.blue,
            "orange":       debug.orange,
            "dark_orange":  debug.dark_orange,
            "yellow":       debug.yellow,
            "red":          debug.red,
            "gray":         debug.gray,
        }.items():
            self.resources.set(ProgressBarStyle, f"debug_{name}_progress_style", ProgressBarStyle(bg_color=Colors.with_alpha(debug.dark_gray, 150), color=color, bd=0, bd_radius=2))
        
        for name, color in {
            "green": debug.green,
            "blue":  debug.blue,
            "teal":  debug.teal,
            "red":   debug.red,
        }.items():
            self.resources.set(GraphStyle, f"debug_{name}_graph_style", GraphStyle(bg_color=Colors.with_alpha(debug.dark_gray, 100), bd=0, line_color=color, line_width=1))
        
        return self
        
    
    def init_resources(self) -> "Engine":
        logging.info("Initializing resources")
        self.init_color_palettes()
        self.init_fonts()
        self.init_styles()
        self.init_textures()
        
        return self
    
    def init_debug_overlay_objects(self, factory: ObjectFactory, debug_overlay: DebugOverlay) -> "Engine":
        
        return self
    
    def process_events(self) -> "Engine":
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.quit()
            
            self.input.process_event(event)
        
        return self
        
    def update(self, dt: float) -> "Engine":
        self.frame_timer.time("Update.Events",  self.process_events)
        self.frame_timer.time("Update.State",   lambda: self.state_manager.update(dt))
        self.frame_timer.time("Update.Input",   self.input.update)
        return self
        
    
    def render(self) -> "Engine":
        self.frame_timer.time("Rendering.Draw Calls",       self.state_manager.render)
        
        self.frame_timer.time("Rendering.Drawing",          lambda: self.renderer.render(self.state.camera if self.state else None))
        self.frame_timer.time("Rendering.Screen Update",    lambda: self.display.update(self.clock.dtime))
        return self
        
    def tick(self) -> "Engine":
        self.clock.tick()
        return self
    
    def run(self) -> None:
        while self.running:
            self.frame_timer.time("Update", lambda: self.update(self.clock.dtime))
            self.frame_timer.time("Rendering", self.render)
            self.frame_timer.time("Ticking", self.tick)
            
        pg.quit()
        
    def quit(self) -> "Engine":
        self._running = False
        return self
