"""Management of scene layers, their ordering, and update/render blacklists."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, Callable, Iterable

from .layer import Layer
from ..rendering import DrawCommand

if TYPE_CHECKING:
    from .object import PygameObject
    from ..core import Camera
    from ..core.states.services_collection import ServicesCollection


class LayerManager:
    """Owns layers, their sort order, and update/render blacklists."""

    def __init__(self, services: ServicesCollection) -> None:
        """
        Initialize a layer manager backed by a services collection.

        :param services: Services collection shared with created layers.
        """
        self._services = services

        self._layers: dict[str, Layer] = {}
        self._sorted_layers: list[Layer] = []

        self._update_blacklist: set[Layer] = set()
        self._render_blacklist: set[Layer] = set()

    # region PROPERTIES

    @property
    def layers(self) -> dict[str, Layer]:
        """Return the layers keyed by their normalized identifier."""
        return self._layers

    @property
    def sorted_layers(self) -> list[Layer]:
        """Return the layers in ascending z-order (lowest drawn first)."""
        return self._sorted_layers

    @property
    def update_blacklist(self) -> set[Layer]:
        """Return the layers skipped during updates."""
        return self._update_blacklist

    @property
    def render_blacklist(self) -> set[Layer]:
        """Return the layers skipped during rendering."""
        return self._render_blacklist

    # endregion

    def _rebuild_sorted(self) -> None:
        """Rebuild the cached list of layers sorted by z-order."""
        self._sorted_layers = sorted(self._layers.values(), key=lambda layer: layer.layer_value)

    def create_layer(
        self,
        name: str,
        layer_value: float,
        camera: Camera,
        interactable: bool = True,
    ) -> Layer:
        """
        Create, register, and return a layer.

        :param name: Human-readable layer name.
        :param layer_value: Z-order value used to sort layers.
        :param camera: Camera used to view the layer.
        :param interactable: Whether input interaction is enabled for the layer.
        :return: The created layer.
        :raises ValueError: When a layer with the derived identifier already exists.
        """
        layer_id = name.lower().replace(" ", "_")
        if layer_id in self._layers:
            raise ValueError(f"Layer '{layer_id}' already exists")

        layer = Layer(name, layer_value, camera, self._services, interactable)
        self._layers[layer_id] = layer
        self._rebuild_sorted()
        return layer

    def remove_layer(self, layer: Layer | str) -> LayerManager:
        """
        Remove a layer and its blacklist entries.

        :param layer: Layer instance or identifier to remove.
        :return: This layer manager.
        """
        layer_id = layer.id if isinstance(layer, Layer) else layer.lower().replace(" ", "_")
        removed = self._layers.pop(layer_id, None)

        if removed is not None:
            self._update_blacklist.discard(removed)
            self._render_blacklist.discard(removed)
            self._rebuild_sorted()

        return self

    def get_layer(self, layer: Layer | str) -> Layer:
        """
        Return a layer by instance or identifier.

        :param layer: Layer instance or identifier to look up.
        :return: The matching layer.
        :raises KeyError: When no layer with the identifier is registered.
        """
        layer_id = layer.id if isinstance(layer, Layer) else layer.lower().replace(" ", "_")
        resolved = self._layers.get(layer_id)

        if resolved is None:
            raise KeyError(f"Layer '{layer_id}' not found. Available: {list(self._layers.keys())}")

        return resolved

    def has_layer(self, layer: Layer | str) -> bool:
        """
        Return whether a layer is registered.

        :param layer: Layer instance or identifier to check.
        :return: ``True`` when the layer is registered.
        """
        if isinstance(layer, Layer):
            return self._layers.get(layer.id) is layer
        return layer.lower().replace(" ", "_") in self._layers

    def add_object(self, layer: Layer | str, obj: PygameObject | Iterable[PygameObject]) -> LayerManager:
        """
        Add an object or iterable of objects to a layer.

        :param layer: Layer instance or identifier.
        :param obj: Object or iterable of objects to add.
        :return: This layer manager.
        """
        self.get_layer(layer).add_object(obj)
        return self

    def remove_object(self, layer: Layer | str, obj: PygameObject | Iterable[PygameObject]) -> LayerManager:
        """
        Remove an object or iterable of objects from a layer.

        :param layer: Layer instance or identifier.
        :param obj: Object or iterable of objects to remove.
        :return: This layer manager.
        """
        self.get_layer(layer).remove_object(obj)
        return self

    def update(self, dt: float) -> LayerManager:
        """
        Update every layer that is not blacklisted.

        :param dt: Elapsed time in seconds since the previous update.
        :return: This layer manager.
        """
        for layer in self._sorted_layers:
            if layer not in self._update_blacklist:
                layer.update(dt)
        return self

    def render(self, submit: Callable[[DrawCommand], Any]) -> LayerManager:
        """
        Render every layer that is not blacklisted.

        :param submit: Callback that accepts draw commands.
        :return: This layer manager.
        """
        for layer in self._sorted_layers:
            if layer not in self._render_blacklist:
                layer.render(submit)
        return self

    def interactable_layers_reversed(self) -> list[Layer]:
        """
        Return interactable layers in descending z-order for hit testing.

        :return: Interactable layers from topmost to bottommost.
        """
        return [layer for layer in reversed(self._sorted_layers) if layer.interactable]

    def add_layer_to_update_blacklist(self, layer: Layer | str) -> LayerManager:
        """
        Skip a layer during updates.

        :param layer: Layer instance or identifier.
        :return: This layer manager.
        """
        self._update_blacklist.add(self.get_layer(layer))
        return self

    def remove_layer_from_update_blacklist(self, layer: Layer | str) -> LayerManager:
        """
        Stop skipping a layer during updates.

        :param layer: Layer instance or identifier.
        :return: This layer manager.
        """
        self._update_blacklist.discard(self.get_layer(layer))
        return self

    def add_layer_to_render_blacklist(self, layer: Layer | str) -> LayerManager:
        """
        Skip a layer during rendering.

        :param layer: Layer instance or identifier.
        :return: This layer manager.
        """
        self._render_blacklist.add(self.get_layer(layer))
        return self

    def remove_layer_from_render_blacklist(self, layer: Layer | str) -> LayerManager:
        """
        Stop skipping a layer during rendering.

        :param layer: Layer instance or identifier.
        :return: This layer manager.
        """
        self._render_blacklist.discard(self.get_layer(layer))
        return self

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"LayerManager({[layer.id for layer in self._sorted_layers]})"
