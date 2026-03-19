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
from ..utils import DictCollection, Vec2, Anchor, Font



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
        
        self._services = DictCollection()
        self._factory.services = self._services
        
        self._objects = ObjectCollection()
        self._ui_objects = ObjectCollection()
        
        self._debug_overlay = self.factory.make_debug_overlay(Vec2(0, self.engine.display.dims.y), anchor=Anchor.TL)
        
        self.init_resources()
        self.init_keybinds()
        self.init_services()
        self.init_debug_layout_objects()
        
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
    def resources(self) -> ResourceManager:
        return self.engine.resources
    
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
    
    def init_resources(self):
        pass
    
    def init_services(self):
        self._services.set(AnimationManager, self.animation_manager)
        self._services.set(InputManager, self.input)
        self._services.set(ParticleSystem, self.particle_system)
        self._services.set(ObjectFactory, self.factory)
    
    def init_debug_layout_objects(self):
        
        self.debug_overlay.set_constant_padding(10).invert_up_down().fix_width(self.engine.display.dims.x)
        self.engine.init_debug_layout_objects(self.factory, self.debug_overlay)
        
        font = self.resources.get(Font, "dejavu_16_white")
        style = self.resources.get(RectStyle, "debug_rect_style")
        
        camera = self.camera
        camera_debug_layout = self.factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_camera_pos = self.factory.make_dynamic_text(Vec2(), "Pos: {} | Zoom: {:.2f} | Rot: {:.1f}", lambda: (round(camera.pos, 1), camera.zoom, camera.rotation), font, cache=False)
        debug_camera_aabb = self.factory.make_dynamic_text(Vec2(), "AABB: {}", lambda: [round(v, 1) for v in camera.world_aabb], font, cache=False)
        debug_camera_corners = self.factory.make_dynamic_text(Vec2(), "Limits: {:.1f} {:.1f} | {:.1f} {:.1f}", lambda: (*camera.bottom_left, *camera.top_right), font, cache=False)
        
        camera_debug_layout.stack_y(self.factory.make_text(Vec2(), "Camera :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        camera_debug_layout.stack_y(debug_camera_pos, anchor=Anchor.TL)
        camera_debug_layout.stack_y(debug_camera_aabb, anchor=Anchor.TL)
        camera_debug_layout.stack_y(debug_camera_corners, anchor=Anchor.TL)
        
        
        inp = self.input
        input_debug_layout = self.factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_mouse_pos = self.factory.make_dynamic_text(Vec2(), "Pos: Screen({}) | World({})", lambda: (round(inp.mouse_pos), round(inp.mouse.world_pos(self.camera))), font, cache=False)
        debug_pressed_keys = self.factory.make_dynamic_text(Vec2(), "Held Keys: {}", lambda: {pg.key.name(k): inp.held_keys[k] for k in inp.held_keys}, font, cache=False)
        debug_pressed_buttons = self.factory.make_dynamic_text(Vec2(), "Held Buttons: {}", lambda: inp.held_buttons, font, cache=False)
        
        input_debug_layout.stack_y(self.factory.make_text(Vec2(), "Mouse :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        input_debug_layout.stack_y(debug_mouse_pos, anchor=Anchor.TL)
        input_debug_layout.stack_y(debug_pressed_keys, anchor=Anchor.TL)
        input_debug_layout.stack_y(debug_pressed_buttons, anchor=Anchor.TL)
        
        
        animation_debug_layout = self.factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_running_animation_count = self.factory.make_dynamic_text(Vec2(), "Running: {}", lambda: len(self.animation_manager.active), font, cache=False)
        debug_scheduled_animation_count = self.factory.make_dynamic_text(Vec2(), "Scheduled: {}", lambda: len(self.animation_manager.scheduled), font, cache=False)
        
        animation_debug_layout.stack_y(self.factory.make_text(Vec2(), "Animations :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        animation_debug_layout.stack_y(debug_running_animation_count, anchor=Anchor.TL)
        animation_debug_layout.stack_y(debug_scheduled_animation_count, anchor=Anchor.TL)
        
        
        object_debug_layout = self.factory.make_column_layout(Vec2(), style=style, invert_y=True).set_outer_padding(10)
        debug_object_count = self.factory.make_dynamic_text(Vec2(), "Count: World({}) | UI({})", lambda: (len(self.objects.elements), len(self.ui_objects.elements)), font, cache=False)
        debug_hovered_object = self.factory.make_dynamic_text(Vec2(), "Hovered : {}", lambda: str(self.interaction_manager.hovered), font, cache=False)
        
        object_debug_layout.stack_y(self.factory.make_text(Vec2(), "Objects :", font), anchor=Anchor.TL).set_cell_padding(5, (0, 0))
        object_debug_layout.stack_y(debug_object_count, anchor=Anchor.TL)
        object_debug_layout.stack_y(debug_hovered_object, anchor=Anchor.TL)
        
        
        self.debug_overlay.stack_y(camera_debug_layout, 0, 1, anchor=Anchor.TL)
        self.debug_overlay.stack_y(input_debug_layout, 0, 1, anchor=Anchor.TL)
        self.debug_overlay.stack_y(animation_debug_layout, 0, 1, anchor=Anchor.TL)
        self.debug_overlay.stack_y(object_debug_layout, 0, 1, anchor=Anchor.TL)
    
    def init_keybinds(self):
        self.add_keybind(pg.K_F3, lambda: self.debug_overlay.toggle_visible())
        self.add_keybind(pg.K_F4, lambda: self.debug_overlay.toggle_freeze())
    
    def add_keybind(self, key: int | tuple[int, ...], action: Callable, *args):
        self.keybinds.add(Keybind(key, action, *args))

    def update(self, dt: float):
        self.animation_manager.update(dt)
        self.keybinds.update()
        
        self.frame_timer.time("Update.State.Interactions", lambda: self.interaction_manager.update(self.objects, self.ui_objects, self.camera))
        
        self.frame_timer.time("Update.State.UI Objects", lambda: self.ui_objects.update(dt))
        self.frame_timer.time("Update.State.World Objects", lambda: self.objects.update(dt))
        
        self.frame_timer.time("Update.State.Camera", lambda: self.camera.update(dt))
        
        self.frame_timer.time("Update.State.Debug Overlay", lambda: self.debug_overlay.update(dt))
    
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
    
    