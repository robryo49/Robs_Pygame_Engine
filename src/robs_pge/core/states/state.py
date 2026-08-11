from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

import pygame as pg

from ..camera import Camera
from ...animation import AnimationManager
from ...debug import FrameTimer, QuickDebugManager
from ...events import Event, EventManager
from ...input import InputManager, Keybind, KeybindsManager
from ...objects import InteractionManager, Layer, LayerManager, ObjectFactory, ParticleSystem, WindowManager, WindowObject, DebugOverlay
from ...rendering import LineChartStyle, WindowStyle
from ...resources import ResourceManager
from ...utils import Anchor, AsyncProcess, AsyncProcessManager, DictCollection, vec2, Callback, ScreenAnchor, round_sig

if TYPE_CHECKING:
    from ..engine import Engine
    from ...objects import PygameObject
    
    

_LAYER_WORLD = 0.0
_LAYER_UI    = 100.0
_LAYER_DEBUG = 1000.0



class State:
    def __init__(self, engine: Engine, state_id: str):
        
        self._id = state_id
        self._engine = engine
        
        self._engine.state_manager.register_state(self)
        
        self._camera = Camera(self.engine.display)
        
        self._event_manager = self._create_event_manager()
        self._animation_manager = self._create_animation_manager()
        self._keybinds_manager = self._create_keybinds_manager(self.input)
        self._particle_system = self._create_particle_system()
        self._async_process_manager = self._create_async_process_manager()
        self._window_manager = self._create_window_manager(self.event_manager)
        self._quick_debug_manager = self._create_quick_debug_manager()
        
        self._factory = self._create_object_factory()
        
        self._services: DictCollection = DictCollection()
        self._factory.services = self._services
        
        self._layer_manager: LayerManager = LayerManager(self._services)
        
        self._debug_layer = self.create_layer("debug", _LAYER_DEBUG, self.engine.default_camera, interactable=False)
        self._ui_layer = self.create_layer("ui", _LAYER_UI, self.engine.default_camera, interactable=True)
        self._world_layer = self.create_layer("world", _LAYER_WORLD, self.camera, interactable=True)
        
        self._debug_overlay = (
            self.create_object.ui.debug
            .debug_overlay(ScreenAnchor.TL, width=self.engine.display.viewport_dims.x, anchor=Anchor.TL)
            .set_constant_padding(20)
        )
        self.debug_layer.add_object(self._debug_overlay)
        self.debug_layer.disable_rendering()
        
        self.init_resources()
        self.init_keybinds()
        self.init_services()
        self.init_debug_overlay_objects()
    
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
    def default_camera(self) -> Camera:
        return self.engine.default_camera
    
    @property
    def mouse(self):
        return self.input.mouse
    
    @property
    def renderer(self):
        return self.engine.renderer
    
    @property
    def debug_overlay(self) -> DebugOverlay:
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
    def interaction_manager(self) -> InteractionManager:
        return self.engine.interaction_manager
    
    @property
    def event_manager(self) -> EventManager:
        return self._event_manager
    
    @property
    def particle_system(self) -> ParticleSystem:
        return self._particle_system
    
    @property
    def async_process_manager(self) -> AsyncProcessManager:
        return self._async_process_manager
    
    @property
    def quick_debug_manager(self):
        return self._quick_debug_manager
    
    @property
    def factory(self) -> ObjectFactory:
        return self._factory
    
    @property
    def create_object(self) -> ObjectFactory:
        return self._factory
    
    @property
    def keybinds(self) -> KeybindsManager:
        return self._keybinds_manager
    
    @property
    def layer_manager(self) -> LayerManager:
        return self._layer_manager
    
    @property
    def windows(self):
        return self._window_manager
    
    
    @property
    def debug_layer(self) -> Layer:
        return self._debug_layer
    
    @property
    def ui_layer(self) -> Layer:
        return self._ui_layer
    
    @property
    def world_layer(self) -> Layer:
        return self._world_layer
    
    # endregion
    
    # region SERVICES CREATION METHODS
    
    @staticmethod
    def _create_event_manager() -> EventManager:
        return EventManager()
    
    @staticmethod
    def _create_animation_manager() -> AnimationManager:
        return AnimationManager()
    
    @staticmethod
    def _create_keybinds_manager(input_manager: InputManager) -> KeybindsManager:
        return KeybindsManager(input_manager)
    
    @staticmethod
    def _create_object_factory() -> ObjectFactory:
        return ObjectFactory()
    
    @staticmethod
    def _create_particle_system() -> ParticleSystem:
        return ParticleSystem()
    
    @staticmethod
    def _create_async_process_manager() -> AsyncProcessManager:
        return AsyncProcessManager()
    
    @staticmethod
    def _create_window_manager(event_manager) -> WindowManager:
        return WindowManager(event_manager)
    
    @staticmethod
    def _create_quick_debug_manager():
        return QuickDebugManager()
    
    # endregion
    
    # region INIT METHODS
    
    def init_debug_overlay_objects(self) -> None:
        
        green_style  = self.resources.get(WindowStyle, "debug_teal_panel_style")
        blue_style   = self.resources.get(WindowStyle, "debug_blue_panel_style")
        yellow_style = self.resources.get(WindowStyle, "debug_yellow_panel_style")
        red_style = self.resources.get(WindowStyle, "debug_red_panel_style")
        
        font_gray       = self.resources.get_font("debug_gray_text")
        font_white      = self.resources.get_font("debug_white_text")
        
        panels_width = 400
        titles_width = 150
        infos_width = panels_width - titles_width - 20
        
        engine_pannel = self.create_object.ui.debug.debug_info_window(vec2(), "ENGINE", panels_width, titles_width, infos_width, font_white, font_gray, blue_style)
        engine_pannel.add_line("FPS", "{} ms", lambda: round(self.clock.fps))
        engine_pannel.add_line("SPF", "{} ms", lambda: round(self.clock.dtime * 1000, 1))
        engine_pannel.add_line("Frames Elapsed", "{} frames", lambda: self.clock.tick_num)
        engine_pannel.add_line("Time Elapsed", "{} s", lambda: round(self.clock.time, 1))
        
        state_panel = self.create_object.ui.debug.debug_info_window(vec2(), "ENGINE", panels_width, titles_width, infos_width, font_white, font_gray, green_style)
        state_panel.add_line("Current", "{}", lambda: self.id)
        state_panel.add_line("Layers :", "{}", lambda: "")
        for layer in list(self.layer_manager.layers.values()):
            state_panel.add_line("- " + layer.id, "{} Objects", layer.get_objects_number)
        
        rendering_panel = self.create_object.ui.debug.debug_info_window(vec2(), "RENDERING", panels_width, titles_width, infos_width, font_white, font_gray, yellow_style)
        rendering_panel.add_line("Cache Size",  "{} ({}Mo)", lambda: (self.renderer.surface_cache_size, round(self.renderer.surface_cache_memory_size, 1)))
        rendering_panel.add_line("Cache Hits",  "{}", lambda: self.renderer.cache_hits)
        rendering_panel.add_line("Cache Skips", "{}", lambda: self.renderer.cache_skips)
        rendering_panel.add_line("Cache Misses", "{}", lambda: self.renderer.cache_misses)
        rendering_panel.add_line("Blits count", "{}", lambda: self.renderer.blit_count)
        
        frame_panel = self.create_object.ui.debug.debug_info_window(vec2(), "FRAME", panels_width, titles_width, infos_width, font_white, font_gray, red_style)
        frame_panel.add_line("Update",          "{} ms", lambda: self.frame_timer.get_time_ms("Update"))
        frame_panel.add_line("- Events",        "{} ms", lambda: self.frame_timer.get_time_ms("Update.Events"))
        frame_panel.add_line("- State",         "{} ms", lambda: self.frame_timer.get_time_ms("Update.State"))
        frame_panel.add_line("- Input",         "{} ms", lambda: self.frame_timer.get_time_ms("Update.Input"))
        frame_panel.add_line_break()
        frame_panel.add_line("Rendering",       "{} ms", lambda: self.frame_timer.get_time_ms("Rendering"))
        frame_panel.add_line("- Draw Calls",    "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Draw Calls"))
        frame_panel.add_line("- Drawing",       "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Drawing"))
        frame_panel.add_line("- Screen Update", "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Screen Update"))
        frame_panel.add_line_break()
        frame_panel.add_line("Ticking",         "{} ms", lambda: self.frame_timer.get_time_ms("Ticking"))
        
        camera_panel = self.create_object.ui.debug.debug_info_window(vec2(), "CAMERA", panels_width, titles_width, infos_width, font_white, font_gray, blue_style)
        camera_panel.add_line("Position",       "{}", lambda: self.camera.pos.to_tuple())
        camera_panel.add_line("Zoom",           "{}x (min: {} max: {})", lambda: (round_sig(self.camera.zoom, 2), self.camera.min_zoom, self.camera.max_zoom))
        camera_panel.add_line("Rotation",       "{}°", lambda: round(self.camera.rotation, 1))
        
        mouse_panel = self.create_object.ui.debug.debug_info_window(vec2(), "MOUSE", panels_width, titles_width, infos_width, font_white, font_gray, green_style)
        mouse_panel.add_line("Screen Position", "{}", lambda: self.mouse.pos.to_tuple())
        mouse_panel.add_line("Camera Position", "{}", lambda: self.camera.screen_to_camera_pos(self.mouse.pos).to_tuple())
        mouse_panel.add_line("World Position",  "{}", lambda: self.camera.screen_to_world_pos(self.mouse.pos).to_tuple())
        mouse_panel.add_line("Pressed Buttons", "{}", lambda: self.mouse.held_buttons)
        mouse_panel.add_line("Hovered",         "{}", lambda: self.interaction_manager.hovered)

        input_panel = self.create_object.ui.debug.debug_info_window(vec2(), "INPUT", panels_width, titles_width, infos_width, font_white, font_gray, yellow_style)
        input_panel.add_line("Pressed Keys",    "{}", lambda: '{' + ", ".join(": ".join([pg.key.name(k), str(t)]) for k, t in self.input.held_keys.items()) + '}')
        
        animation_panel = self.create_object.ui.debug.debug_info_window(vec2(), "ANIMATION", panels_width, titles_width, infos_width, font_white, font_gray, blue_style)
        animation_panel.add_line("Running",     "{}", lambda: len(self.animation_manager.active))
        animation_panel.add_line("Scheduled",   "{}", lambda: len(self.animation_manager.scheduled))
        
        async_panel = self.create_object.ui.debug.debug_info_window(vec2(), "ASYNC", panels_width, titles_width, infos_width, font_white, font_gray, red_style)
        async_panel.add_line("Running",         "{}", lambda: self.async_process_manager.pending_count)
        
        quick_debug_panel = self.create_object.ui.debug.dynamic_debug_info_window(vec2(), "QUICK DEBUG", panels_width, self.quick_debug_manager.get_values, titles_width, infos_width, font_white, font_gray, yellow_style)
        
        self.debug_overlay.stack_y(engine_pannel, 0, Anchor.TL)
        self.debug_overlay.stack_y(state_panel, 0, Anchor.TL)
        self.debug_overlay.stack_y(rendering_panel, 0, Anchor.TL)
        self.debug_overlay.stack_y(frame_panel, 0, Anchor.TL)
        self.debug_overlay.stack_y(camera_panel, 0, Anchor.TL)
        self.debug_overlay.stack_y(mouse_panel, 0, Anchor.TL)
        
        self.debug_overlay.stack_y(input_panel, 1, Anchor.TL)
        self.debug_overlay.stack_y(animation_panel, 1, Anchor.TL)
        self.debug_overlay.stack_y(async_panel, 1, Anchor.TL)
        
        self.debug_overlay.stack_y(quick_debug_panel, 2, Anchor.TR)
    
    def init_resources(self) -> None:
        pass
    
    def init_services(self) -> None:
        self._services.set(State, self)
        self._services.set(AnimationManager, self.animation_manager)
        self._services.set(InputManager, self.input)
        self._services.set(ParticleSystem, self.particle_system)
        self._services.set(ObjectFactory, self.factory)
        self._services.set(EventManager, self.event_manager)
        self._services.set(AsyncProcessManager, self.async_process_manager)
        self._services.set(ResourceManager, self.resources)
        self._services.set(QuickDebugManager, self.quick_debug_manager)
    
    def init_keybinds(self) -> None:
        self.register_keybind(pg.K_F3, lambda: self.debug_layer.toggle_rendering())
        self.register_keybind(pg.K_F4, lambda: self.debug_layer.toggle_frozen())
    
    def init_events(self):
        pass
    
    # endregion
    
    # region REGISTRATION METHODS
    
    def register_keybind(self, key: int | tuple[int, ...], action: Callback[[], Any], *args) -> None:
        self.keybinds.register(Keybind(key, action, *args))

    def register_event_callback(self, event_type: str, callback: Callback[[Event], Any], condition: Optional[Callable[[Event], bool]] = None) -> None:
        self.event_manager.register(event_type, callback, condition)
    
    def register_object(self, layer: str, *obj: PygameObject | list[PygameObject]) -> None:
        for o in obj:
            self._layer_manager.add_object(layer, o)
    
    def create_layer(self, name: str, layer_value: float, camera: Optional[Camera] = None, interactable: bool = True) -> Layer:
        cam = camera if camera is not None else self.default_camera
        return self._layer_manager.create_layer(name, layer_value, cam, interactable)
    
    def register_window(self, window: WindowObject, group: str = "main", layer: Layer | str = "ui") -> WindowObject:
        if isinstance(layer, str):
            self.register_object(layer, window)
        else:
            layer.add_object(window)
        return self.windows.register(window, group)
    
    def register_quick_debug(self, name: str, getter: Callable, template: str = "{}"):
        self.quick_debug_manager.register_listener(name, getter, template)
    
    # endregion
    
    # region OTHER
    
    def trigger_event(self, event: Event) -> None:
        self.event_manager.trigger(event)
    
    def start_async_process(self, fn: Callable, *args, **kwargs) -> AsyncProcess:
        return self.async_process_manager.submit(fn, *args, **kwargs)
    
    def open_window(self, window_id: str) -> None:
        self.windows.open(window_id)
    
    def close_window(self, window_id: str) -> None:
        self.windows.close(window_id)
    
    def quick_debug(self, name: str, value: Any) -> None:
        self.quick_debug_manager.quick_debug(name, value)
    
    # endregion
    
    def update(self, dt: float) -> None:
        self.animation_manager.update(dt)
        self.keybinds.update()
        self.event_manager.update(dt)
        
        self.frame_timer.time("Update.State.Interactions",     lambda: self.interaction_manager.update(self._layer_manager))
        self.frame_timer.time("Update.State.Async Generation", self.async_process_manager.update)
        self.frame_timer.time("Update.State.Layers",           lambda: self._layer_manager.update(dt))
        self.frame_timer.time("Update.State.Particles",        lambda: self.particle_system.update(dt))
        self.frame_timer.time("Update.State.Camera",           lambda: self.camera.update(dt))
        
        self.quick_debug_manager.update_values()
    
    def render(self) -> None:
        for layer in self._layer_manager.sorted_layers:
            layer.render(self.renderer.draw)

    # region PHYSICS

    def enable_physics(self, layer_name: str = "world", gravity: vec2 = vec2(0, 980)):
        layer = self._layer_manager.get_layer(layer_name)
        pw = layer.enable_physics(gravity)
        return pw

    # endregion
    
    def __repr__(self) -> str:
        return f"State('{self.id}')"
    