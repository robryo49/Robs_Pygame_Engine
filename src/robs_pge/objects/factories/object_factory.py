"""Factories for constructing scene objects and resolving resources."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from .shape_object_factory import ShapeObjectFactory
from .sprite_object_factory import SpriteObjectFactory
from .text_object_factory import TextObjectFactory
from .layout_object_factory import LayoutObjectFactory
from .ui_object_factory import UIObjectFactory
from .window_object_factory import WindowObjectFactory
from .debug_object_factory import DebugObjectFactory

if TYPE_CHECKING:
    from ...objects import PygameObject
    from ...core import ServicesCollection


class ObjectFactory:
    """Construct scene objects and resolve shared resources and styles."""
    def __init__(self, services: ServicesCollection) -> None:
        """
        Initialize object factories for each supported object category.

        :param services: Services collection used by factory constructors.
        """
        self._services = services
        self._constructors: dict[str, Callable[[...], PygameObject]] = {}

        self._shape: ShapeObjectFactory = self._create_shape_object_factory(self)
        self._sprite: SpriteObjectFactory = self._create_sprite_object_factory(self)
        self._text: TextObjectFactory = self._create_text_object_factory(self)
        self._layout: LayoutObjectFactory = self._create_layout_object_factory(self)
        self._ui: UIObjectFactory = self._create_ui_object_factory(self)
        self._window: WindowObjectFactory = self._create_window_object_factory(self)
        self._debug: DebugObjectFactory = self._create_debug_object_factory(self)


    # region PROPERTIES

    @property
    def services(self) -> ServicesCollection:
        """Return the services collection used by factory constructors."""
        return self._services

    @property
    def constructors(self):
        """Return the registered named object constructors."""
        return self._constructors

    @property
    def shape(self) -> ShapeObjectFactory:
        return self._shape

    @property
    def sprite(self) -> SpriteObjectFactory:
        return self._sprite

    @property
    def text(self) -> TextObjectFactory:
        return self._text

    @property
    def layout(self) -> LayoutObjectFactory:
        return self._layout

    @property
    def ui(self) -> UIObjectFactory:
        return self._ui

    @property
    def window(self) -> WindowObjectFactory:
        return self._window

    @property
    def debug(self) -> DebugObjectFactory:
        return self._debug

    # endregion

    # region SUB FACTORIES CREATION METHODS

    @staticmethod
    def _create_shape_object_factory(services) -> ShapeObjectFactory:
        return ShapeObjectFactory(services)

    @staticmethod
    def _create_sprite_object_factory(services) -> SpriteObjectFactory:
        return SpriteObjectFactory(services)

    @staticmethod
    def _create_text_object_factory(services) -> TextObjectFactory:
        return TextObjectFactory(services)

    @staticmethod
    def _create_layout_object_factory(services) -> LayoutObjectFactory:
        return LayoutObjectFactory(services)

    @staticmethod
    def _create_ui_object_factory(services) -> UIObjectFactory:
        return UIObjectFactory(services)

    @staticmethod
    def _create_window_object_factory(services) -> WindowObjectFactory:
        return WindowObjectFactory(services)

    @staticmethod
    def _create_debug_object_factory(services) -> DebugObjectFactory:
        return DebugObjectFactory(services)

    # endregion

    def register_constructor(self, name: str, constructor: Callable[[...], PygameObject]):
        """
        Register a named object constructor.

        :param name: Constructor name.
        :param constructor: Callable that creates the object.
        """
        self._constructors[name] = constructor

    def create(self, constructor_name: str, *args, **kwargs) -> PygameObject:
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
