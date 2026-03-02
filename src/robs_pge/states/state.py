from typing import Callable

import pygame as pg

from ..animation import AnimationManager
from ..core.camera import Camera
from ..debug import FrameTimer
from ..input import InputManager, Keybind, KeybindsManager
from ..objects import ObjectCollection, ObjectFactory, PygameObject
from ..particles.particle_system import ParticleSystem
from ..resources import ResourceManager
from ..utils import DictCollection, Vec2, Anchor, ObjectFlags, Font


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
        
        self._services = DictCollection({AnimationManager: self.animation_manager, ParticleSystem: self.particle_system, ObjectFactory: self.factory})
        self._factory.set_services(self._services)
        
        self._objects = ObjectCollection()
        self._ui_objects = ObjectCollection()
        
        self._debug_overlay = self.factory.make_debug_overlay(Vec2(0, self.engine.display.dims.y), anchor=Anchor.TL).set_constant_padding(10).invert_up_down().fix_col_width(0, 500)
        
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
    def input(self) -> InputManager:
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
        self.engine.init_debug_objects(self.factory, self.debug_overlay)
        
        font = self.resource_manager.get(Font, "debug_font_16")
        
        
        camera = self.camera
        camera_debug_layout = self.factory.make_column_layout(Vec2(), invert_y=True)
        debug_camera_pos = self.factory.make_dynamic_text(Vec2(), "Camera Pos: {} | Zoom: {:.2f} | Rot: {:.1f}", lambda: (round(camera.pos, 1), camera.zoom, camera.rotation), font)
        debug_camera_aabb = self.factory.make_dynamic_text(Vec2(), "Camera AABB: {}", lambda: [round(v, 1) for v in camera.world_aabb], font)
        debug_camera_corners = self.factory.make_dynamic_text(Vec2(), "Camera Limits: {:.1f} {:.1f} | {:.1f} {:.1f}", lambda: (*camera.bottom_left, *camera.top_right), font)
        
        camera_debug_layout.add_object(debug_camera_pos, 0, 0, anchor=Anchor.TL)
        camera_debug_layout.add_object(debug_camera_aabb, 0, 1, anchor=Anchor.TL)
        camera_debug_layout.add_object(debug_camera_corners, 0, 2, anchor=Anchor.TL)
        
        
        inp = self.input
        input_debug_layout = self.factory.make_column_layout(Vec2(), invert_y=True)
        debug_mouse_pos = self.factory.make_dynamic_text(Vec2(), "Mouse Pos: Screen({}) World({})", lambda: (round(inp.mouse_pos), round(inp.mouse.world_pos(self.camera))), font)
        debug_pressed_keys = self.factory.make_dynamic_text(Vec2(), "Held Keys: {}", lambda: inp.held_keys, font)
        debug_pressed_buttons = self.factory.make_dynamic_text(Vec2(), "Held Buttons: {}", lambda: inp.held_buttons, font)
        
        input_debug_layout.add_object(debug_mouse_pos, 0, 0, anchor=Anchor.TL)
        input_debug_layout.add_object(debug_pressed_keys, 0, 1, anchor=Anchor.TL)
        input_debug_layout.add_object(debug_pressed_buttons, 0, 2, anchor=Anchor.TL)
        
        
        
        self.debug_overlay.add_object(camera_debug_layout, 0, 1, anchor=Anchor.TL)
        self.debug_overlay.add_object(input_debug_layout, 0, 2, anchor=Anchor.TL)
    
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
        
        self.camera.update(dt)
        
        self.debug_overlay.update(dt)
    
    def render(self):
        self.draw_world(self.objects)
        self.draw_ui(self.ui_objects)
        
        self.draw_debug(self.debug_overlay)
    
    def draw_world(self, obj: PygameObject | ObjectCollection):
        obj.render(self.renderer.draw_world, self.camera)
    
    def draw_ui(self, obj: PygameObject | ObjectCollection):
        obj.render(self.renderer.draw_ui, self.engine.default_camera)
        
    def draw_debug(self, obj: PygameObject | ObjectCollection):
        obj.render(self.renderer.draw_debug, self.engine.default_camera)
    
    