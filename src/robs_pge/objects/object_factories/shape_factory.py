from .sub_factory import SubObjectFactory
from ..custom import CircleObject, LineObject, RectObject
from ...rendering import CircleRenderer, CircleStyle, LineRenderer, LineStyle, RectRenderer, RectStyle
from ...utils import Anchor, StyleOrName, vec2


class ShapeFactory(SubObjectFactory):
    
    def make_rect(
            self, position: vec2, dims: vec2, style: StyleOrName[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> RectObject:
        
        style = self._get_resource(style, RectStyle)
        obj = self._make_object(RectObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor)
        
        return obj
    
    def make_circle(
            self, position: vec2, radius: int, style: StyleOrName[CircleStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> CircleObject:
        
        style = self._get_resource(style, CircleStyle)
        obj = self._make_object(CircleObject, position, rotation, scale, CircleRenderer(radius, style, cache), layer, anchor)
        
        return obj
    
    def make_line(
            self, position: vec2, points: list[vec2], style: StyleOrName[LineStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> LineObject:
        
        style = self._get_resource(style, LineStyle)
        obj = self._make_object(LineObject, position, rotation, scale, LineRenderer(points, style, cache), layer, anchor)
        
        return obj
    
