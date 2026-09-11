from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .object_factories import ShapeFactory, SpriteObjectFactory, TextObjectFactory, UIObjectFactory, WindowObjectFactory
from ..rendering import Style
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
        
    @property
    def constructors(self):
        return self._constructors
    
    # endregion
    
    def get_resource[T](self, resource: Optional[str | Any], resource_type: type[T]) -> T:
        manager: ResourceManager = self._services[ResourceManager]
        is_style = isinstance(resource_type, type) and issubclass(resource_type, Style)

        if is_style:
            return manager.get_style_or_default(resource_type, resource)
        else:
            return manager.get_or_default(resource_type, resource)
        
    
    def create_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        return object_type(Transform(position, rotation, scale), renderer, *args, self._services, layer, anchor)
    
    def register_constructor(self, name: str, constructor: Callable[[...], PygameObject]):
        self._constructors[name] = constructor
    
    def __call__(self, constructor_name: str, *args, **kwargs) -> PygameObject:
        try:
            return self._constructors[constructor_name](*args, **kwargs)
        except KeyError:
            raise KeyError(f"Object constructor with name '{constructor_name}' not found, only have : {list(self._constructors.keys())}")
        