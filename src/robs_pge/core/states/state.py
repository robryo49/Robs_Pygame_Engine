"""Provides the runtime state that owns a scene's cameras, layers, and services."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, TYPE_CHECKING, Literal, cast

import pygame as pg

from .services_collection import ServicesCollection
from ..camera import Camera
from ..clock import Clock
from ...sound import Sound, SoundManager
from ...animation import AnimationManager
from ...debug import FrameTimer, QuickDebugManager
from ...events import Event, EventManager
from ...input import InputManager, Keybind, KeybindsManager
from ...input import Mouse
from ...objects import DebugOverlay, InteractionManager, Layer, LayerManager, ObjectFactory, WindowManager, WindowObject, DialogManager
from ...physics import PhysicsWorld
from ...rendering import WindowStyle, Renderer
from ...resources import ResourceManager
from ...utils import Anchor, AsyncProcessManager, Callback, ScreenAnchor, round_sig, vec2

if TYPE_CHECKING:
    from ...core import Engine
    from ...objects import PygameObject
    
    

_LAYER_WORLD = 0.0
_LAYER_UI    = 100.0
_LAYER_DEBUG = 1000.0



class State:
    """Runtime scene state containing cameras, layers, services, and managers."""

    DEBUG_DISABLED: Literal[0] = 0
    DEBUG_PERF: Literal[1] = 1
    DEBUG_FULL: Literal[2] = 2
    
    def __init__(self, engine: Engine, state_id: str, debug_mode: Literal[0, 1, 2] = DEBUG_DISABLED) -> None:
        """Register the state and build its cameras, managers, layers, and services.

        :param engine: Engine that owns this state.
        :param state_id: Unique identifier used to switch to this state.
        :param debug_mode: Debug overlay level mode.
        """
        
        self._id = state_id
        self._engine = engine
        self._engine.state_manager.register_state(self)
        
        self._camera = Camera(self.engine.display)
        self._services = self._create_services_collection()
        
        self._event_manager = self._create_event_manager()
        self._animation_manager = self._create_animation_manager()
        self._keybinds_manager = self._create_keybinds_manager(self.input)
        self._async_process_manager = self._create_async_process_manager()
        self._window_manager = self._create_window_manager(self.event_manager)
        self._quick_debug_manager = self._create_quick_debug_manager()
        
        self._factory = self._create_object_factory(self._services)

        self._layer_manager = self._create_layer_manager()
        self._debug_layer, self._ui_layer, self._world_layer = self._create_layers()

        self._dialogs_layer_id = "ui"
        self._dialogs_manager = self._create_dialog_manager(
            self._factory, self._window_manager,
            lambda o: self.register_object(self._dialogs_layer_id, o),
            lambda o: self.unregister_object(self._dialogs_layer_id, o)
        )
        
        self._debug_mode = debug_mode
        self._debug_overlay: DebugOverlay = cast(DebugOverlay,
            self.create_object.debug
            .debug_overlay(ScreenAnchor.TL, width=self.engine.display.viewport_dims.x, anchor=Anchor.TL)
            .set_cell_spacing(20, True)
        )
        self.debug_layer.add_object(self._debug_overlay)
        self.debug_layer.disable_rendering()
        
        self.init_resources()
        self.init_keybinds()
        self.init_services()
        self.init_events()
        self.init_object_constructors()
        self.init_debug_overlay_objects()
    
    # region PROPERTIES
    
    @property
    def id(self) -> str:
        """Return the unique state identifier."""
        return self._id
    
    @property
    def engine(self) -> Engine:
        """Return the engine that owns this state."""
        return self._engine
    
    @property
    def clock(self) -> Clock:
        """Return the engine clock."""
        return self.engine.clock
    
    @property
    def dt(self) -> float:
        """Return the last frame's delta time in seconds."""
        return self.clock.dtime
    
    @property
    def input(self) -> InputManager:
        """Return the shared input manager."""
        return self.engine.input
    
    @property
    def camera(self) -> Camera:
        """Return the state's world camera."""
        return self._camera
    
    @property
    def default_camera(self) -> Camera:
        """Return the engine's default camera."""
        return self.engine.default_camera
    
    @property
    def mouse(self) -> Mouse:
        """Return the shared mouse state."""
        return self.input.mouse
    
    @property
    def renderer(self) -> Renderer:
        """Return the engine renderer."""
        return self.engine.renderer
    
    @property
    def debug_overlay(self) -> DebugOverlay:
        """Return the debug overlay object."""
        return self._debug_overlay
    
    @property
    def frame_timer(self) -> FrameTimer:
        """Return the engine frame timer."""
        return self.engine.frame_timer
    
    @property
    def resources(self) -> ResourceManager:
        """Return the shared resource manager."""
        return self.engine.resources

    @property
    def sounds(self):
        """Return the shared sound manager."""
        return self.engine.sounds
    
    @property
    def animation_manager(self) -> AnimationManager:
        """Return the state's animation manager."""
        return self._animation_manager
    
    @property
    def interaction_manager(self) -> InteractionManager:
        """Return the engine's interaction manager."""
        return self.engine.interaction_manager
    
    @property
    def event_manager(self) -> EventManager:
        """Return the state's event manager."""
        return self._event_manager
    
    @property
    def async_process_manager(self) -> AsyncProcessManager:
        """Return the state's asynchronous process manager."""
        return self._async_process_manager
    
    @property
    def quick_debug_manager(self) -> QuickDebugManager:
        """Return the state's quick debug manager."""
        return self._quick_debug_manager
    
    @property
    def factory(self) -> ObjectFactory:
        """Return the state's object factory."""
        return self._factory
    
    @property
    def create_object(self) -> ObjectFactory:
        """Return the object factory used to construct game objects."""
        return self._factory
    
    @property
    def keybinds(self) -> KeybindsManager:
        """Return the state's keybind manager."""
        return self._keybinds_manager
    
    @property
    def layer_manager(self) -> LayerManager:
        """Return the state's layer manager."""
        return self._layer_manager
    
    @property
    def windows(self) -> WindowManager:
        """Return the state's window manager."""
        return self._window_manager
    
    @property
    def dialogs(self) -> DialogManager:
        """Return the state's dialog manager."""
        return self._dialogs_manager
    
    
    @property
    def debug_layer(self) -> Layer:
        """Return the debug layer."""
        return self._debug_layer
    
    @property
    def ui_layer(self) -> Layer:
        """Return the UI layer."""
        return self._ui_layer
    
    @property
    def world_layer(self) -> Layer:
        """Return the world layer."""
        return self._world_layer
    
    # endregion
    
    # region SERVICES CREATION METHODS

    @staticmethod
    def _create_services_collection() -> ServicesCollection:
        return ServicesCollection()

    def _create_layer_manager(self) -> LayerManager:
        return LayerManager(self._services)

    def _create_layers(self) -> tuple[Layer, Layer, Layer]:
        debug_layer = self.create_layer("debug", _LAYER_DEBUG, self.engine.default_camera, interactable=False)
        ui_layer = self.create_layer("ui", _LAYER_UI, self.engine.default_camera, interactable=True)
        world_layer = self.create_layer("world", _LAYER_WORLD, self.camera, interactable=True)
        return debug_layer, ui_layer, world_layer
    
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
    def _create_object_factory(services: ServicesCollection) -> ObjectFactory:
        return ObjectFactory(services)
    
    @staticmethod
    def _create_dialog_manager(object_factory, window_manager, object_registration_method, object_unregistration_method) -> DialogManager:
        return DialogManager(object_factory, window_manager, object_registration_method, object_unregistration_method)
    
    @staticmethod
    def _create_async_process_manager() -> AsyncProcessManager:
        return AsyncProcessManager()
    
    @staticmethod
    def _create_window_manager(event_manager) -> WindowManager:
        return WindowManager(event_manager)
    
    @staticmethod
    def _create_quick_debug_manager() -> QuickDebugManager:
        return QuickDebugManager()
    
    # endregion
    
    # region INIT METHODS
    
    def init_debug_overlay_objects(self) -> None:
        """Create and position debug panels according to the configured debug mode."""
        if not self._debug_mode:
            return
        
        green_style  = self.resources.get(WindowStyle, "debug_teal_panel_style")
        blue_style   = self.resources.get(WindowStyle, "debug_blue_panel_style")
        yellow_style = self.resources.get(WindowStyle, "debug_yellow_panel_style")
        red_style = self.resources.get(WindowStyle, "debug_red_panel_style")
        
        font_gray       = self.resources.get_font("debug_gray_text")
        font_white      = self.resources.get_font("debug_white_text")
        
        panels_width = 400
        titles_width = 150
        infos_width = panels_width - titles_width - 20
        
        engine_panel = self.create_object.debug.debug_info_window(vec2(), "ENGINE", panels_width, titles_width, infos_width, font_white, font_gray, blue_style)
        engine_panel.add_line("FPS", "{} ms", lambda: round(self.clock.fps))
        engine_panel.add_line("SPF", "{} ms", lambda: round(self.clock.dtime * 1000, 1))
        engine_panel.add_line("Frames Elapsed", "{} frames", lambda: self.clock.tick_num)
        engine_panel.add_line("Time Elapsed", "{} s", lambda: round(self.clock.time, 1))
        
        state_panel = self.create_object.debug.debug_info_window(vec2(), "STATE", panels_width, titles_width, infos_width, font_white, font_gray, green_style)
        state_panel.add_line("Current", "{}", lambda: self.id)
        state_panel.add_line("Layers :", "{}", lambda: "")
        for layer in list(self.layer_manager.layers.values()):
            state_panel.add_line("- " + layer.id, "{} Objects ({})", layer.get_objects_count)
        
        rendering_panel = self.create_object.debug.debug_info_window(vec2(), "RENDERING", panels_width, titles_width, infos_width, font_white, font_gray, yellow_style)
        rendering_panel.add_line("Cache Size",  "{} ({}Mo)", lambda: (self.renderer.surface_cache_size, round(self.renderer.surface_cache_memory_size, 1)))
        rendering_panel.add_line("Cache Hits",  "{}", lambda: self.renderer.cache_hits)
        rendering_panel.add_line("Cache Skips", "{}", lambda: self.renderer.cache_skips)
        rendering_panel.add_line("Cache Misses", "{}", lambda: self.renderer.cache_misses)
        rendering_panel.add_line("Blits count", "{}", lambda: self.renderer.blit_count)
        
        frame_panel = self.create_object.debug.debug_info_window(vec2(), "FRAME", panels_width, titles_width, infos_width, font_white, font_gray, red_style)
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
        
        camera_panel = self.create_object.debug.debug_info_window(vec2(), "CAMERA", panels_width, titles_width, infos_width, font_white, font_gray, blue_style)
        camera_panel.add_line("Position",       "{}", lambda: self.camera.pos.to_tuple())
        camera_panel.add_line("Zoom",           "{}x (min: {} max: {})", lambda: (round_sig(self.camera.zoom, 2), self.camera.min_zoom, self.camera.max_zoom))
        camera_panel.add_line("Rotation",       "{}°", lambda: round(self.camera.rotation, 1))
        
        mouse_panel = self.create_object.debug.debug_info_window(vec2(), "MOUSE", panels_width, titles_width, infos_width, font_white, font_gray, green_style)
        mouse_panel.add_line("Screen Position", "{}", lambda: self.mouse.pos.to_tuple())
        mouse_panel.add_line("Camera Position", "{}", lambda: self.camera.screen_to_camera_pos(self.mouse.pos).to_tuple())
        mouse_panel.add_line("World Position",  "{}", lambda: self.camera.screen_to_world_pos(self.mouse.pos).to_tuple())
        mouse_panel.add_line("Pressed Buttons", "{}", lambda: self.mouse.held_buttons)
        mouse_panel.add_line("Hovered",         "{}", lambda: self.interaction_manager.hovered)

        input_panel = self.create_object.debug.debug_info_window(vec2(), "INPUT", panels_width, titles_width, infos_width, font_white, font_gray, yellow_style)
        input_panel.add_line("Pressed Keys",    "{}", lambda: '{' + ", ".join(": ".join([pg.key.name(k), str(t)]) for k, t in self.input.held_keys.items()) + '}')
        
        animation_panel = self.create_object.debug.debug_info_window(vec2(), "ANIMATION", panels_width, titles_width, infos_width, font_white, font_gray, blue_style)
        animation_panel.add_line("Running",     "{}", lambda: len(self.animation_manager.active))
        animation_panel.add_line("Scheduled",   "{}", lambda: len(self.animation_manager.scheduled))
        
        async_panel = self.create_object.debug.debug_info_window(vec2(), "ASYNC", panels_width, titles_width, infos_width, font_white, font_gray, red_style)
        async_panel.add_line("Running",         "{}", lambda: self.async_process_manager.pending_count)
        
        quick_debug_panel = self.create_object.debug.dynamic_debug_info_window(vec2(), "QUICK DEBUG", panels_width, self.quick_debug_manager.get_values, titles_width-85, infos_width+85, font_white, font_gray, yellow_style)
    
        
        if self._debug_mode >= self.DEBUG_PERF: self.debug_overlay.stack_y(engine_panel, 0, Anchor.TL)
        if self._debug_mode >= self.DEBUG_PERF: self.debug_overlay.stack_y(state_panel, 0, Anchor.TL)
        if self._debug_mode >= self.DEBUG_PERF: self.debug_overlay.stack_y(rendering_panel, 0, Anchor.TL)
        if self._debug_mode >= self.DEBUG_PERF: self.debug_overlay.stack_y(frame_panel, 0, Anchor.TL)
        if self._debug_mode >= self.DEBUG_FULL: self.debug_overlay.stack_y(camera_panel, 0, Anchor.TL)
        if self._debug_mode >= self.DEBUG_FULL: self.debug_overlay.stack_y(mouse_panel, 0, Anchor.TL)
        
        if self._debug_mode >= self.DEBUG_FULL: self.debug_overlay.stack_y(input_panel, 1, Anchor.TL)
        if self._debug_mode >= self.DEBUG_FULL: self.debug_overlay.stack_y(animation_panel, 1, Anchor.TL)
        if self._debug_mode >= self.DEBUG_FULL: self.debug_overlay.stack_y(async_panel, 1, Anchor.TL)
        
        cols = 2 if self._debug_mode >= self.DEBUG_FULL else 1
        self.debug_overlay.set_fixed_col_width(self.engine.default_camera.viewport_width - cols * (panels_width + 20) - 40, 2)
        if self._debug_mode >= self.DEBUG_PERF: self.debug_overlay.stack_y(quick_debug_panel, 2, Anchor.TR)
    
    def init_resources(self) -> None:
        """Hook for subclass-specific resource setup."""

    def init_services(self) -> None:
        """Populate the service collection after all managers exist."""
        self._services.init(
            self,
            self.animation_manager,
            self.input,
            self.factory,
            self.event_manager,
            self.async_process_manager,
            self.resources,
            self.sounds,
            self.quick_debug_manager
        )
    
    def init_keybinds(self) -> None:
        """Register the default F3 and F4 debug layer toggles."""
        self.register_keybind(pg.K_F3, lambda: self.debug_layer.toggle_rendering())
        self.register_keybind(pg.K_F4, lambda: self.debug_layer.toggle_frozen())
    
    def init_events(self) -> None:
        """Hook for subclass-specific event registration."""

    def init_object_constructors(self) -> None:
        """Hook for subclass-specific object constructor registration."""
    
    # endregion
    
    # region REGISTRATION METHODS
    
    def register_object_constructor(self, name: str, constructor: Callable[[...], PygameObject]) -> None:
        """Register a named object constructor on the factory.

        :param name: Constructor name used by the factory.
        :param constructor: Callable that builds a game object.
        """
        self.factory.register_constructor(name, constructor)
    
    def register_keybind(self, key: int | tuple[int, ...], action: Callback[[], Any], *args) -> None:
        """Register a keybind that runs an action when its key is pressed.

        :param key: Key code or tuple of key codes to bind.
        :param action: Callback invoked when the keybind activates.
        :param args: Additional arguments forwarded to the keybind.
        """
        self.keybinds.register(Keybind(key, action, *args))

    def register_event_callback(self, event_type: str, callback: Callback[[Event], Any], condition: Optional[Callable[[Event], bool]] = None) -> None:
        """Register a callback for an event type.

        :param event_type: Event type identifier to listen for.
        :param callback: Callback invoked with the matching event.
        :param condition: Optional predicate that must return True before dispatch.
        """
        self.event_manager.register(event_type, callback, condition)
    
    def register_object(self, layer: Layer | str, obj: PygameObject | list[PygameObject]) -> None:
        """Register one or more objects on a layer.

        :param layer: Layer instance or layer identifier.
        :param obj: Object or list of objects to add.
        """
        self._layer_manager.add_object(layer, obj)

    def unregister_object(self, layer: Layer | str, obj: PygameObject | list[PygameObject]) -> None:
        """Unregister one or more objects from a layer.

        :param layer: Layer instance or layer identifier.
        :param obj: Object or list of objects to remove.
        """
        self._layer_manager.remove_object(layer, obj)

    def create_layer(self, name: str, layer_value: float, camera: Optional[Camera] = None, interactable: bool = True) -> Layer:
        """Create a layer using the supplied or default camera.

        :param name: Unique layer name.
        :param layer_value: Sort value that determines draw order.
        :param camera: Camera for the layer; defaults to the engine camera.
        :param interactable: Whether objects on the layer receive interaction updates.
        :return: The created layer.
        """
        cam = camera if camera is not None else self.default_camera
        return self._layer_manager.create_layer(name, layer_value, cam, interactable)
    
    def register_window(self, window: WindowObject, group: Optional[str] = None, layer: Layer | str = "ui") -> None:
        """Register a window on a layer and with the window manager.

        :param window: Window object to register.
        :param group: Optional window group name.
        :param layer: Layer instance or layer identifier.
        """
        if isinstance(layer, str):
            self.register_object(layer, window)
        else:
            layer.add_object(window)
        self.windows.register(window, group)
    
    def register_windows(self, windows: Iterable[WindowObject], group: Optional[str] = None, layer: Layer | str = "ui") -> None:
        """Register multiple windows on a layer and with the window manager.

        :param windows: Window objects to register.
        :param group: Optional window group name.
        :param layer: Layer instance or layer identifier.
        """
        for window in windows:
            self.register_window(window, group, layer)
    
    def unregister_window(self, window: WindowObject, layer: Layer | str = "ui") -> None:
        """Unregister a window from a layer and from the window manager.

        :param window: Window object to unregister.
        :param layer: Layer instance or layer identifier.
        """
        if isinstance(layer, str):
            self.unregister_object(layer, window)
        else:
            layer.remove_object(window)
        self.windows.unregister(window)
    
    def unregister_windows(self, windows: Iterable[WindowObject], layer: Layer | str = "ui") -> None:
        """Unregister multiple windows from a layer and from the window manager.

        :param windows: Window objects to unregister.
        :param layer: Layer instance or layer identifier.
        """
        for window in windows:
            self.unregister_window(window, layer)
    
    def register_quick_debug(self, name: str, getter: Callable, template: str = "{}") -> None:
        """Register a named value getter for the quick debug panel.

        :param name: Display name for the value.
        :param getter: Callable that returns the value to display.
        :param template: Format template applied to the getter result.
        """
        self.quick_debug_manager.register_listener(name, getter, template)
    
    # endregion
    
    # region OTHER
    
    def trigger_event(self, event: Event) -> None:
        """Queue an event on the state event manager.

        :param event: Event to queue.
        """
        self.event_manager.trigger(event)

    def play_sound(self, sound: Sound | str, volume: float=1.0, loops: int = 0,
                   max_time: float = 0.0, fade_time: float = 0.0, category: str = "main"):
        self.sounds.play_sound(sound, volume, loops, max_time, fade_time, category)
    
    def start_async_process(self, fn: Callable, *args, **kwargs) -> None:
        """Submit a callable to the asynchronous process manager.

        :param fn: Callable to run asynchronously.
        :param args: Positional arguments forwarded to the callable.
        :param kwargs: Keyword arguments forwarded to the callable.
        """
        self.async_process_manager.submit(fn, *args, **kwargs)
    
    def open_window(self, window_id: str | WindowObject) -> None:
        """Open a registered window.

        :param window_id: Window identifier or window object.
        """
        self.windows.open(window_id)
    
    def close_window(self, window_id: str | WindowObject) -> None:
        """Close a registered window.

        :param window_id: Window identifier or window object.
        """
        self.windows.close(window_id)
    
    def quick_debug(self, name: str, value: Any, duration: float = 0.0) -> None:
        """Display a transient value in the quick debug panel.

        :param name: Display name for the value.
        :param value: Value to display.
        :param duration: Seconds to keep the value visible.
        """
        self.quick_debug_manager.quick_debug(name, value, duration)
    
    # endregion
    
    def update(self, dt: float) -> None:
        """Advance animations, input, events, interactions, layers, and the camera.

        :param dt: Elapsed time in seconds.
        """
        self.animation_manager.update(dt)
        self.keybinds.update()
        self.event_manager.update(dt)
        
        self.frame_timer.time("Update.State.Interactions",     lambda: self.interaction_manager.update(self._layer_manager))
        self.frame_timer.time("Update.State.Async Generation", self.async_process_manager.update)
        self.frame_timer.time("Update.State.Layers",           lambda: self._layer_manager.update(dt))
        self.frame_timer.time("Update.State.Camera",           lambda: self.camera.update(dt))
        
        self.quick_debug_manager.update(dt)
    
    def render(self) -> None:
        """Render all layers through the state renderer."""
        self._layer_manager.render(self.renderer.draw)

    # region PHYSICS

    def enable_physics(self, layer_name: str = "world", gravity: vec2 = vec2(0, 980)) -> PhysicsWorld:
        """Enable physics on a layer and return its physics world.

        :param layer_name: Name of the layer to enable physics on.
        :param gravity: Gravity vector applied by the physics world.
        :return: Physics world attached to the layer.
        """
        layer = self._layer_manager.get_layer(layer_name)
        pw = layer.enable_physics(gravity)
        return pw

    # endregion
    
    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"State('{self.id}')"
    