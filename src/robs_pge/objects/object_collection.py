from __future__ import annotations

from typing import Iterable, TYPE_CHECKING, Any, Callable

from ..utils import TypedCollection, ObjectLikeType
from ..rendering import DrawCommand

if TYPE_CHECKING:
    from ..core import Camera


class ObjectCollection(TypedCollection):
    def __init__(self, objects: Iterable[ObjectLikeType] = ()):
        
        super().__init__(ObjectLikeType, objects)
        
        self._to_remove: list[ObjectLikeType] = []
        self._to_add: list[ObjectLikeType] = []
        
        self._frozen = False
        self._render = True
    
    
    def toggle_render(self) -> "ObjectCollection":
        self._render = not self._render
        return self
    
    def enable_render(self) -> "ObjectCollection":
        self._render = True
        return self
    
    def disable_render(self) -> "ObjectCollection":
        self._render = False
        return self
    
    
    def toggle_frozen(self) -> "ObjectCollection":
        self._frozen = not self._frozen
        return self
    
    def enable_frozen(self) -> "ObjectCollection":
        self._frozen = True
        return self
    
    def disable_frozen(self) -> "ObjectCollection":
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
    
    def add_object(self, obj: ObjectLikeType | list[ObjectLikeType]) -> "ObjectCollection":
        if isinstance(obj, list):
            for o in obj:
                self.add(o)
        else:
            self._to_add.append(obj)
        return self
        
    def remove_object(self, obj: ObjectLikeType | list[ObjectLikeType]) -> "ObjectCollection":
        if isinstance(obj, list):
            for o in obj:
                self.remove_object(o)
                
        elif self.has(obj):
            self._to_remove.append(obj)
        return self
        
    def update(self, dt: float) -> "ObjectCollection":
        self._handle_object_additions()
        self._handle_object_removals()
        
        self.foreach(lambda o: o.update())
        return self
            
    def render(self, submit: Callable[[DrawCommand], Any], camera: Camera) -> "ObjectCollection":
        self.foreach(lambda o: o.render(submit, camera))
        return self
        
    