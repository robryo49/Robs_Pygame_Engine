from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from .layer import Layer
from ..rendering import DrawCommand
from ..utils import DictCollection

if TYPE_CHECKING:
    from ..core import Camera


class LayerManager:
    def __init__(self, services: DictCollection):
        self._services = services
        
        self._layers: dict[str, Layer] = {}
        self._sorted_layers: list[Layer] = []  # maintained in ascending z-order
    
    # region PROPERTIES
    
    @property
    def layers(self) -> dict[str, Layer]:
        return self._layers
    
    @property
    def sorted_layers(self) -> list[Layer]:
        """Layers in ascending z-order (lowest drawn first)."""
        return self._sorted_layers
    
    # endregion
    
    def _rebuild_sorted(self):
        self._sorted_layers = sorted(self._layers.values(), key=lambda l: l.layer_value)
    
    def create_layer(self, name: str, layer_value: float, camera: Camera, interactable: bool = True) -> Layer:
        layer_id = name.lower().replace(" ", "_")
        if layer_id in self._layers:
            raise ValueError(f"Layer '{layer_id}' already exists")
        layer = Layer(name, layer_value, camera, self._services, interactable)
        self._layers[layer_id] = layer
        self._rebuild_sorted()
        return layer
    
    def remove_layer(self, name: str) -> "LayerManager":
        layer_id = name.lower().replace(" ", "_")
        if layer_id in self._layers:
            del self._layers[layer_id]
            self._rebuild_sorted()
        return self
    
    def get_layer(self, name: str) -> Layer:
        layer_id = name.lower().replace(" ", "_")
        layer = self._layers.get(layer_id)
        if layer is None:
            raise KeyError(f"Layer '{layer_id}' not found. Available: {list(self._layers.keys())}")
        return layer
    
    def has_layer(self, name: str) -> bool:
        return name.lower().replace(" ", "_") in self._layers
    
    def add_object(self, layer_name: str, obj) -> "LayerManager":
        self.get_layer(layer_name).add_object(obj)
        return self
    
    def update(self, dt: float) -> "LayerManager":
        for layer in self._sorted_layers:
            layer.update(dt)
        return self
    
    def render(self, submit: Callable[[DrawCommand], Any]) -> "LayerManager":
        for layer in self._sorted_layers:
            layer.render(submit)
        return self
    
    def interactable_layers_reversed(self) -> list[Layer]:
        """Interactable layers in descending z-order for hit testing (topmost wins)."""
        return [l for l in reversed(self._sorted_layers) if l.interactable]
    
    def __repr__(self):
        return f"LayerManager({[l.id for l in self._sorted_layers]})"