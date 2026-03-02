import pygame as pg

from .camera import Camera
from .clock import Clock
from .display import Display
from .renderer import Renderer
from ..debug import FrameTimer
from ..input import InputManager
from ..objects import InteractionManager, DebugOverlay, ObjectFactory
from ..resources import ResourceManager
from ..states import StateManager
from ..utils import Vec2, Font, Colors, Anchor


class Engine:
    def __init__(self, name: str):
        self._name: str = name
        
        self._display: Display = Display(Vec2(1920, 1080))
        
        self._clock: Clock = Clock(60)
        self._input: InputManager = InputManager()
        self._interaction_manager: InteractionManager = InteractionManager(self.input)
        
        self._resource_manager: ResourceManager = ResourceManager()
        
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
    def resource_manager(self) -> ResourceManager:
        return self._resource_manager
    
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
        self.resource_manager.set(Font, "debug_font_16", Font(size=16, font_color=Colors.WHITE))
        return self
    
    def init_debug_objects(self, factory: ObjectFactory, debug_overlay: DebugOverlay) -> "Engine":
        
        font = self.resource_manager.get(Font, "debug_font_16")
        
        engine_debug_layout = factory.make_column_layout(Vec2(), invert_y=True)
        debug_fps = factory.make_dynamic_text(Vec2(), "FPS: {:.1f} | {:.1f} ms", lambda: (self.clock.fps, self.clock.dtime*1000), font)
        debug_renderer = factory.make_dynamic_text(Vec2(), "Draw Calls : World({}), UI({}), Debug({})", lambda: self.renderer.commands_count, font)
        debug_cache = factory.make_dynamic_text(Vec2(), "Cache Size : Surface({}), Font({})", lambda: (self.renderer.surface_cache_size, self.renderer.font_cache_size), font)
        
        engine_debug_layout.add_object(debug_fps, 0, 0, anchor=Anchor.TL)
        engine_debug_layout.add_object(debug_renderer, 0, 1, anchor=Anchor.TL)
        engine_debug_layout.add_object(debug_cache, 0, 2, anchor=Anchor.TL)
        
        debug_overlay.add_object(engine_debug_layout, 0, 0, anchor=Anchor.TL)
        
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
