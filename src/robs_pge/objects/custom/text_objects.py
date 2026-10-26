"""Concrete pygame objects text renderers."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ..object import PygameObject
from ...rendering import TextRenderer
from ...utils import Anchor, Transform, vec2

if TYPE_CHECKING:
    from ...core import ServicesCollection


class TextObject(PygameObject[TextRenderer]):
    """Pygame object backed by a TextRenderer with convenient text and font access."""
    def __init__(self, transform: Transform, renderer: TextRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the text object.

        :param transform: Transform applied to the object.
        :param renderer: Text renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)

    # region PROPERTIES

    @property
    def renderer(self) -> TextRenderer:
        """Return the text renderer."""
        return self._renderer

    @property
    def text(self) -> str:
        """Return the rendered text."""
        return self.renderer.text

    @text.setter
    def text(self, value: Any):
        """
        Set the rendered text, converting the value to a string.

        :param value: The new value.
        """
        self.renderer.text = str(value)

    @property
    def font(self):
        """Return the text font."""
        return self.renderer.font

    # region color
    @property
    def color(self):
        """Return the text font color."""
        return self.font.color

    @color.setter
    def color(self, value):
        """
        Set the text font color.

        :param value: The new text font color.
        """
        self.font.color = value
    # endregion

    # endregion
