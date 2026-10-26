"""Concrete pygame objects backed by rectangle, circle, line, and text renderers."""

from __future__ import annotations

from typing import Any, Literal, TYPE_CHECKING

from ..object import PygameObject
from ...physics import ShapeTypes
from ...rendering import CircleRenderer, LineRenderer, RectRenderer, TextRenderer
from ...utils import Anchor, Color, Transform, vec2

if TYPE_CHECKING:
    from ...core import ServicesCollection


class RectObject(PygameObject[RectRenderer]):
    """Pygame object backed by a RectRenderer with convenient access to rectangle properties."""
    def __init__(self, transform: Transform, renderer: RectRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the rectangle object.

        :param transform: Transform applied to the object.
        :param renderer: Rectangle renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> RectRenderer:
        """Return the rectangle renderer."""
        return self._renderer
    
    
    @property
    def dims(self):
        """Return the rectangle dimensions."""
        return self.renderer.dims
    
    @dims.setter
    def dims(self, value: vec2):
        """
        Set the rectangle dimensions.

        :param value: The new rectangle dimensions.
        """
        self.renderer.dims = value
    
    
    @property
    def width(self):
        """Return the rectangle width."""
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        """
        Set the rectangle width.

        :param value: The new rectangle width.
        """
        self.renderer.width = value
    
    
    @property
    def height(self):
        """Return the rectangle height."""
        return self.renderer.height
    
    @height.setter
    def height(self, value: int):
        """
        Set the rectangle height.

        :param value: The new rectangle height.
        """
        self.renderer.height = value
    
    
    @property
    def bg_color(self):
        """Return the rectangle background color."""
        return self.renderer.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        """
        Set the rectangle background color.

        :param value: The new rectangle background color.
        """
        self.renderer.bg_color = value
    
    
    @property
    def bd(self):
        """Return the rectangle border width."""
        return self.renderer.bd
    
    @bd.setter
    def bd(self, value: int):
        """
        Set the rectangle border width.

        :param value: The new rectangle border width.
        """
        self.renderer.bd = value
    
    
    @property
    def bd_color(self):
        """Return the rectangle border color."""
        return self.renderer.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        """
        Set the rectangle border color.

        :param value: The new rectangle border color.
        """
        self.renderer.bd_color = value
    
    
    @property
    def bd_radius(self):
        """Return the rectangle border radius."""
        return self.renderer.bd_radius
    
    @bd_radius.setter
    def bd_radius(self, value: int):
        """
        Set the rectangle border radius.

        :param value: The new rectangle border radius.
        """
        self.renderer.bd_radius = value
    
    # endregion


class CircleObject(PygameObject[CircleRenderer]):
    """Pygame object backed by a CircleRenderer with convenient access to circle properties."""
    def __init__(self, transform: Transform, renderer: CircleRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the circle object.

        :param transform: Transform applied to the object.
        :param renderer: Circle renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> CircleRenderer:
        """Return the circle renderer."""
        return self._renderer
    
    
    @property
    def dims(self):
        """Return the circle dimensions."""
        return self.renderer.dims
    
    
    @property
    def width(self):
        """Return the circle width."""
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        """
        Set the circle width.

        :param value: The new circle width.
        """
        self.renderer.width = value
    
    
    @property
    def height(self):
        """Return the circle height."""
        return self.renderer.height
    
    @height.setter
    def height(self, value):
        """
        Set the circle height.

        :param value: The new circle height.
        """
        self.renderer.height = value
    
    
    @property
    def diameter(self):
        """Return the circle diameter."""
        return self.renderer.diameter
    
    @diameter.setter
    def diameter(self, value: int):
        """
        Set the circle diameter.

        :param value: The new circle diameter.
        """
        self.renderer.diameter = value
    
    
    @property
    def radius(self):
        """Return the circle radius."""
        return self.renderer.radius
    
    @radius.setter
    def radius(self, value: int):
        """
        Set the circle radius.

        :param value: The new circle radius.
        """
        self.renderer.radius = value
    
    
    @property
    def bg_color(self):
        """Return the circle background color."""
        return self.renderer.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        """
        Set the circle background color.

        :param value: The new circle background color.
        """
        self.renderer.bg_color = value
    
    
    @property
    def bd_color(self):
        """Return the circle border color."""
        return self.renderer.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        """
        Set the circle border color.

        :param value: The new circle border color.
        """
        self.renderer.bd_color = value
    
    
    @property
    def bd(self):
        """Return the circle border width."""
        return self.renderer.bd
    
    @bd.setter
    def bd(self, value: int):
        """
        Set the circle border width.

        :param value: The new circle border width.
        """
        self.renderer.bd = value
    
    # endregion
    
    @staticmethod
    def get_default_shape_type() -> Literal["box", "circle"]:
        """
        Return the circle shape type used by the physics system.

        :return: The circle shape type constant.
        """
        return ShapeTypes.CIRCLE


class LineObject(PygameObject[LineRenderer]):
    """Pygame object backed by a LineRenderer that draws a connected point path."""
    def __init__(self, transform: Transform, renderer: LineRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the line object.

        :param transform: Transform applied to the object.
        :param renderer: Line renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> LineRenderer:
        """Return the line renderer."""
        return self._renderer
    
    
    @property
    def points(self):
        """Return the line points."""
        return self.renderer.points
    
    @points.setter
    def points(self, value: list[vec2]):
        """
        Set the line points.

        :param value: The new line points.
        """
        self.renderer.points = value
    
    
    @property
    def width(self):
        """Return the line width."""
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        """
        Set the line width.

        :param value: The new line width.
        """
        self.renderer.width = value
    
    
    @property
    def color(self):
        """Return the line color."""
        return self.renderer.color
    
    @color.setter
    def color(self, value: Color):
        """
        Set the line color.

        :param value: The new line color.
        """
        self.renderer.color = value
    
    # endregion


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

