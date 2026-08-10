from __future__ import annotations

from typing import Any, Callable, Iterable, TYPE_CHECKING

from ..rendering import DrawCommand
from ..utils import TypedCollection

if TYPE_CHECKING:
    from ..objects import PygameObject
    

class ObjectCollection(TypedCollection):
    def __init__(self, objects: Iterable[PygameObject] = ()):
        from ..objects import PygameObject
        
        super().__init__(PygameObject, objects)
        
        self._to_remove: list[PygameObject] = []
        self._to_add: list[PygameObject] = []
        
        self._frozen = False
        self._rendering_enabled = True
        
    # region PROPERTIES
    
    @property
    def frozen(self):
        return self._frozen
    
    @property
    def rendering_enabled(self):
        return self._rendering_enabled
    
    # endregion
    
    
    def toggle_rendering(self) -> "ObjectCollection":
        self._rendering_enabled = not self._rendering_enabled
        return self
    
    def enable_rendering(self) -> "ObjectCollection":
        self._rendering_enabled = True
        return self
    
    def disable_rendering(self) -> "ObjectCollection":
        self._rendering_enabled = False
        return self
    
    
    def toggle_frozen(self) -> "ObjectCollection":
        self._frozen = not self._frozen
        return self
    
    def freeze(self) -> "ObjectCollection":
        self._frozen = True
        return self
    
    def unfreeze(self) -> "ObjectCollection":
        self._frozen = False
        return self
    
    def _handle_object_additions(self) -> "ObjectCollection":
        if not self._to_add:
            return self
        
        self.extend(self._to_add)
        self._to_add.clear()
        return self
        
    def _handle_object_removals(self) -> "ObjectCollection":
        if not self._to_remove:
            return self
        
        for o in self._to_remove:
            self.remove(o)
            
        self._to_remove.clear()
        return self
    
    def add(self, item: PygameObject) -> PygameObject:
        self._to_add.append(item)
        return item
    
    def add_object(self, *obj: PygameObject | Iterable[PygameObject]) -> "ObjectCollection":
        for o in obj:
            if isinstance(o, Iterable):
                self.add_object(*o)
            else:
                self._to_add.append(o)
        return self
    
    def remove(self, item: PygameObject) -> PygameObject:
        self._to_remove.append(item)
        return item
        
    def remove_object(self, *obj: PygameObject | Iterable[PygameObject]) -> "ObjectCollection":
        for o in obj:
            if isinstance(o, Iterable):
                self.remove_object(*o)
            else:
                self._to_remove.append(o)
        return self
        
    def update(self, dt: float) -> "ObjectCollection":
        self._handle_object_additions()
        self._handle_object_removals()
        
        if not self._frozen:
            for o in self:
                o.update(dt)
            
        return self
            
    def render(self, submit: Callable[[DrawCommand], Any]) -> "ObjectCollection":
        
        if self.rendering_enabled:
            for o in self:
                o.render(submit)
        
        return self
        
    