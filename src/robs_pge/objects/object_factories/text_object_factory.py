from typing import Callable, Any, Optional

from .sub_factory import SubObjectFactory

from ..custom import *
from ..behaviors import DynamicAttributeBehavior

from ...rendering import *
from ...utils import Vec2, Anchor, Font



class TextObjectFactory(SubObjectFactory):
    def make_text(
            self, position: Vec2, text: str, font: Optional[Font | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        
        font = self._get_resource(font, Font)
        obj = self._make_object(TextObject, position, rotation, scale, TextRenderer(text, font, cache), layer, anchor)
        
        return obj
    
    def make_dynamic_text(
            self, position: Vec2, template: str, getter: Callable[[], Any | tuple[Any, ...]], font: Optional[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        
        font = self._get_resource(font, Font)
        obj = self.make_text(position, "", font, rotation, scale, layer, anchor, cache)
        obj.add_behavior(DynamicAttributeBehavior("text", getter, template))
        
        return obj

