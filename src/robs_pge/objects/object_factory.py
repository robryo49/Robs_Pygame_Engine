from typing import Any, Optional

from .object_factories import ShapeFactory, SpriteObjectFactory, TextObjectFactory, UIObjectFactory
from robs_pge.resources import ResourceManager
from robs_pge.utils import DictCollection, Transform


class ObjectFactory:
    def __init__(self):
        self._services = DictCollection()
        
        self.shape = ShapeFactory(self)
        self.text = TextObjectFactory(self)
        self.ui = UIObjectFactory(self)
        self.sprite = SpriteObjectFactory(self)
        
    
    # region PROPERTIES
    
    @property
    def services(self):
        return self._services
    
    @services.setter
    def services(self, value: DictCollection):
        self._services = value
    
    # endregion
    
    def get_resource[T](self, resource: Optional[str | Any], style_type: type[T]) -> T:
        if isinstance(resource, str):
            return self._services.get(ResourceManager).get(style_type, resource)
        elif resource is not None:
            return resource
        else:
            return style_type()
    
    def make_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        return object_type(Transform(position, rotation, scale), renderer, *args, self._services, layer, anchor)
    