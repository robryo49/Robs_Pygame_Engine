from __future__ import annotations
from typing import Any, Callable, Optional, TYPE_CHECKING

from .object_factories import ShapeFactory, SpriteObjectFactory, TextObjectFactory, UIObjectFactory, WindowObjectFactory
from ..resources import ResourceManager
from ..utils import DictCollection, Transform

if TYPE_CHECKING:
    from ..objects import PygameObject


class ObjectFactory:
    def __init__(self):
        self._services = DictCollection()
        
        self.shape = ShapeFactory(self)
        self.text = TextObjectFactory(self)
        self.ui = UIObjectFactory(self)
        self.sprite = SpriteObjectFactory(self)
        self.window: WindowObjectFactory = WindowObjectFactory(self)
        
        self._constructors: dict[str, Callable[[...], PygameObject]] = {}
    
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
    
    def create_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        return object_type(Transform(position, rotation, scale), renderer, *args, self._services, layer, anchor)
    
    def register_constructor(self, name: str, constructor: Callable[[...], PygameObject]):
        self._constructors[name] = constructor
    
    def __call__(self, constructor_name: str, *args, **kwargs) -> PygameObject:
        return self._constructors[constructor_name](*args, **kwargs)
    