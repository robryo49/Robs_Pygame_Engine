"""Factories for constructing scene objects and resolving resources."""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .object_factories import ShapeFactory, SpriteObjectFactory, TextObjectFactory, UIObjectFactory, WindowObjectFactory
from ..rendering import Style
from ..resources import ResourceManager
from ..utils import Transform

if TYPE_CHECKING:
    from ..objects import PygameObject
    from ..core import ServicesCollection


class ObjectFactory:
    """Construct scene objects and resolve shared resources and styles."""
    def __init__(self, services: ServicesCollection) -> None:
        """
        Initialize object factories for each supported object category.

        :param services: Services collection used by factory constructors.
        """
        self._services = services
        
        self.shape = ShapeFactory(self)
        self.text = TextObjectFactory(self)
        self.ui = UIObjectFactory(self)
        self.sprite = SpriteObjectFactory(self)
        self.window: WindowObjectFactory = WindowObjectFactory(self)
        
        self._constructors: dict[str, Callable[[...], PygameObject]] = {}
    
    # region PROPERTIES
    
    @property
    def services(self) -> ServicesCollection:
        """Return the services collection used by factory constructors."""
        return self._services
    
    @services.setter
    def services(self, value: ServicesCollection):
        """
        Set the services collection used by factory constructors.

        :param value: The new value.
        """
        self._services = value
        
    @property
    def constructors(self):
        """Return the registered named object constructors."""
        return self._constructors
    
    # endregion
    
    def get_resource[T](self, resource: Optional[str | Any], resource_type: type[T]) -> T:
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
        
    
    def create_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
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
    
    def register_constructor(self, name: str, constructor: Callable[[...], PygameObject]):
        """
        Register a named object constructor.

        :param name: Constructor name.
        :param constructor: Callable that creates the object.
        """
        self._constructors[name] = constructor
    
    def __call__(self, constructor_name: str, *args, **kwargs) -> PygameObject:
        """
        Create an object using a registered constructor name.

        :param constructor_name: Registered constructor name.
        :param args: Positional arguments passed to the constructor.
        :param kwargs: Keyword arguments passed to the constructor.
        :return: The created object.
        :raises KeyError: When no constructor with the given name is registered.
        """
        try:
            return self._constructors[constructor_name](*args, **kwargs)
        except KeyError:
            raise KeyError(f"Object constructor with name '{constructor_name}' not found, only have : {list(self._constructors.keys())}")
        