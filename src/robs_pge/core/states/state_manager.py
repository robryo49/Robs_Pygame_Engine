from .state import State
from ...events import Event, Events


class StateManager:
    def __init__(self):
        self._state = None
        self._states: dict[str, State] = {}
        
        self._state_request = None
    
    # region PROPERTIES
    
    @property
    def state(self):
        return self._state
    
    @property
    def states(self):
        return self._states
    
    # endregion
    
    def add_state(self, state: State):
        self.states[state.id] = state
    
    def set_state(self, state: str | State):
        self._state_request = state if isinstance(state, str) else state.id
        
    def update(self, dt: float):
        if self._state_request:
            
            if self._state is not None:
                self._state.trigger_event(Event(Events.STATE_EXIT, state_id=self._state.id))
                
            self._state = self.states[self._state_request]
            
            if self._state is not None:
                self._state.trigger_event(Event(Events.STATE_ENTER, state_id=self._state.id))
                
            self._state_request = None
        
        if self.state:
            self.state.update(dt)
        
    def render(self):
        if self.state:
            self.state.render()