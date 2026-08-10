from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

import pygame as pg

from ..camera import Camera
from ...animation import AnimationManager
from ...debug import FrameTimer, QuickDebugManager
from ...events import Event, EventManager
from ...input import InputManager, Keybind, KeybindsManager
from ...objects import InteractionManager, Layer, LayerManager, ObjectFactory, ParticleSystem, WindowManager, WindowObject
from ...rendering import LineChartStyle, WindowStyle
from ...resources import ResourceManager
from ...utils import Anchor, AsyncProcess, AsyncProcessManager, DictCollection, vec2, Callback

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
            .debug_overlay(vec2(), width=self.engine.display.viewport_dims.x, anchor=Anchor.TL)
            .set_constant_padding(10)
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
        
        blue_line_chart_style = self.resources.get(LineChartStyle, "debug_blue_line_chart_style")
        
        font_blue_title = self.resources.get_font("debug_blue_title")
        font_gray       = self.resources.get_font("debug_gray_text")
        font_white      = self.resources.get_font("debug_white_text")
        
        c1 = self.create_object.ui.layouts.vertical_layout(vec2()).skip_rendering().set_cell_padding(10)
        c2 = self.create_object.ui.layouts.vertical_layout(vec2()).skip_rendering().set_cell_padding(10)
        
        # region ENGINE PANEL
        
        engine_pannel = self.create_object.window.regular(vec2(), vec2(400, 190), "ENGINE", style=green_style)
        
        engine_c1 = (
            self.create_object.ui.layouts.vertical_layout(vec2(), 400)
            .skip_rendering().set_constant_padding(10)
        )
        engine_c1.stack_y(
            self.create_object.text.dynamic_label(
                vec2(), "{} FPS    |    {} ms",
                lambda: (round(self.clock.fps), round(self.clock.dtime * 1000, 1)),
                font_blue_title, cache=False
            ),
            anchor=Anchor.T
        )
        fps_line_chart = self.create_object.ui.line_chart(
            vec2(), vec2(380, 100), blue_line_chart_style, 10, 10, None, None, 0, 120, None, 5,
            update_action=lambda o: fps_line_chart.insert_point(vec2(self.clock.time, self.clock.fps))
        )
        engine_c1.stack_y(fps_line_chart, anchor=Anchor.TL)
        engine_pannel.content.stack_x(engine_c1)
        
        # endregion
        
        # region FRAME PANEL
        
        frame_pannel = (
            self.create_object.window.regular(vec2(), vec2(400, 200), "FRAME TIMER", style=yellow_style)
            .stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.label(vec2(), "Update", font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "- Events", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "- State", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "- Input", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Rendering", font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "- Draw Calls", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "- Drawing", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "- Screen Update", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Ticking", font_white), anchor=Anchor.TL)
            ).stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update"), font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update.Events"), font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update.State"), font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update.Input"), font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering"), font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Draw Calls"), font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Drawing"), font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Screen Update"), font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Ticking"), font_white), anchor=Anchor.TL)
            )
        )
        
        # endregion
        
        # region CAMERA PANEL
        
        camera_pannel = (
            self.create_object.window.regular(vec2(), vec2(400, 94), "CAMERA", style=blue_style)
            .stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.label(vec2(), "Position", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Zoom", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Rotation", font_gray), anchor=Anchor.TL)
            ).stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: list(self.camera.pos), font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: (f"{self.camera.zoom:.2e}" if (abs(self.camera.zoom) < 0.01 or abs(self.camera.zoom) >= 1000) else f"{self.camera.zoom:.3f}"), font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}°", lambda: round(self.camera.rotation, 1), font_white), anchor=Anchor.TL)
            )
        )
        
        # endregion
        
        # region INPUT PANEL
        
        input_pannel = (
            self.create_object.window.regular(vec2(), vec2(400, 116), "INPUT", style=green_style)
            .stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.label(vec2(), "Mouse Screen Pos", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Mouse World Pos", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Held Buttons", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Held Keys", font_gray), anchor=Anchor.TL)
            ).stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: list(self.mouse.pos), font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: list(self.mouse.world_pos(self.camera)), font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: self.input.held_buttons, font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(
                    vec2(), "{}",
                    lambda: "{" + ", ".join(f"{pg.key.name(k)}: {v}" for k, v in list(self.input.held_keys.items())[:2])
                            + (f", +{len(self.input.held_keys) - 2}" if len(self.input.held_keys) > 2 else "") + "}",
                    font_white
                ), anchor=Anchor.TL)
            )
        )
        
        # endregion
        
        # region RENDERING PANEL
        
        rendering_pannel = (
            self.create_object.window.regular(vec2(), vec2(400, 150), "RENDERING", style=blue_style)
            .stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.label(vec2(), "Cache Size", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Cache Hits", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Cache Skips", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Cache Misses", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Commands", font_gray), anchor=Anchor.TL)
                .stack_y(self.create_object.text.label(vec2(), "Blits", font_gray), anchor=Anchor.TL)
            ).stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{} ({}Mo)", lambda: (self.renderer.surface_cache_size, round(self.renderer.surface_cache_memory_size, 1)), font_white, cache=False), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: self.renderer.cache_hits, font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: self.renderer.cache_skips, font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: self.renderer.cache_misses, font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: self.renderer.total_commands_count, font_white), anchor=Anchor.TL)
                .stack_y(self.create_object.text.dynamic_label(vec2(), "{}", lambda: self.renderer.blit_count, font_white), anchor=Anchor.TL)
            )
        )
        
        # endregion
        
        # region QUICK DEBUG PANEL
        
        quick_debug_pannel = (
            self.create_object.window.regular(vec2(), vec2(400, 200), "QUICK DEBUG", style=yellow_style)
            .stack_content_x(
                self.create_object.ui.layouts.vertical_layout(vec2(), 180).skip_rendering()
                .stack_y(
                    self.create_object.text.dynamic_label(
                        vec2(), "{}",
                        lambda: ("\n".join(self.quick_debug_manager.get_values()))
                        if self._quick_debug_manager.has_values() else "Nothing to Show",
                        font_white
                    ),
                    anchor=Anchor.TL
                )
                .set_outer_padding(10),
                anchor=Anchor.TL
            )
        )
        quick_debug_pannel.unfix_height()
        
        # endregion
        
        c1.stack_y(engine_pannel,    anchor=Anchor.TL)
        c1.stack_y(frame_pannel,     anchor=Anchor.TL)
        c1.stack_y(camera_pannel,    anchor=Anchor.TL)
        c1.stack_y(input_pannel,     anchor=Anchor.TL)
        c1.stack_y(rendering_pannel, anchor=Anchor.TL)
        
        c2.stack_y(quick_debug_pannel, anchor=Anchor.TR)
        
        self.debug_overlay.stack_x(c1, anchor=Anchor.TL)
        self.debug_overlay.stack_x(c2, anchor=Anchor.TR)
        
        self.debug_overlay.fix_col_width(0, 420)
    
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
    
    def add_quick_debug(self, getter: Callable, template: str = "{}"):
        self.quick_debug_manager.register_listener(getter, template)
    
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
    
    def quick_debug(self, *infos: Any) -> None:
        self.quick_debug_manager.quick_debug(infos)
    
    # endregion
    
    def update(self, dt: float) -> None:
        self.animation_manager.update(dt)
        self.keybinds.update()
        self.event_manager.update()
        
        self.frame_timer.time("Update.State.Interactions",     lambda: self.interaction_manager.update(self._layer_manager))
        self.frame_timer.time("Update.State.Async Generation", self.async_process_manager.update)
        self.frame_timer.time("Update.State.Layers",           lambda: self._layer_manager.update(dt))
        self.frame_timer.time("Update.State.Particles",        lambda: self.particle_system.update(dt))
        self.frame_timer.time("Update.State.Camera",           lambda: self.camera.update(dt))
    
    def render(self) -> None:
        for layer in self._layer_manager.sorted_layers:
            layer.render(self.renderer.draw)

    # region PHYSICS

    def enable_physics(self, layer_name: str = "world", gravity: vec2 = vec2(0, 980)):
        layer = self._layer_manager.get_layer(layer_name)
        pw = layer.enable_physics(gravity)
        return pw

    # endregion
    