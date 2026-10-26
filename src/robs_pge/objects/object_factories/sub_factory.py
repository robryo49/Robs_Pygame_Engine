"""
Base sub-factory that delegates resource lookup and object creation to the main factory.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from ..object_factory import ObjectFactory



class SubObjectFactory:
    """
    Provide shared helpers for sub-factories that create specialized object types.
    """
    def __init__(self, object_factory: ObjectFactory) -> None:
        """
        Initialize the sub-factory with its parent object factory.

        :param object_factory: Main object factory used for resource lookup and object creation.
        """
        self.factory: ObjectFactory = object_factory
    
    def _get_resource[T](self, resource: Optional[str | Any], style_type: type[T]) -> T:
        return self.factory.get_resource(resource, style_type)
    
    def _create_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        return self.factory.create_object(object_type, position, rotation, scale, renderer, layer, anchor, *args)
    


