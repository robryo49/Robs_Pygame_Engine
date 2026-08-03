from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Any

from .object_collection import ObjectCollection
from ..rendering import DrawCommand

if TYPE_CHECKING:
    from ..core import Camera


class Layer(ObjectCollection):
    def __init__(self, name: str, layer_value: float, camera: Camera, interactable: bool = True):
        self._id = name.lower().replace(" ", "_")
        self._layer_value = layer_value
        self._camera = camera
        self._interactable = interactable
        
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
    
    # endregion
    
    def render(self, submit: Callable[[DrawCommand], Any]) -> "Layer":
        super().render(submit, self._camera)
        return self
    
    def update(self, dt: float) -> "Layer":
        super().update(dt)
        return self
    
    def __repr__(self):
        return f"Layer('{self._id}', z={self._layer_value})"