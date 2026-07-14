from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from ..utils import Collection

if TYPE_CHECKING:
    from ..core import Camera
    from ..objects import PygameObject


class ObjectCollection(Collection):
    def __init__(self, objects: Optional[list[PygameObject]] = None):
        super().__init__(objects)
        
        self._to_remove: list[PygameObject] = []
        self._to_add: list[PygameObject] = []
        
        self._frozen = False
        self._render = True

    # region PROPERTIES
    
    @property
    def objects(self) -> list[PygameObject]:
        return self.elements
    
    # endregion
    
    
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
        
        self._elements.extend(self._to_add)
        self._to_add.clear()
        return self
        
    def _handle_object_removals(self) -> "ObjectCollection":
        if not self._to_remove:
            return self
        
        self._elements = [obj for obj in self._elements if obj not in self._to_remove]
        self._to_remove.clear()
        return self
    
    def add(self, obj: PygameObject | list[PygameObject]) -> "ObjectCollection":
        if isinstance(obj, list):
            for o in obj:
                self.add(o)
        else:
            self._to_add.append(obj)
        return self
        
    def remove(self, obj: PygameObject | list[PygameObject]) -> "ObjectCollection":
        if isinstance(obj, list):
            for o in obj:
                self.remove(o)
        elif self.has(obj):
            self._to_remove.append(obj)
        return self
        
    def update(self, dt: float) -> "ObjectCollection":
        self._handle_object_additions()
        self._handle_object_removals()
        
        for obj in self._elements:
            obj.update(dt)
        return self
            
    def render(self, submit, camera: Camera) -> "ObjectCollection":
        for obj in self._elements:
            obj.render(submit, camera)
        return self
        
    