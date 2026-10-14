from __future__ import annotations

from typing import Iterator, TYPE_CHECKING, overload, Optional

from .behavior import ObjectBehavior, LayoutObjectBehavior
from ..events import Event
from ..utils import TypedCollection, vec2

if TYPE_CHECKING:
    from .object import PygameObject
    from .custom import LayoutObject

class BehaviorManager(TypedCollection):
    def __init__(self, owner: PygameObject):
        super().__init__(ObjectBehavior)
        self._behavior_ids: dict[str, ObjectBehavior] = {}
        self._owner: PygameObject = owner
        
    # region PROPERTIES
    
    @property
    def owner(self) -> PygameObject:
        return self._owner
    
    def __iter__(self) -> Iterator[ObjectBehavior]:
        return super().__iter__()
    
    # endregion
    
    def add(self, item: ObjectBehavior, behavior_id: Optional[str] = None) -> ObjectBehavior:
        if behavior_id is not None:
            if b := self.get(behavior_id) is not None:
                self.remove(b)
            self._behavior_ids[behavior_id] = item

        super().add(item)
        
        if isinstance(item, ObjectBehavior):
            item.owner = self.owner
            item.on_attach()
            
        return item

    def get(self, behavior_id: str) -> Optional[ObjectBehavior]:
        return self._behavior_ids.get(behavior_id)

    def get_id(self, behavior: ObjectBehavior) -> Optional[str]:
        return next((k for k, v in self._behavior_ids.items() if v is behavior), None)

    def remove(self, item: ObjectBehavior | str) -> Optional[ObjectBehavior]:
        if isinstance(item, str):
            item = self.get(item)

        super().remove(item)
        
        if isinstance(item, ObjectBehavior):
            item.on_detach()
            item.owner = None
            
        return item
    
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

