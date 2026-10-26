"""
Base sub-factory that delegates resource lookup and object creation to the main factory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any

from ...rendering import Style
from ...resources import ResourceManager
from ...utils import Transform

if TYPE_CHECKING:
    from .object_factory import ObjectFactory
    from ...core import ServicesCollection


class SubObjectFactory:
    """
    Provide shared helpers for sub-factories that create specialized object types.
    """
    def __init__(self, factory: ObjectFactory) -> None:
        """
        Initialize the sub-factory with its parent object factory.

        :param factory: parent object factory.
        """

        self._factory: ObjectFactory = factory
        self._services: ServicesCollection = factory.services


    def _get_resource[T](self, resource: Optional[str | Any], resource_type: type[T]) -> T:
        """
        Resolve a resource or style by name, falling back to the type's default.

        :param resource: Resource name, resource instance, or ``None``.
        :param resource_type: Expected resource type.
        :return: The resolved resource or style.
        """
        manager: ResourceManager = self._services.get_resource_manager()
        is_style = isinstance(resource_type, type) and issubclass(resource_type, Style)

        if is_style:
            return manager.get_style_or_default(resource_type, resource)
        else:
            return manager.get_or_default(resource_type, resource)

    def _create_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        """
        Create an object with a transform and injected services.

        :param object_type: Object class to instantiate.
        :param position: Initial local position.
        :param rotation: Initial rotation in degrees.
        :param scale: Initial uniform scale.
        :param renderer: Renderer for the object.
        :param layer: Layer for the object.
        :param anchor: Anchor used to position the renderer.
        :param args: Additional positional arguments passed to the object.
        :return: The created object.
        """
        return object_type(Transform(position, rotation, scale), renderer, *args, self._services, layer, anchor)



