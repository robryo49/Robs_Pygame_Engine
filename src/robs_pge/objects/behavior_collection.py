from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

from .behaviors import ObjectBehavior
from ..events import Event
from ..utils import TypedCollection, vec2

if TYPE_CHECKING:
    from .object import PygameObject

class BehaviorCollection(TypedCollection):
    def __init__(self, owner):
        super().__init__(ObjectBehavior)
        
        self._owner = owner
        
    # region PROPERTIES
    
    @property
    def owner(self):
        return self._owner
    
    def __iter__(self) -> Iterator[ObjectBehavior]:
        return super().__iter__()
    
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
                self.remove(b)
            return
        
        super().remove(behavior)
        if isinstance(behavior, ObjectBehavior):
            behavior.on_detach()
            behavior.owner = None
    
    def on_hover(self):
        for b in self:
            b.on_hover()
        
    def on_hover_end(self):
        for b in self:
            b.on_hover_end()
        
    def on_hover_start(self):
        for b in self:
            b.on_hover_start()
        
    def on_click(self, button: int, pos: vec2):
        for b in self:
            b.on_click(button, pos)
        
    def on_hold(self, button: int, pos: vec2):
        for b in self:
            b.on_hold(button, pos)
        
    def on_release(self, button: int, pos: vec2):
        for b in self:
            b.on_release(button, pos)
            
    def on_update(self, dt: float):
        for b in self:
            b.on_update(dt)
            
    def on_event(self, event: Event):
        for b in self:
            b.on_event(event)
    
    def on_scroll(self, scroll: int, pos: vec2):
        for b in self:
            b.on_scroll(scroll, pos)
            
    def on_collision(self, obj: PygameObject):
        for b in self:
            b.on_collision(obj)
    
    def on_collision_end(self, obj: PygameObject):
        for b in self:
            b.on_collision_end(obj)
        
