from .behaviors import ObjectBehavior
from ..events import Event
from ..utils import Collection, Vec2


class BehaviorCollection(Collection):
    def __init__(self, owner):
        super().__init__()
        
        self._owner = owner
        
    # region PROPERTIES
    
    @property
    def behaviors(self):
        return self._elements
    
    @property
    def owner(self):
        return self._owner
    
    # endregion
    
    def has(self, behavior: ObjectBehavior):
        super().has(behavior)
    
    def add(self, behavior: "ObjectBehavior | list[ObjectBehavior] | BehaviorCollection"):
        super().add(behavior)
        if isinstance(behavior, ObjectBehavior):
            behavior.owner = self.owner
            behavior.on_attach()
        
    def remove(self, behavior: "ObjectBehavior | list[ObjectBehavior] | BehaviorCollection"):
        super().remove(behavior)
        if isinstance(behavior, ObjectBehavior):
            behavior.on_detach()
            behavior.owner = None
    
    def on_hover(self):
        for behavior in self._elements:
            behavior.on_hover()
        
    def on_hover_end(self):
        for behavior in self._elements:
            behavior.on_hover_end()
        
    def on_hover_start(self):
        for behavior in self._elements:
            behavior.on_hover_start()
        
    def on_click(self, button: int, pos: Vec2):
        for behavior in self._elements:
            behavior.on_click(button, pos)
        
    def on_hold(self, button: int, pos: Vec2):
        for behavior in self._elements:
            behavior.on_hold(button, pos)
        
    def on_release(self, button: int, pos: Vec2):
        for behavior in self._elements:
            behavior.on_release(button, pos)
            
    def on_update(self, dt: float):
        for behavior in self._elements:
            behavior.on_update(dt)
            
    def on_event(self, event: Event):
        for behavior in self._elements:
            behavior.on_event(event)
    
    def on_scroll(self, scroll: int, pos: Vec2):
        for behavior in self._elements:
            behavior.on_scroll(scroll, pos)
        
