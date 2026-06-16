from utils import Vec2
from events import Event


class ObjectBehavior:
    def __init__(self):
        self._object = None
    
    # region PROPERTIES
    
    # region object
    @property
    def owner(self):
        return self._object
    
    @owner.setter
    def owner(self, value):
        self._object = value
    # endregion
    
    # endregion
    
    def on_click(self, button: int, pos: Vec2): pass
    def on_hold(self, button: int, pos: Vec2): pass
    def on_release(self, button: int, pos: Vec2): pass
    
    def on_hover_start(self): pass
    def on_hover(self): pass
    def on_hover_end(self): pass
    
    def on_event(self, event: Event): pass
    
    def on_attach(self): pass
    def on_detach(self): pass
    
    def on_update(self, dt: float): pass