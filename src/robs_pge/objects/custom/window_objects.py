"""Window layout object that manages a title, header, and replaceable content panel."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, Transform, vec2, ObjectFlags

if TYPE_CHECKING:
    from ...core import ServicesCollection


class WindowObject(LayoutObject):
    """Layout-based window with a title, optional header, and a content panel."""
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject, header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject],
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the window from its layout parts.

        :param transform: Transform applied to the window.
        :param renderer: Rectangle renderer used by the window.
        :param title: Window title text, also used to derive the id.
        :param content_panel: Layout object that holds the window content.
        :param header: Optional header layout object.
        :param title_panel: Optional title panel rectangle.
        :param title_object: Optional title text object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the window.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)

        self._id = title.lower().replace(" ", "_")
        self._title = title

        self._content = content_panel
        self._header = header
        self._title_panel = title_panel
        self._title_object = title_object

    # region PROPERTIES

    # region content
    @property
    def content(self):
        """Return the layout object used for window content."""
        return self._content
    
    @content.setter
    def content(self, obj: LayoutObject):
        """
        Replace the content panel while preserving its height constraint.

        :param obj: New layout object to use as content.
        """
        if obj is self._content:
            return

        constraint = self._content.height_constraint
        if self.has_object(self._content):
            self.replace_object(self._content, obj, ignore_callbacks=True)
        else:
            self.remove_child(self._content)
            self.add_child(obj)
            self.stack_y(obj)

        obj.set_height_constraint(constraint.min, constraint.max, constraint.fixed)
        self._content = obj
        self._content.mark_dirty()
        self.mark_dirty()
    # endregion

    @property
    def header(self) -> Optional[LayoutObject]:
        """Return the optional header layout object."""
        return self._header

    @property
    def title_panel(self) -> Optional[RectObject]:
        """Return the optional title panel rectangle."""
        return self._title_panel

    @property
    def title_object(self) -> Optional[TextObject]:
        """Return the optional title text object."""
        return self._title_object

    @property
    def title(self):
        """Return the window title text."""
        return self._title

    @property
    def id(self):
        """Return the identifier derived from the title."""
        return self._id

    @property
    def opened(self):
        """Return whether the window is visible."""
        return not self.closed

    @property
    def closed(self):
        """Return whether the window is hidden."""
        return self.has_flag(ObjectFlags.HIDDEN)

    def _update_self(self, dt: float):
        super()._update_self(dt)

    # endregion

    def open(self) -> "WindowObject":
        """
        Show the window.

        :return: This window, allowing chained calls.
        """
        self.show()
        return self

    def close(self) -> "WindowObject":
        """
        Hide the window.

        :return: This window, allowing chained calls.
        """
        self.hide()
        return self

    def add_content(self, obj: PygameObject, x: int, y: int, anchor: vec2 = Anchor.C) -> "WindowObject":
        """
        Place an object in a content cell.

        :param obj: Object to place in the content panel.
        :param x: Content column index.
        :param y: Content row index.
        :param anchor: Anchor used inside the target cell.
        :return: This window, allowing chained calls.
        """
        self.content.set_object_in_cell(obj, x, y, anchor)
        return self

    def stack_content_x(self, obj: PygameObject, row: int = 0, anchor: vec2 = Anchor.C) -> "WindowObject":
        """
        Stack an object along the content row.

        :param obj: Object to place in the content panel.
        :param row: Content row index.
        :param anchor: Anchor used inside the target cell.
        :return: This window, allowing chained calls.
        """
        self.content.stack_x(obj, row, anchor)
        return self

    def stack_content_y(self, obj: PygameObject, col: int = 0, anchor: vec2 = Anchor.C) -> "WindowObject":
        """
        Stack an object along the content column.

        :param obj: Object to place in the content panel.
        :param col: Content column index.
        :param anchor: Anchor used inside the target cell.
        :return: This window, allowing chained calls.
        """
        self.content.stack_y(obj, col, anchor)
        return self
    
    def set_content(self, obj: LayoutObject):
        """
        Replace the content panel.

        :param obj: New layout object to use as content.
        :return: This window, allowing chained calls.
        """
        self.content = obj
        return self

    def __repr__(self):
        """Return a debug string representation."""
        return f"Window('{self.id}')"
    
    
        
    