import pygame as pg

from .camera import Camera
from .clock import Clock
from .display import Display
from .renderer import Renderer
from ..debug import FrameTimer
from ..input import InputManager
from ..objects import InteractionManager, DebugOverlay
from ..resources import ResourceManager
from ..states import StateManager
from ..utils import Colors, Font, Vec2


class Engine:
    def __init__(self, name: str):
        self._name: str = name
        
        self._display = Display(Vec2(1920, 1080))
        self._default_camera = Camera(self._display).move(self._display.dims*0.5)
        
        self._clock: Clock = Clock(60)
        self._input = InputManager()
        self._interaction_manager = InteractionManager(self.input)
        
        self._resource_manager = ResourceManager()
        
        self._frame_timer = FrameTimer()
        
        self._state_manager = StateManager()
        self._renderer = Renderer(self.display, self._default_camera)
        
        self._running = True
        
        self.init_resources()
        
    # region PROPERTIES
    
    @property
    def name(self):
        return self._name
    
    @property
    def display(self):
        return self._display
    
    @property
    def clock(self):
        return self._clock
    
    @property
    def input(self):
        return self._input
    
    @property
    def interaction_manager(self):
        return self._interaction_manager
    
    @property
    def resource_manager(self):
        return self._resource_manager
    
    @property
    def frame_timer(self):
        return self._frame_timer
    
    @property
    def state_manager(self):
        return self._state_manager
    
    @property
    def renderer(self):
        return self._renderer
    
    @property
    def state(self):
        return self.state_manager.state
    
    @property
    def running(self):
        return self._running
    
    # endregion
    
    def init_resources(self):
        pass
    
    def init_debug_objects(self, debug_overlay: DebugOverlay):
        pass
    
    def process_events(self):
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                self.quit()
            
            self.input.process_event(event)
        
    def update(self, dt: float):
        self.process_events()
        self.state_manager.update(dt)
        self.input.update()
        
    
    def render(self):
        self.state_manager.render()
        
        self.renderer.render(self.state.camera if self.state else None)
        self.display.update()
        
    def tick(self):
        self.clock.tick()
        self.frame_timer.reset()
    
    def run(self):
        while self.running:
            self.frame_timer.start("update")
            self.update(self.clock.dtime)
            self.frame_timer.end("update")
            
            self.frame_timer.start("render")
            self.render()
            self.frame_timer.end("render")
            
            self.tick()
            
        pg.quit()
        
    def quit(self):
        self._running = False

