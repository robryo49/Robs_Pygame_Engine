from typing import Any, Callable, Optional

from .sub_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Font, StyleOrName, vec2, split_text


class TextObjectFactory(SubObjectFactory):
    def label(
            self, position: vec2, text: str, font: StyleOrName[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        
        font = self._get_resource(font, Font)
        obj = self._create_object(TextObject, position, rotation, scale, TextRenderer(text, font, cache), layer, anchor)
        
        return obj
    
    def dynamic_label(
            self, position: vec2, template: str, getter: Callable[[], Any | tuple[Any, ...]], font: StyleOrName[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        
        font = self._get_resource(font, Font)
        obj = self.label(position, "", font, rotation, scale, layer, anchor, cache)
        obj.make_attribute_dynamic("text", getter, template)
        
        return obj

    def text_box(
            self, position: vec2, text: str, width: Optional[int] = None, height: Optional[int] = None,
            justification: vec2 = TextBoxObject.JUSTIFY_LEFT,
            font: StyleOrName[Font] = None, bg_style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextBoxObject:

        font = self._get_resource(font, Font)
        bg_style = self._get_resource(bg_style, RectStyle)

        margin = getattr(bg_style, "margin", 0) if bg_style else 0
        max_content_width = (width - 2 * margin) if width is not None else None

        lines = split_text(text, font, max_content_width)

        text_objects = [
            self.label(vec2(), line, font, rotation=0.0, scale=1.0, layer=layer, anchor=Anchor.C, cache=cache)
            for line in lines
        ]

        obj = self.factory.ui.layout.create_layout(
            TextBoxObject, position, width, height,
            TextBoxObject.GRID_MODE, TextBoxObject.PRESERVE_MODE, TextBoxObject.PRESERVE_MODE,
            justification, bg_style, rotation, scale, layer, anchor, cache,
            text, font, text_objects, self.label
        )

        obj.set_cell_anchor(justification)

        for text_obj in text_objects:
            obj.stack_y(text_obj, x=0)

        return obj

    def __call__(
                 self, position: vec2, text: str, font: StyleOrName[Font] = None,
    rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        
        return self.label(position, text, font, rotation, scale, layer, anchor, cache)