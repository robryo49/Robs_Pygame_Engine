from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from .layer import Layer
from ..rendering import DrawCommand

if TYPE_CHECKING:
    from ..core import Camera
    from ..core.states.services_collection import ServicesCollection


class LayerManager:
    def __init__(self, services: ServicesCollection):
        self._services = services
        
        self._layers: dict[str, Layer] = {}
        self._sorted_layers: list[Layer] = []

        self._update_blacklist: set[Layer] = set()
        self._render_blacklist: set[Layer] = set()
    
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
    
    def remove_layer(self, layer: Layer | str) -> "LayerManager":
        if isinstance(layer, Layer):
            layer_id = layer.id
        else:
            layer_id = layer.lower().replace(" ", "_")

        if layer_id in self._layers:
            del self._layers[layer_id]
            self._rebuild_sorted()
        return self
    
    def get_layer(self, layer: Layer | str) -> Layer:
        if isinstance(layer, Layer):
            layer_id = layer.id
        else:
            layer_id = layer.lower().replace(" ", "_")

        layer = self._layers.get(layer_id)
        if layer is None:
            raise KeyError(f"Layer '{layer_id}' not found. Available: {list(self._layers.keys())}")
        return layer
    
    def has_layer(self, layer: Layer | str) -> bool:
        if isinstance(layer, Layer):
            return layer in self.layers.values()
        return layer.lower().replace(" ", "_") in self._layers
    
    def add_object(self, layer: Layer | str, obj) -> "LayerManager":
        self.get_layer(layer).add_object(obj)
        return self
    
    def remove_object(self, layer: Layer | str, obj) -> "LayerManager":
        self.get_layer(layer).remove_object(obj)
        return self
    
    def update(self, dt: float) -> "LayerManager":
        for layer in self._sorted_layers:
            if layer not in self._update_blacklist:
                layer.update(dt)
        return self
    
    def render(self, submit: Callable[[DrawCommand], Any]) -> "LayerManager":
        for layer in self._sorted_layers:
            if layer not in self._render_blacklist:
                layer.render(submit)
        return self
    
    def interactable_layers_reversed(self) -> list[Layer]:
        """Interactable layers in descending z-order for hit testing (topmost wins)."""
        return [l for l in reversed(self._sorted_layers) if l.interactable]

    def add_layer_to_update_blacklist(self, layer: Layer | str):
        if isinstance(layer, str):
            layer = self.get_layer(layer)
        self._update_blacklist.add(layer)

    def remove_layer_from_update_blacklist(self, layer: Layer | str):
        if isinstance(layer, str):
            layer = self.get_layer(layer)
        try:
            self._update_blacklist.remove(layer)
        except KeyError:
            pass

    def add_layer_to_render_blacklist(self, layer: Layer | str):
        if isinstance(layer, str):
            layer = self.get_layer(layer)
        self._render_blacklist.add(layer)

    def remove_layer_from_render_blacklist(self, layer: Layer | str):
        if isinstance(layer, str):
            layer = self.get_layer(layer)
        try:
            self._render_blacklist.remove(layer)
        except KeyError:
            pass

    def __repr__(self):
        return f"LayerManager({[l.id for l in self._sorted_layers]})"