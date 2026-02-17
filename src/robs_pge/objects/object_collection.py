from typing import Any, Optional

from ..core.camera import Camera
from ..utils import Collection


class ObjectCollection(Collection):
    def __init__(self, objects: list[Any] = None):
        super().__init__(objects)
        
        self._to_remove: list = []
        self._to_add: list = []

    # region PROPERTIES
    
    @property
    def objects(self):
        return self.elements
    
    # endregion
    
    def _handle_object_additions(self):
        if not self._to_add:
            return
        
        self._elements.extend(self._to_add)
        self._to_add.clear()
        
    def _handle_object_removals(self):
        if not self._to_remove:
            return
        
        self._elements = [obj for obj in self._elements if obj not in self._to_remove]
        self._to_remove.clear()
        
    
    def add(self, obj: Any | list[Any]):
        if isinstance(obj, list):
            for o in obj:
                self.add(o)
        else:
            self._to_add.append(obj)
        
    def remove(self, obj: Any | list[Any]):
        if isinstance(obj, list):
            for o in obj:
                self.remove(o)
        elif self.has(obj):
            self._to_remove.append(obj)
        
    def update(self, dt: float):
        self._handle_object_additions()
        self._handle_object_removals()
        
        for obj in self._elements:
            obj.update(dt)
            
    def render(self, submit, camera: Optional[Camera] = None):
        for obj in self._elements:
            obj.render(submit, camera) if camera else obj.render(submit)
        
    