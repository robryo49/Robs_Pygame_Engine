from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Any

from .object_collection import ObjectCollection
from ..rendering import DrawCommand
from ..utils import ObjectLikeType

if TYPE_CHECKING:
    from ..core import Camera


class Layer:
    def __init__(self, name: str, layer_value: float, camera: Camera, interactable: bool = True):
        self._id = name.lower().replace(" ", "_")
        self._layer_value = layer_value
        self._camera = camera
        self._interactable = interactable
        
        self._objects = ObjectCollection()
        
        super().__init__()
    
    # region PROPERTIES
    
    @property
    def id(self):
        return self._id
    
    @property
    def layer_value(self):
        return self._layer_value
    
    @property
    def camera(self):
        return self._camera
    
    @property
    def interactable(self):
        return self._interactable
    
    @interactable.setter
    def interactable(self, value: bool):
        self._interactable = value
        
    @property
    def objects(self):
        return self._objects
    
    # endregion
    
    def freeze(self):
        self.objects.freeze()
    
    def unfreeze(self):
        self.objects.unfreeze()
        
    def toggle_frozen(self):
        self.objects.toggle_frozen()
        
        
    def enable_rendering(self):
        self.objects.enable_rendering()
        
    def disable_rendering(self):
        self.objects.disable_rendering()
        
    def toggle_rendering(self):
        self.objects.toggle_rendering()
        
    
    def add_object(self, obj: ObjectLikeType | list[ObjectLikeType]):
        self.objects.add_object(obj)
        
    def remove_object(self, obj: ObjectLikeType | list[ObjectLikeType]):
        self.objects.remove_object(obj)
    
    def render(self, submit: Callable[[DrawCommand, Camera, float], Any]) -> "Layer":
        self.objects.render(lambda c: submit(c, self._camera, self._layer_value), self._camera)
        return self
    
    def update(self, dt: float) -> "Layer":
        self.objects.update(dt)
        return self
    
    def __iter__(self):
        return self.objects.__iter__()
    
    def __repr__(self):
        return f"Layer('{self._id}', z={self._layer_value})"