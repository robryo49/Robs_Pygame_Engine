from typing import Callable

import pygame as pg

from ..animation import AnimationManager
from ..core.camera import Camera
from ..debug import FrameTimer
from ..input import Keybind, KeybindsManager
from ..objects import ObjectCollection, ObjectFactory, PygameObject
from ..particles.particle_system import ParticleSystem
from ..resources import ResourceManager
from ..utils import DictCollection, Vec2, Anchor, ObjectFlags


class State:
    def __init__(self, engine, state_id: str):
        
        self._id = state_id
        self._engine = engine
        
        self._camera = Camera(self.engine.display)
        
        self._animation_manager = AnimationManager()
        self._keybinds_manager = KeybindsManager(self.input)
        self._factory = ObjectFactory()
        self._particle_system = ParticleSystem()
        
        self._services = DictCollection({AnimationManager: self.animation_manager, ParticleSystem: self.particle_system, ObjectFactory: self.factory})
        self._factory.set_services(self._services)
        
        self._objects = ObjectCollection()
        self._ui_objects = ObjectCollection()
        
        self._debug_overlay = self.factory.make_debug_overlay(Vec2(0, self.engine.display.dims.y), invert_y=True, anchor=Anchor.TL)
        self._ui_objects.add(self._debug_overlay)
        
        self.engine.state_manager.add_state(self)
        
        self.init_keybinds()
        self.init_debug_objects()
        
    # region PROPERTIES
    
    @property
    def id(self):
        return self._id
    
    @property
    def engine(self):
        return self._engine
    
    @property
    def clock(self):
        return self.engine.clock
    
    @property
    def dt(self):
        return self.clock.dtime
    
    @property
    def input(self):
        return self.engine.input
    
    @property
    def camera(self):
        return self._camera
    
    @property
    def mouse(self):
        return self.input.mouse
    
    @property
    def renderer(self):
        return self.engine.renderer
    
    @property
    def debug_overlay(self):
        return self._debug_overlay
    
    @property
    def frame_timer(self) -> FrameTimer:
        return self.engine.frame_timer
    
    @property
    def resource_manager(self) -> ResourceManager:
        return self.engine.resource_manager
    
    @property
    def animation_manager(self):
        return self._animation_manager
    
    @property
    def interaction_manager(self):
        return self.engine.interaction_manager
    
    @property
    def particle_system(self):
        return self._particle_system
    
    @property
    def factory(self):
        return self._factory
    
    @property
    def keybinds(self):
        return self._keybinds_manager
    
    @property
    def objects(self):
        return self._objects
    
    @property
    def ui_objects(self):
        return self._ui_objects
    
    # endregion
    
    def init_debug_objects(self):
        self.debug_overlay.add_object(self.factory.make_text(Vec2(), "-  111  -"), 0, 0)
        self.debug_overlay.add_object(self.factory.make_text(Vec2(), "-    22222    -"), 0, 1)
        self.debug_overlay.add_object(self.factory.make_text(Vec2(), "- 33 3 33 -"), 0, 2)
    
    def init_keybinds(self):
        self.add_keybind(pg.K_F3, lambda: self.debug_overlay.toggle())
        self.add_keybind(pg.K_F4, lambda: self.debug_overlay.toggle_freeze())
    
    def add_keybind(self, key: int | tuple[int, ...], action: Callable, *args):
        self.keybinds.add(Keybind(key, action, *args))

    def update(self, dt: float):
        self.animation_manager.update(dt)
        self.keybinds.update()
        
        self.interaction_manager.update(self.objects, self.ui_objects, self.camera)
        
        self.ui_objects.update(dt)
        self.objects.update(dt)
        
        self.particle_system.update(dt)
        
        self.camera.update(dt)
    
    def render(self):
        self.draw_world(self.objects)
        self.draw_ui(self.ui_objects)
        
        self.particle_system.render(self.renderer.draw_world, self.camera)
    
    def draw_world(self, obj: PygameObject | ObjectCollection):
        obj.render(self.renderer.draw_world, self.camera)
    
    def draw_ui(self, obj: PygameObject | ObjectCollection):
        obj.render(self.renderer.draw_ui)
    
    