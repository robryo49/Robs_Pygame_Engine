import logging
from typing import Callable

import pygame as pg

from ..animation import AnimationManager
from ..rendering import RectStyle
from ..core.camera import Camera
from ..debug import FrameTimer
from ..input import InputManager, Keybind, KeybindsManager
from ..objects import ObjectCollection, ObjectFactory, PygameObject, ObjectFlags
from ..particles.particle_system import ParticleSystem
from ..resources import ResourceManager
from ..utils import DictCollection, Vec2, Anchor, Font, Color, Colors



class State:
    def __init__(self, engine, state_id: str):
        
        self._id = state_id
        self._engine = engine
        
        self._engine.state_manager.add_state(self)
        
        self._camera = Camera(self.engine.display)
        
        self._animation_manager = AnimationManager()
        self._keybinds_manager = KeybindsManager(self.input)
        self._factory = ObjectFactory()
        self._particle_system = ParticleSystem()
        
        self._services: DictCollection = DictCollection()
        self._factory.services = self._services
        
        self._objects: ObjectCollection = ObjectCollection()
        self._ui_objects: ObjectCollection = ObjectCollection()
        
        self._debug_overlay = self.factory.make_debug_overlay(Vec2(0, self.engine.display.dims.y), anchor=Anchor.TL)
        
        self.init_resources()
        self.init_keybinds()
        self.init_services()
        self.init_debug_layout_objects()
    
    # region PROPERTIES
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def engine(self):
        return self._engine
    
    @property
    def clock(self):
        return self.engine.clock
    
    @property
    def dt(self) -> float:
        return self.clock.dtime
    
    @property
    def input(self) -> InputManager:
        return self.engine.input
    
    @property
    def camera(self) -> Camera:
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
    def resources(self) -> ResourceManager:
        return self.engine.resources
    
    @property
    def animation_manager(self) -> AnimationManager:
        return self._animation_manager
    
    @property
    def interaction_manager(self):
        return self.engine.interaction_manager
    
    @property
    def particle_system(self) -> ParticleSystem:
        return self._particle_system
    
    @property
    def factory(self) -> ObjectFactory:
        return self._factory
    
    @property
    def keybinds(self) -> KeybindsManager:
        return self._keybinds_manager
    
    @property
    def objects(self) -> ObjectCollection:
        return self._objects
    
    @property
    def ui_objects(self) -> ObjectCollection:
        return self._ui_objects
    
    # endregion
    
    def init_debug_layout_objects(self) -> None:
        
        self.debug_overlay.set_constant_padding(10).invert_up_down().fix_width(self.engine.display.dims.x)
        self.engine.init_debug_layout_objects(self.factory, self.debug_overlay)
        
        debug_rect_style = self.resources.get(RectStyle, "debug_rect_style")
        debug_red_header_style = self.resources.get(RectStyle, "debug_red_header_style")
        
        layout = self.factory.make_column_layout(Vec2(), 200, 200).skip_rendering()
        
        layout.stack_y(self.factory.make_rect(Vec2(), Vec2(300, 100), style=debug_rect_style))
        layout.stack_y(self.factory.make_rect(Vec2(), Vec2(300, 100), style=debug_red_header_style))
        
        self.debug_overlay.stack_y(layout, anchor=Anchor.TL)
    
    def init_resources(self) -> None:
        pass
    
    def init_services(self) -> None:
        self._services.set(AnimationManager, self.animation_manager)
        self._services.set(InputManager, self.input)
        self._services.set(ParticleSystem, self.particle_system)
        self._services.set(ObjectFactory, self.factory)
        
    
    def init_keybinds(self) -> None:
        self.add_keybind(pg.K_F3, lambda: self.debug_overlay.toggle_visible())
        self.add_keybind(pg.K_F4, lambda: self.debug_overlay.toggle_freeze())
    
    def add_keybind(self, key: int | tuple[int, ...], action: Callable, *args) -> None:
        self.keybinds.add(Keybind(key, action, *args))
    
    def update(self, dt: float) -> None:
        self.animation_manager.update(dt)
        self.keybinds.update()
        
        self.frame_timer.time("Update.State.Interactions", lambda: self.interaction_manager.update(self.objects, self.ui_objects, self.camera))
        self.frame_timer.time("Update.State.UI Objects", lambda: self.ui_objects.update(dt))
        self.frame_timer.time("Update.State.World Objects", lambda: self.objects.update(dt))
        self.frame_timer.time("Update.State.Camera", lambda: self.camera.update(dt))
        self.frame_timer.time("Update.State.Debug Overlay", lambda: self.debug_overlay.update(dt))
    
    def render(self) -> None:
        self.draw_world(self.objects)
        self.draw_ui(self.ui_objects)
        self.draw_debug(self.debug_overlay)
    
    def draw_world(self, obj: PygameObject | ObjectCollection) -> None:
        obj.render(self.renderer.draw_world, self.camera)
    
    def draw_ui(self, obj: PygameObject | ObjectCollection) -> None:
        obj.render(self.renderer.draw_ui, self.engine.default_camera)
    
    def draw_debug(self, obj: PygameObject | ObjectCollection) -> None:
        obj.render(self.renderer.draw_debug, self.engine.default_camera)