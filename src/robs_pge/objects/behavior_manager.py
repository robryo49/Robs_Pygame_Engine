from __future__ import annotations

from typing import Iterator, TYPE_CHECKING, overload

from .behaviors import ObjectBehavior
from ..events import Event
from ..utils import TypedCollection, vec2

if TYPE_CHECKING:
    from .object import PygameObject

class BehaviorManager(TypedCollection):
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
    
    def add(self, item: ObjectBehavior) -> ObjectBehavior:
        super().add(item)
        
        if isinstance(item, ObjectBehavior):
            item.owner = self.owner
            item.on_attach()
            
        return item
    
    def remove(self, item: ObjectBehavior) -> ObjectBehavior:
        super().remove(item)
        
        if isinstance(item, ObjectBehavior):
            item.on_detach()
            item.owner = None
            
        return item
    
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
        
