"""Provides a container that exposes shared services to state-managed objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core import State
    from ...animation import AnimationManager
    from ...input import InputManager
    from ...objects import ObjectFactory
    from ...events import EventManager
    from ...utils import AsyncProcessManager
    from ...resources import ResourceManager
    from ...debug import QuickDebugManager


class ServicesCollection:
    """Hold references to the managers and resources shared within a state."""

    def __init__(self) -> None:
        """Initialize an empty collection to be populated by init()."""
        self._state: State
        self._animation_manager: AnimationManager
        self._input_manager: InputManager
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
            object_factory: ObjectFactory,
            event_manager: EventManager,
            async_process_manager: AsyncProcessManager,
            resource_manager: ResourceManager,
            quick_debug_manager: QuickDebugManager
    ) -> None:
        """Populate the collection with a state and its shared services.

        :param state: State that owns the collection.
        :param animation_manager: Animation manager for the state.
        :param input_manager: Shared input manager.
        :param object_factory: Factory used to create game objects.
        :param event_manager: Event manager for the state.
        :param async_process_manager: Manager for asynchronous work.
        :param resource_manager: Shared resource manager.
        :param quick_debug_manager: Manager for quick debug values.
        """
        self._state = state
        self._animation_manager = animation_manager
        self._input_manager = input_manager
        self._object_factory = object_factory
        self._event_manager = event_manager
        self._async_process_manager = async_process_manager
        self._resource_manager = resource_manager
        self._quick_debug_manager = quick_debug_manager

    def get_state(self) -> State:
        """Return the state that owns this collection.

        :return: Owning state.
        """
        return self._state

    def get_animation_manager(self) -> AnimationManager:
        """Return the state's animation manager.

        :return: Animation manager.
        """
        return self._animation_manager

    def get_input_manager(self) -> InputManager:
        """Return the shared input manager.

        :return: Input manager.
        """
        return self._input_manager

    def get_object_factory(self) -> ObjectFactory:
        """Return the state's object factory.

        :return: Object factory.
        """
        return self._object_factory

    def get_event_manager(self) -> EventManager:
        """Return the state's event manager.

        :return: Event manager.
        """
        return self._event_manager

    def get_async_process_manager(self) -> AsyncProcessManager:
        """Return the state's asynchronous process manager.

        :return: Asynchronous process manager.
        """
        return self._async_process_manager

    def get_resource_manager(self) -> ResourceManager:
        """Return the shared resource manager.

        :return: Resource manager.
        """
        return self._resource_manager

    def get_quick_debug_manager(self) -> QuickDebugManager:
        """Return the state's quick debug manager.

        :return: Quick debug manager.
        """
        return self._quick_debug_manager

