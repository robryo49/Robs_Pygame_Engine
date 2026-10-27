"""Provides state registration and deferred state switching between frames."""

from typing import Optional

from .state import State
from ... import State
from ...events import Event, Events


class StateManager:
    """Registers states and switches between them between update frames."""

    def __init__(self) -> None:
        """Initialize an empty state registry with no pending switch."""
        self._state: Optional[State] = None
        self._states: dict[str, State] = {}

        self._state_request: Optional[str] = None
    
    # region PROPERTIES
    
    @property
    def state(self) -> Optional[State]:
        """Return the currently active state, if any."""
        return self._state

    @property
    def states(self) -> dict[str, State]:
        """Return the registered states keyed by identifier."""
        return self._states
    
    # endregion
    
    def register_state(self, state: State) -> "StateManager":
        """Register a state by id and return it.

        :param state: State instance to register.
        :return: This manager for chaining.
        """
        self.states[state.id] = state
        return self

    def set_state(self, state: str | State) -> "StateManager":
        """Queue a state switch for the next update.

        :param state: State instance or registered state identifier.
        :return: This manager for chaining.
        """
        self._state_request = state if isinstance(state, str) else state.id
        return self

    def update(self, dt: float) -> "StateManager":
        """Apply a pending state switch, then update the active state.

        :param dt: Elapsed time in seconds.
        :return: This manager for chaining.
        """
        if self._state_request:
            
            if self._state is not None:
                self._state.trigger_event(Event(Events.STATE_EXIT, state_id=self._state.id))
                self._state.on_open()
                
            self._state = self.states[self._state_request]
            self._state_request = None
            
            if self._state is not None:
                self._state.trigger_event(Event(Events.STATE_ENTER, state_id=self._state.id))
                self._state.on_close()

        if (s := self.state) is not None:
            s.update(dt)

        return self
        
    def render(self) -> "StateManager":
        """Render the currently active state, if one exists."""
        if (s := self.state) is not None:
            s.render()

        return self