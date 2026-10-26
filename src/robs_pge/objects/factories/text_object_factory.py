"""
Factories for creating labels, dynamic labels, and text boxes.
"""

from typing import Any, Callable, Optional

from .sub_object_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Font, StyleOrName, vec2, split_text


class TextObjectFactory(SubObjectFactory):
    """
    Create text labels, dynamic labels, and wrapped text boxes.
    """
    def label(
            self, position: vec2, text: str, font: StyleOrName[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        """
        Create a text label from a string and font.

        :param position: World-space position of the object.
        :param text: Text displayed by the label.
        :param font: Font or registered font name used to render the text.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created text object.
        """

        font = self._get_resource(font, Font)
        obj = self._create_object(TextObject, position, rotation, scale, TextRenderer(text, font, cache), layer, anchor)

        return obj

    def dynamic_label(
            self, position: vec2, template: str, getter: Callable[[], Any | tuple[Any, ...]], font: StyleOrName[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        """
        Create a label whose text is recomputed from a getter and format template.

        :param position: World-space position of the object.
        :param template: Format string applied to the getter result.
        :param getter: Callable returning the value or values used to render the text.
        :param font: Font or registered font name used to render the text.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created dynamic text object.
        """

        font = self._get_resource(font, Font)
        obj = self.label(position, "", font, rotation, scale, layer, anchor, cache)
        obj.make_attribute_dynamic("text", getter, template)

        return obj

    def text_box(
            self, position: vec2, text: str, width: Optional[int] = None, height: Optional[int] = None,
            justification: vec2 = Anchor.TL, margin: int = 0,
            font: StyleOrName[Font] = None, bg_style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextBoxObject:
        """
        Create a text box that wraps text and lays out each line vertically.

        :param position: World-space position of the object.
        :param text: Text to wrap and display.
        :param width: Fixed width of the text box.
        :param height: Fixed height of the text box.
        :param justification: Anchor used to justify the wrapped text.
        :param margin: Padding between the text box border and its content.
        :param font: Font or registered font name used to render the text.
        :param bg_style: Rectangle style or registered style name for the background.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created text box object.
        """

        font = self._get_resource(font, Font)
        bg_style = self._get_resource(bg_style, RectStyle)

        max_content_width = (width - 2 * margin) if width is not None else None

        lines = split_text(text, font, max_content_width)

        text_objects = [
            self.label(vec2(), line, font, rotation=0.0, scale=1.0, layer=layer, anchor=Anchor.C, cache=cache)
            for line in lines
        ]

        obj: TextBoxObject = self._factory.layout._create_layout(
            TextBoxObject, position, width, height,
            TextBoxObject.GRID_MODE, TextBoxObject.PRESERVE_MODE, TextBoxObject.PRESERVE_MODE,
            justification, False, bg_style, rotation, scale, layer, anchor, cache,
            text, font, text_objects, self.label
        )

        obj.set_cell_anchor(justification)

        for text_obj in text_objects:
            obj.stack_y(text_obj, x=0)

        obj.outer_padding = margin

        return obj
