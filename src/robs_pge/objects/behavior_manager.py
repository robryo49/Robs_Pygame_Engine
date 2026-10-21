from __future__ import annotations

from typing import Iterator, TYPE_CHECKING, Optional

from .behavior import ObjectBehavior, LayoutObjectBehavior
from ..events import Event
from ..utils import vec2

if TYPE_CHECKING:
    from .object import PygameObject
    from .custom import LayoutObject

class BehaviorManager:
    def __init__(self, owner: PygameObject):
        self._behaviors: dict[str, ObjectBehavior] = {}
        self._owner: PygameObject = owner
        
    # region PROPERTIES
    
    @property
    def owner(self) -> PygameObject:
        return self._owner
    
    def __iter__(self) -> Iterator[ObjectBehavior]:
        return iter(self._behaviors.values())
    
    # endregion
    
    def add(self, behavior: ObjectBehavior, behavior_id: Optional[str] = None) -> ObjectBehavior:
        if behavior_id is None:
            behavior_id = str(hash(behavior))

        if b := self.get(behavior_id) is not None:
            self.remove(b)
        self._behaviors[behavior_id] = behavior
        
        behavior.owner = self.owner
        behavior.on_attach()
            
        return behavior

    def get(self, behavior_id: str) -> Optional[ObjectBehavior]:
        return self._behaviors.get(behavior_id)

    def get_id(self, behavior: ObjectBehavior) -> Optional[str]:
        return next((k for k, v in self._behaviors.items() if v is behavior), None)

    def remove(self, behavior: ObjectBehavior | str) -> Optional[ObjectBehavior]:
        if isinstance(behavior, str):
            behavior_id = behavior
            behavior = self._behaviors.get(behavior_id)
        else:
            behavior_id = self.get_id(behavior)

        if behavior_id is not None:
            self._behaviors.pop(behavior_id)

        if behavior is not None:
            behavior.on_detach()
            behavior.owner = None
            
        return behavior
    
    def on_hover(self) -> None:
        for b in self:
            b.on_hover()
        
    def on_hover_end(self) -> None:
        for b in self:
            b.on_hover_end()
        
    def on_hover_start(self) -> None:
        for b in self:
            b.on_hover_start()
        
    def on_click(self, button: int, pos: vec2) -> None:
        for b in self:
            b.on_click(button, pos)
        
    def on_hold(self, button: int, pos: vec2) -> None:
        for b in self:
            b.on_hold(button, pos)
        
    def on_release(self, button: int, pos: vec2) -> None:
        for b in self:
            b.on_release(button, pos)
            
    def on_update(self, dt: float) -> None:
        for b in self:
            b.on_update(dt)
            
    def on_event(self, event: Event) -> None:
        for b in self:
            b.on_event(event)
    
    def on_scroll(self, scroll: int, pos: vec2) -> None:
        for b in self:
            b.on_scroll(scroll, pos)
            
    def on_collision(self, obj: PygameObject) -> None:
        for b in self:
            b.on_collision(obj)
    
    def on_collision_end(self, obj: PygameObject) -> None:
        for b in self:
            b.on_collision_end(obj)


class LayoutBehaviorManager(BehaviorManager):
    def __init__(self, owner: LayoutObject):
        super().__init__(owner)

    def on_object_addition(self, obj: PygameObject):
        for b in self:
            if isinstance(b, LayoutObjectBehavior):
                b.on_object_addition(obj)

    def on_object_removal(self, obj: PygameObject):
        for b in self:
            if isinstance(b, LayoutObjectBehavior):
                b.on_object_removal(obj)

