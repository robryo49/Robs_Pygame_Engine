from __future__ import annotations

from typing import Iterable, TYPE_CHECKING, Any, Callable

from ..utils import TypedCollection, ObjectLikeType
from ..rendering import DrawCommand

if TYPE_CHECKING:
    from ..core import Camera
    from .layer import Layer


class ObjectCollection(TypedCollection):
    def __init__(self, objects: Iterable[ObjectLikeType] = ()):
        
        super().__init__(ObjectLikeType, objects)
        
        self._to_remove: list[ObjectLikeType] = []
        self._to_add: list[ObjectLikeType] = []
        
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
        
        if not self._frozen:
            self.foreach(lambda o: o.update())
            
        return self
            
    def render(self, submit: Callable[[DrawCommand], Any]) -> "ObjectCollection":
        
        if self.rendering_enabled:
            self.foreach(lambda o: o.render(submit))
        
        return self
        
    