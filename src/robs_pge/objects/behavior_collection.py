from .behaviors import ObjectBehavior
from ..events import Event
from ..utils import TypedCollection, Vec2


class BehaviorCollection(TypedCollection):
    def __init__(self, owner):
        super().__init__(ObjectBehavior)
        
        self._owner = owner
        
    # region PROPERTIES
    
    @property
    def owner(self):
        return self._owner
    
    # endregion
    
    def add_behavior(self, behavior: "ObjectBehavior | list[ObjectBehavior] | BehaviorCollection"):
        
        if isinstance(behavior, list):
            for b in behavior:
                self.add_behavior(b)
            return
        
        super().add(behavior)
        if isinstance(behavior, ObjectBehavior):
            behavior.owner = self.owner
            behavior.on_attach()
        
    def remove(self, behavior: "ObjectBehavior | list[ObjectBehavior] | BehaviorCollection"):
        
        if isinstance(behavior, list):
            for b in behavior:
                self.add_behavior(b)
            return
        
        super().remove(behavior)
        if isinstance(behavior, ObjectBehavior):
            behavior.on_detach()
            behavior.owner = None
    
    def on_hover(self):
        self.foreach(lambda b: b.on_hover())
        
    def on_hover_end(self):
        self.foreach(lambda b: b.on_hover_end())
        
    def on_hover_start(self):
        self.foreach(lambda b: b.on_hover_start())
        
    def on_click(self, button: int, pos: Vec2):
        self.foreach(lambda b: b.on_click(button, pos))
        
    def on_hold(self, button: int, pos: Vec2):
        self.foreach(lambda b: b.on_hold(button, pos))
        
    def on_release(self, button: int, pos: Vec2):
        self.foreach(lambda b: b.on_release(button, pos))
            
    def on_update(self, dt: float):
        self.foreach(lambda b: b.on_update(dt))
            
    def on_event(self, event: Event):
        self.foreach(lambda b: b.on_event(event))
    
    def on_scroll(self, scroll: int, pos: Vec2):
        self.foreach(lambda b: b.on_scroll(scroll, pos))
        
