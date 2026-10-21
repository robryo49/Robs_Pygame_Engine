from __future__ import annotations

from typing import Any, Callable, Iterable, TYPE_CHECKING

from ..rendering import DrawCommand

if TYPE_CHECKING:
    from ..objects import PygameObject
    

class ObjectCollection:
    def __init__(self, objects: Iterable[PygameObject] = ()):
        self._objects: list[PygameObject] = []
        
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
    
    @property
    def size(self):
        return len(self._objects)
    
    @property
    def full_size(self):
        return self.size + sum(o.children.full_size for o in self._objects)
    
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
        
        self._objects.extend(self._to_add)
        self._to_add.clear()
        return self
        
    def _handle_object_removals(self) -> "ObjectCollection":
        if not self._to_remove:
            return self
        
        for o in self._to_remove:
            self._objects.remove(o)
            
        self._to_remove.clear()
        return self
    
    def add(self, item: PygameObject) -> PygameObject:
        if item in self._to_remove:
            self._to_remove.remove(item)
        if not self.has(item):
            self._to_add.append(item)
        return item
    
    def add_object(self, *obj: PygameObject) -> "ObjectCollection":
        for o in obj:
            self._to_add.append(o)
        return self
    
    def remove(self, item: PygameObject) -> PygameObject:
        self._to_remove.append(item)
        return item
        
    def remove_object(self, *obj: PygameObject) -> "ObjectCollection":
        for o in obj:
            self._to_remove.append(o)
        return self
        
    def update(self, dt: float) -> "ObjectCollection":
        self._handle_object_additions()
        self._handle_object_removals()
        
        if not self._frozen:
            for o in self._objects:
                o.update(dt)
            
        return self
        
    def render(self, submit: Callable[[DrawCommand], Any]) -> "ObjectCollection":
        
        if self.rendering_enabled:
            for o in self._objects:
                o.render(submit)
        
        return self

    def has(self, item: PygameObject) -> bool:
        return (item in self._objects or item in self._to_add) and item not in self._to_remove

    def __contains__(self, item: object) -> bool:
        return (self._objects.__contains__(item) or item in self._to_add) and item not in self._to_remove

    def __iter__(self):
        return iter(self._objects)
        
    