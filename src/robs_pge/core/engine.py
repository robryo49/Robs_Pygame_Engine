import sys

import pygame as pg
import logging

from .camera import Camera
from .clock import Clock
from .display import Display
from .renderer import Renderer
from ..debug import FrameTimer
from ..input import InputManager
from ..objects import InteractionManager, DebugOverlay, ObjectFactory
from ..resources import ResourceManager
from ..rendering import RectStyle
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
            single_colors={
                "white": Colors.LIGHT_GRAY,
                "gray": Colors.SLATE_BLUE,
                "blue": Colors.BRIGHT_BLUE,
                "yellow": Colors.AMBER,
                "red": Colors.LIGHT_RED,
                "teal": Colors.CARIBBEAN_GREEN,
                "bg_blue_1": Colors.DARK_NAVY,
                "bg_blue_2": Colors.MIDNIGHT
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
        })
        
    def init_textures(self):
        logging.info("Initializing textures")
    
    def init_styles(self):
        logging.info("Initializing styles")
        self.resources.set(RectStyle, "debug_rect_style",   RectStyle(bg_color=Color(0, 0, 0, 160), bd_color=Color(0, 0, 0, 160), bd_radius=16))
        
    
    def init_resources(self) -> "Engine":
        logging.info("Initializing resources")
        self.init_color_palettes()
        self.init_fonts()
        self.init_styles()
        self.init_textures()
        
        return self
    
    def init_debug_layout_objects(self, factory: ObjectFactory, debug_overlay: DebugOverlay) -> "Engine":
        
        font = self.resources.get_font("debug_yellow_text")
        style = self.resources.get(RectStyle, "debug_rect_style")
        
        engine_debug_layout = factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_fps = factory.make_dynamic_text(Vec2(), "FPS: {:.1f} | {:.0f} ms", lambda: (self.clock.fps, self.clock.dtime*1000), font, cache=False)
        debug_renderer = factory.make_dynamic_text(Vec2(), "Draw Calls : World({}), UI({}), Debug({})", lambda: self.renderer.commands_count, font, cache=False)
        debug_cache = factory.make_dynamic_text(
            Vec2(), "Cache Size : {:.1f}Mb (Surface({}), Font({}))",
            lambda: (self.renderer.surface_cache_memory_size, self.renderer.surface_cache_size, self.renderer.font_cache_size), font, cache=False
        )
        debug_cache_hits = factory.make_dynamic_text(
            Vec2(), "Cache Hits : {} | Misses : {} | Skips : {}", lambda: (self.renderer.cache_hits, self.renderer.cache_misses, self.renderer.cache_skips), font, cache=False
        )
        
        engine_debug_layout.stack_y(factory.make_text(Vec2(), "Engine :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        engine_debug_layout.stack_y(debug_fps, anchor=Anchor.TL)
        engine_debug_layout.stack_y(debug_renderer, anchor=Anchor.TL)
        engine_debug_layout.stack_y(debug_cache, anchor=Anchor.TL)
        engine_debug_layout.stack_y(debug_cache_hits, anchor=Anchor.TL)
        
        debug_overlay.stack_y(engine_debug_layout, 0, 1, anchor=Anchor.TL)
        
        
        timer_debug_layout = factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_timer = factory.make_dynamic_text(Vec2(), "{}", lambda: self.frame_timer.format(), font, cache=False)
        
        timer_debug_layout.stack_y(factory.make_text(Vec2(), "Timer :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        timer_debug_layout.stack_y(debug_timer, 0, 1, anchor=Anchor.TL)
        
        debug_overlay.stack_y(timer_debug_layout, 0, 1, anchor=Anchor.TL)
        
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
