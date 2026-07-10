from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from robs_pge.objects.object_factory import ObjectFactory



class SubObjectFactory:
    def __init__(self, object_factory: ObjectFactory):
        self.factory: ObjectFactory = object_factory
    
    def _get_resource[T](self, resource: Optional[str | Any], style_type: type[T]) -> T:
        return self.factory.get_resource(resource, style_type)
    
    def _make_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        return self.factory.make_object(object_type, position, rotation, scale, renderer, layer, anchor, *args)
    


