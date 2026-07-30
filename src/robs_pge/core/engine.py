import logging
import sys

import pygame as pg


from ..debug import FrameTimer
from ..input import InputManager
from ..objects import InteractionManager
from ..rendering import WindowStyle, LineChartStyle, ProgressBarStyle, RectStyle, Renderer
from ..resources import ResourceManager
from ..utils import Colors, Vec2, Vec2Like, Color, Anchor
from .camera import Camera
from .clock import Clock
from .display import Display
from .states import StateManager, State


class Engine:
    def __init__(self, name: str, resolution: Vec2Like = Vec2(1920, 1080), fullscreen: bool = True):
        self._name: str = name
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(name)s - %(levelname)s : %(message)s')
        
        self._display: Display = self._create_display(resolution, fullscreen)
        
        self._clock: Clock = self._create_clock()
        self._input: InputManager = self._create_input_manager()
        self._interaction_manager: InteractionManager = self._create_interaction_manager(self.input)
        
        self._resources: ResourceManager = self._create_resource_manager()
        
        self._frame_timer: FrameTimer = self._create_frame_timer()
        
        self._default_camera: Camera = Camera(self._display, invert_y_axis=False).move(self._display.dims*0.5).update(self.clock.dtime)
        
        self._state_manager: StateManager = self._create_state_manager()
        self._renderer: Renderer = self._create_renderer(self.display, self._default_camera)
        
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
    def state_camera(self) -> Camera:
        return self.state.camera
    
    @property
    def default_camera(self) -> Camera:
        return self._default_camera
    
    @property
    def running(self) -> bool:
        return self._running
    
    # endregion
    
    # region SERVICES CREATION
    
    @staticmethod
    def _create_display(dims: Vec2Like, fullscreen: bool = True) -> Display:
        return Display(dims, fullscreen, True, Color(20, 26, 40))
    
    @staticmethod
    def _create_clock() -> Clock:
        return Clock()
    
    @staticmethod
    def _create_input_manager() -> InputManager:
        return InputManager()
    
    @staticmethod
    def _create_interaction_manager(input_manager: InputManager) -> InteractionManager:
        return InteractionManager(input_manager)
    
    @staticmethod
    def _create_resource_manager() -> ResourceManager:
        return ResourceManager()
    
    @staticmethod
    def _create_frame_timer() -> FrameTimer:
        return FrameTimer()
    
    @staticmethod
    def _create_state_manager() -> StateManager:
        return StateManager()
    
    @staticmethod
    def _create_renderer(display: Display, default_camera: Camera, max_cache_size: int = 2048*1024*1024) -> Renderer:
        return Renderer(display, default_camera, max_cache_size)
    
    
    # endregion
    
    def init_resources(self) -> "Engine":
        logging.info("Initializing resources")
        self.init_folders()
        self.init_color_palettes()
        self.init_fonts()
        self.init_styles()
        self.init_textures()
        
        return self
    
    def init_folders(self):
        pass
    
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
        
        panel_style = RectStyle(bg_color=Colors.with_alpha(debug.dark_gray, 200), bd_color=Colors.with_alpha(debug.medium_gray, 200), bd=1)
        title_panel_style = RectStyle(bg_color=Colors.with_alpha(debug.medium_gray, 200))
        
        self.resources.set(RectStyle, "debug_panel_style", panel_style)
        self.resources.set(RectStyle, "debug_title_panel_style", title_panel_style)
        
        colors = {
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
        }
        
        for name, color in colors.items():
            header_style = RectStyle(bg_color=color)
            font = self.resources.get_font(f"debug_{name}_title")
            self.resources.set(RectStyle, f"debug_{name}_header_style", header_style)
            self.resources.set(WindowStyle, f"debug_{name}_panel_style", WindowStyle(
                bg_style=panel_style,
                show_header=True,
                header_style=header_style,
                header_height=4,
                header_margin=0,
                show_title=True,
                title_panel_style=title_panel_style,
                title_panel_height=30,
                title_panel_margin=8,
                title_font=font,
                title_align=Anchor.L,
            ))
        
        for name, color in colors.items():
            self.resources.set(LineChartStyle, f"debug_{name}_line_chart_style", LineChartStyle(RectStyle(Colors.with_alpha(Colors.BLACK, 60), bd=0), line_color=color, line_width=1))
        
        for name, color in colors.items():
            self.resources.set(ProgressBarStyle, f"debug_{name}_progress_bar_style", ProgressBarStyle(RectStyle(Colors.with_alpha(debug.dark_gray, 150), bd=0, bd_radius=2), color=color))
        
        return self
    
    def set_state(self, state: str | State):
        self.state_manager.set_state(state)
    
    
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
        self.frame_timer.time("Rendering.Drawing",          lambda: self.renderer.render(self.state_camera))
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
