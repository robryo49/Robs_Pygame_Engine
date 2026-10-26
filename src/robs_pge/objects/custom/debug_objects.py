"""Debug overlay and information window objects for displaying runtime data."""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject
from .window_objects import WindowObject
from ...rendering import RectRenderer
from ...utils import Anchor, Transform, vec2

if TYPE_CHECKING:
    from ...core import ServicesCollection


class DebugOverlay(LayoutObject):
    """Layout container that can toggle the visibility of a debug overlay."""
    def __init__(self, transform: Transform, renderer: RectRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the debug overlay layout.

        :param transform: Transform applied to the overlay.
        :param renderer: Rectangle renderer used by the overlay.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the overlay.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    def toggle(self) -> LayoutObject:
        """
        Toggle overlay visibility.

        :return: This overlay, allowing chained calls.
        """
        self.visible = not self.visible
        return self
    
    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"DebugOverlay({id(self)})"
    

class DebugInfoWindow(WindowObject):
    """Window that displays live debug values built from title and value factories."""
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject,
                 header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject],
                 title_factory_method, value_factory_method,
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the debug information window.

        :param transform: Transform applied to the window.
        :param renderer: Rectangle renderer used by the window.
        :param title: Window title text.
        :param content_panel: Layout object that holds the debug lines.
        :param header: Optional header layout object.
        :param title_panel: Optional title panel rectangle.
        :param title_object: Optional title text object.
        :param title_factory_method: Factory used to create title objects for each line.
        :param value_factory_method: Factory used to create value objects for each line.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the window.
        """
        super().__init__(transform, renderer, title, content_panel, header, title_panel, title_object, services, sub_layer, anchor)
        
        self._title_factory = title_factory_method
        self._value_factory = value_factory_method
    
    def add_line(self, title: str, template: str, getter: Callable):
        """
        Add a titled live value line to the window content.

        :param title: Static title shown for the line.
        :param template: Format template used by the value object.
        :param getter: Callable that supplies the current value.
        """
        title = self._title_factory(title)
        value = self._value_factory(template, getter)
        
        self.stack_content_y(title, 0, anchor=Anchor.TL)
        self.stack_content_y(value, 1, anchor=Anchor.TL)
    
    def add_line_break(self):
        """Add a blank line to the window content."""
        title = self._title_factory(" ")
        value = self._title_factory(" ")
        
        self.stack_content_y(title, 0, anchor=Anchor.TL)
        self.stack_content_y(value, 1, anchor=Anchor.TL)