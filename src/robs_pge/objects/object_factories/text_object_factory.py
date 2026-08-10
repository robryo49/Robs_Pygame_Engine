from typing import Any, Callable

from .sub_factory import SubObjectFactory
from ..custom import *
from ...rendering import *
from ...utils import Anchor, Font, StyleOrName, vec2


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
        obj.create_attribute_dynamic("text", getter, template)
        
        return obj

