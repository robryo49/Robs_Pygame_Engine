"""
Factories for creating rectangle, circle, and line shape objects.
"""

from .sub_object_factory import SubObjectFactory
from ..custom import CircleObject, LineObject, RectObject
from ...rendering import CircleRenderer, CircleStyle, LineRenderer, LineStyle, RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2


class ShapeObjectFactory(SubObjectFactory):
    """
    Create rectangle, circle, and line objects with configurable styles.
    """

    def rect(
            self, position: vec2, dims: vec2, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> RectObject:
        """
        Create a rectangle object.

        :param position: World-space position of the object.
        :param dims: Dimensions of the rectangle.
        :param style: Rectangle style or name of a registered rectangle style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created rectangle object.
        """

        style = self._get_resource(style, RectStyle)
        obj = self._create_object(RectObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor)

        return obj

    def circle(
            self, position: vec2, radius: int, style: StyleOrName[CircleStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> CircleObject:
        """
        Create a circle object.

        :param position: World-space position of the object.
        :param radius: Radius of the circle in pixels.
        :param style: Circle style or name of a registered circle style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created circle object.
        """

        style = self._get_resource(style, CircleStyle)
        obj = self._create_object(CircleObject, position, rotation, scale, CircleRenderer(radius, style, cache), layer, anchor)

        return obj

    def line(
            self, position: vec2, points: list[vec2], style: StyleOrName[LineStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LineObject:
        """
        Create a line object from a sequence of points.

        :param position: World-space position of the object.
        :param points: Points defining the line.
        :param style: Line style or name of a registered line style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created line object.
        """

        style = self._get_resource(style, LineStyle)
        obj = self._create_object(LineObject, position, rotation, scale, LineRenderer(points, style, cache), layer, anchor)

        return obj

