from __future__ import annotations
from typing import Any, TYPE_CHECKING, Callable

import pygame as pg

from ...animation import AnimationManager
from ...debug import FrameTimer
from ...events import Event, EventManager
from ...input import InputManager, Keybind, KeybindsManager
from ...objects import InteractionManager, ObjectCollection, ObjectFactory, PygameObject, ParticleSystem
from ...rendering import DebugPanelStyle, GraphStyle
from ...resources import ResourceManager
from ...utils import Anchor, DictCollection, Vec2, AsyncProcessManager, AsyncProcess
from ..camera import Camera

if TYPE_CHECKING:
    from ..engine import Engine
    

class State:
    def __init__(self, engine: Engine, state_id: str):
        
        self._id = state_id
        self._engine = engine
        
        self._engine.state_manager.add_state(self)
        
        self._camera = Camera(self.engine.display)
        
        self._event_manager = self._create_event_manager()
        self._animation_manager = self._create_animation_manager()
        self._keybinds_manager = self._create_keybinds_manager(self.input)
        self._particle_system = self._create_particle_system()
        self._async_process_manager = self._create_async_process_manager()
        
        self._factory = self._create_object_factory()
        
        
        self._services: DictCollection = DictCollection()
        self._factory.services = self._services
        
        self._objects: ObjectCollection = ObjectCollection()
        self._ui_objects: ObjectCollection = ObjectCollection()
        
        self._debug_overlay = self.factory.make_debug_overlay(Vec2(0, self.engine.display.dims.y), width=self.engine.display.dims.x, invert_y=True, anchor=Anchor.TL).set_constant_padding(10)

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
    
    # region SEVICES CREATION
    
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
    
    # endregion
    
    def init_debug_overlay_objects(self) -> None:
        
        green_style = self.resources.get(DebugPanelStyle, "debug_teal_panel_style")
        blue_style = self.resources.get(DebugPanelStyle, "debug_blue_panel_style")
        yellow_style = self.resources.get(DebugPanelStyle, "debug_yellow_panel_style")
        
        blue_graph_style = self.resources.get(GraphStyle, "debug_blue_graph_style")
        
        font_blue_title = self.resources.get_font("debug_blue_title")
        
        font_gray = self.resources.get_font("debug_gray_text")
        font_white = self.resources.get_font("debug_white_text")
        
        
        c1 = self.factory.make_vertical_layout(Vec2()).skip_rendering().set_cell_padding(10).invert_up_down()
        
        # region ENGINE PANNEL
        
        engine_pannel = self.factory.make_debug_panel(Vec2(), Vec2(400, 190), green_style, "ENGINE")
        
        engine_c1 = self.factory.make_vertical_layout(Vec2(), 400).skip_rendering().invert_up_down().set_constant_padding(10)
        engine_c1.stack_y(self.factory.make_dynamic_text(Vec2(), "{} FPS    |    {} ms", lambda: (round(self.clock.fps), round(self.clock.dtime*1000, 1)), font_blue_title, cache=False), anchor=Anchor.T)
        fps_graph = self.factory.make_graph(Vec2(), Vec2(380, 100), blue_graph_style, 10, 10, None, None, 0, 120, None, 5,
                                            update_action=lambda: fps_graph.insert_point(Vec2(self.clock.time, self.clock.fps)))
        engine_c1.stack_y(fps_graph, anchor=Anchor.TL)
        
        engine_pannel.panel.stack_x(engine_c1)
        
        # endregion
        
        # region FRAME PANNEL
        
        frame_pannel = self.factory.make_debug_panel(Vec2(), Vec2(400, 200), yellow_style, "FRAME TIMER").stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_text(Vec2(), "Update", font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "- Events", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "- State", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "- Input", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Rendering", font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "- Draw Calls", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "- Drawing", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "- Screen Update", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Ticking", font_white), anchor=Anchor.TL)
        ).stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update"), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update.Events"), font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update.State"), font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Update.Input"), font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering"), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Draw Calls"), font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Drawing"), font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Rendering.Screen Update"), font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ms", lambda: self.frame_timer.get_time_ms("Ticking"), font_white), anchor=Anchor.TL)
        )
        
        # endregion
        
        # region CAMERA PANEL
        
        camera_pannel = self.factory.make_debug_panel(Vec2(), Vec2(400, 132), blue_style, "CAMERA").stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_text(Vec2(), "Position", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Zoom", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Rotation", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "BL", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "TR", font_gray), anchor=Anchor.TL)
        ).stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: round(self.camera.pos, 1), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: (f"{self.camera.zoom:.2e}" if (abs(self.camera.zoom) < 0.01 or abs(self.camera.zoom) >= 1000) else f"{self.camera.zoom:.3f}"), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}°", lambda: round(self.camera.rotation, 1), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: round(Vec2(self.camera.world_aabb.topleft), 1), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: round(Vec2(self.camera.world_aabb.bottomright), 1), font_white), anchor=Anchor.TL)
        )
        
        # endregion
        
        # region INPUT PANEL
        
        input_pannel = self.factory.make_debug_panel(Vec2(), Vec2(400, 116), green_style, "INPUT").stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_text(Vec2(), "Mouse Screen Pos", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Mouse World Pos", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Held Buttons", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Held Keys", font_gray), anchor=Anchor.TL)
        ).stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: round(self.mouse.pos, 1), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: round(self.mouse.world_pos(self.camera), 1), font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.input.held_buttons, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: "{" + ", ".join(f"{pg.key.name(k)}: {v}" for k, v in list(self.input.held_keys.items())[:2]) + (f", +{len(self.input.held_keys)-2}" if len(self.input.held_keys) > 2 else "") + "}",font_white), anchor=Anchor.TL)
        )
        
        # endregion
        
        # region RENDERING PANNEL
        
        rendering_pannel = self.factory.make_debug_panel(Vec2(), Vec2(400, 176), blue_style, "RENDERING").stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_text(Vec2(), "Cache Size", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Cache Hits", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Cache Skips", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Cache Misses", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "World Draw Commands", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "UI Draw Commands", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Debug Draw Commands", font_gray), anchor=Anchor.TL).
            stack_y(self.factory.make_text(Vec2(), "Blits", font_gray), anchor=Anchor.TL)
        ).stack_pannel_x(
            self.factory.make_vertical_layout(Vec2(), 180).skip_rendering().invert_up_down().
            stack_y(self.factory.make_dynamic_text(Vec2(), "{} ({}Mo)", lambda: (self.renderer.surface_cache_size, round(self.renderer.surface_cache_memory_size, 1)), font_white, cache=False), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.cache_hits, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.cache_skips, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.cache_misses, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.world_commands_count, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.ui_commands_count, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.debug_commands_count, font_white), anchor=Anchor.TL).
            stack_y(self.factory.make_dynamic_text(Vec2(), "{}", lambda: self.renderer.blit_count, font_white), anchor=Anchor.TL)
        )
        
        # endregion
        
        c1.stack_y(engine_pannel, anchor=Anchor.TL)
        c1.stack_y(frame_pannel, anchor=Anchor.TL)
        c1.stack_y(camera_pannel, anchor=Anchor.TL)
        c1.stack_y(input_pannel, anchor=Anchor.TL)
        c1.stack_y(rendering_pannel, anchor=Anchor.TL)
        
        self.debug_overlay.stack_x(c1, anchor=Anchor.TL)
        
        self.debug_overlay.fix_col_width(0, 420)
    
    def init_resources(self) -> None:
        pass
    
    def init_services(self) -> None:
        self._services.set(AnimationManager, self.animation_manager)
        self._services.set(InputManager, self.input)
        self._services.set(ParticleSystem, self.particle_system)
        self._services.set(ObjectFactory, self.factory)
        self._services.set(EventManager, self.event_manager)
        self._services.set(AsyncProcessManager, self.async_process_manager)
        self._services.set(ResourceManager, self.resources)
    
    def init_keybinds(self) -> None:
        self.register_keybind(pg.K_F3, lambda: self.debug_overlay.toggle_visible())
        self.register_keybind(pg.K_F4, lambda: self.debug_overlay.toggle_freeze())
    
    def register_keybind(self, key: int | tuple[int, ...], action: Callable, *args) -> None:
        self.keybinds.add(Keybind(key, action, *args))
    
    def register_event_callback(self, event_type: str, callback: Callable[[Event], Any]) -> None:
        self.event_manager.register_listener(event_type, callback)
        
    def trigger_event(self, event: Event) -> None:
        self.event_manager.trigger(event)
    
    def start_async_process(self, fn: Callable, *args, **kwargs) -> AsyncProcess:
        return self.async_process_manager.submit(fn, *args, **kwargs)
        
    def add_object(self, obj: PygameObject | list[PygameObject]) -> None:
        self.objects.add(obj)
        
    def add_ui_object(self, obj: PygameObject | list[PygameObject]) -> None:
        self.ui_objects.add(obj)
        
    
    def update(self, dt: float) -> None:
        self.animation_manager.update(dt)
        self.keybinds.update()
        self.event_manager.update()
        
        self.frame_timer.time("Update.State.Interactions", lambda: self.interaction_manager.update(self.objects, self.ui_objects, self.camera))
        self.frame_timer.time("Update.State.Async Generation", self.async_process_manager.update)
        self.frame_timer.time("Update.State.UI Objects", lambda: self.ui_objects.update(dt))
        self.frame_timer.time("Update.State.World Objects", lambda: self.objects.update(dt))
        self.frame_timer.time("Update.State.Particles", lambda: self.particle_system.update(dt))
        self.frame_timer.time("Update.State.Camera", lambda: self.camera.update(dt))
        self.frame_timer.time("Update.State.Debug Overlay", lambda: self.debug_overlay.update(dt))
    
    def render(self) -> None:
        self.draw_world(self.objects)
        self.draw_particles(self.particle_system)
        self.draw_ui(self.ui_objects)
        self.draw_debug(self.debug_overlay)
    
    def draw_world(self, obj: PygameObject | ObjectCollection) -> None:
        obj.render(self.renderer.draw_world, self.camera)
    
    def draw_ui(self, obj: PygameObject | ObjectCollection) -> None:
        obj.render(self.renderer.draw_ui, self.engine.default_camera)
    
    def draw_debug(self, obj: PygameObject | ObjectCollection) -> None:
        obj.render(self.renderer.draw_debug, self.engine.default_camera)
    
    def draw_particles(self, particle_system) -> None:
        particle_system.render(self.renderer.draw_world, self.camera)