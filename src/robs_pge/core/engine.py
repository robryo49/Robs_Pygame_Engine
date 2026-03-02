import pygame as pg

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
from ..utils import Vec2, Font, Colors, Anchor, Color


class Engine:
    def __init__(self, name: str):
        self._name: str = name
        
        self._display: Display = Display(Vec2(1920, 1080))
        
        self._clock: Clock = Clock(60)
        self._input: InputManager = InputManager()
        self._interaction_manager: InteractionManager = InteractionManager(self.input)
        
        self._resources: ResourceManager = ResourceManager()
        
        self._frame_timer: FrameTimer = FrameTimer()
        
        self._default_camera: Camera = Camera(self._display).move(self._display.dims*0.5).update(self.clock.dtime)
        
        self._state_manager: StateManager = StateManager()
        self._renderer: Renderer = Renderer(self.display, self._default_camera)
        
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
    
    def init_resources(self) -> "Engine":
        self.resources.set(Font, "debug_font_16", Font(size=16, font_color=Colors.WHITE))
        self.resources.set(RectStyle, "debug_rect_style", RectStyle(bg_color=Color(0, 0, 0, 160), bd_color=Color(0, 0, 0, 160), bd_radius=16))
        return self
    
    def init_debug_objects(self, factory: ObjectFactory, debug_overlay: DebugOverlay) -> "Engine":
        
        font = self.resources.get(Font, "debug_font_16")
        style = self.resources.get(RectStyle, "debug_rect_style")
        
        engine_debug_layout = factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_fps = factory.make_dynamic_text(Vec2(), "FPS: {:.1f} | {:.0f} ms", lambda: (self.clock.fps, self.clock.dtime*1000), font)
        debug_renderer = factory.make_dynamic_text(Vec2(), "Draw Calls : World({}), UI({}), Debug({})", lambda: self.renderer.commands_count, font)
        debug_cache = factory.make_dynamic_text(Vec2(), "Cache Size : Surface({}), Font({})", lambda: (self.renderer.surface_cache_size, self.renderer.font_cache_size), font)
        
        engine_debug_layout.stack_y(factory.make_text(Vec2(), "Engine :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        engine_debug_layout.stack_y(debug_fps, anchor=Anchor.TL)
        engine_debug_layout.stack_y(debug_renderer, anchor=Anchor.TL)
        engine_debug_layout.stack_y(debug_cache, anchor=Anchor.TL)
        
        debug_overlay.stack_y(engine_debug_layout, 0, 1, anchor=Anchor.TL)
        
        return self
    
    def process_events(self) -> "Engine":
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.quit()
            
            self.input.process_event(event)
        
        return self
        
    def update(self, dt: float) -> "Engine":
        self.process_events()
        self.state_manager.update(dt)
        self.input.update()
        return self
        
    
    def render(self) -> "Engine":
        self.state_manager.render()
        
        self.renderer.render(self.state.camera if self.state else None)
        self.display.update(self.clock.dtime)
        return self
        
    def tick(self) -> "Engine":
        self.clock.tick()
        self.frame_timer.reset()
        return self
    
    def run(self) -> None:
        while self.running:
            self.frame_timer.start("update")
            self.update(self.clock.dtime)
            self.frame_timer.end("update")
            
            self.frame_timer.start("render")
            self.render()
            self.frame_timer.end("render")
            
            self.tick()
            
        pg.quit()
        
    def quit(self) -> "Engine":
        self._running = False
        return self
