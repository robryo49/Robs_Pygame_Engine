from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core import State
    from ...animation import AnimationManager
    from ...input import InputManager
    from ...objects import ParticleSystem, ObjectFactory
    from ...events import EventManager
    from ...utils import AsyncProcessManager
    from ...resources import ResourceManager
    from ...debug import QuickDebugManager


class ServicesCollection:
    def __init__(self):
        self._state: State
        self._animation_manager: AnimationManager
        self._input_manager: InputManager
        self._particle_system: ParticleSystem
        self._object_factory: ObjectFactory
        self._event_manager: EventManager
        self._async_process_manager: AsyncProcessManager
        self._resource_manager: ResourceManager
        self._quick_debug_manager: QuickDebugManager

    def init(
            self,
            state: State,
            animation_manager: AnimationManager,
            input_manager: InputManager,
            particle_system: ParticleSystem,
            object_factory: ObjectFactory,
            event_manager: EventManager,
            async_process_manager: AsyncProcessManager,
            resource_manager: ResourceManager,
            quick_debug_manager: QuickDebugManager
    ) -> None:
        self._state = state
        self._animation_manager = animation_manager
        self._input_manager = input_manager
        self._particle_system = particle_system
        self._object_factory = object_factory
        self._event_manager = event_manager
        self._async_process_manager = async_process_manager
        self._resource_manager = resource_manager
        self._quick_debug_manager = quick_debug_manager

    def get_state(self) -> State:
        return self._state

    def get_animation_manager(self) -> AnimationManager:
        return self._animation_manager

    def get_input_manager(self) -> InputManager:
        return self._input_manager

    def get_particle_system(self) -> ParticleSystem:
        return self._particle_system

    def get_object_factory(self) -> ObjectFactory:
        return self._object_factory

    def get_event_manager(self) -> EventManager:
        return self._event_manager

    def get_async_process_manager(self) -> AsyncProcessManager:
        return self._async_process_manager

    def get_resource_manager(self) -> ResourceManager:
        return self._resource_manager

    def get_quick_debug_manager(self) -> QuickDebugManager:
        return self._quick_debug_manager

