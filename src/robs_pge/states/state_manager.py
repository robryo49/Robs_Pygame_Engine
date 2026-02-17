from .state import State


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
        self._state_request = state.id if isinstance(state, State) else state
        
    def update(self, dt: float):
        if self._state_request:
            self._state = self.states[self._state_request]
            self._state_request = None
        
        if self.state:
            self.state.update(dt)
        
    def render(self):
        if self.state:
            self.state.render()