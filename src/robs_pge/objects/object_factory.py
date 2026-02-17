from typing import Callable

from .objects import ButtonObject, CircleObject, LayoutObject, PygameObject, RectObject, TextObject
from ..rendering import ButtonStyle, CircleShape, CircleStyle, RectShape, RectStyle, SpriteRenderer, TextRenderer
from ..resources import Texture
from ..utils import Anchor, Color, DictCollection, Font, Transform, Vec2, inf


class ObjectFactory:
    def __init__(self, services: DictCollection):
        self._services = services
    
    # region PROPERTIES
    
    # endregion
    
    def _get_services(self):
        return self._services
    
    def make_sprite(
            self, position: Vec2, texture: Texture,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C
    ):
        
        obj = PygameObject(
            Transform(position, rotation, scale),
            SpriteRenderer(texture),
            self._services, layer, anchor
        )
        
        return obj
    
    
    
    def make_rect(
            self, position: Vec2, dims: Vec2, bg_color: Color = None, border: int = None, bd_color: Color = None, bd_radius: int = None, style: RectStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        
        obj = RectObject(
            Transform(position, rotation, scale ),
            RectShape(dims, bg_color, border, bd_color, bd_radius, style),
            self._services, layer, anchor
        )
        
        return obj
    
    
    
    def make_circle(
            self, position: Vec2, radius: int, bg_color: Color = None, border: int = None, bd_color: Color = None, style: CircleStyle = None,
            scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        
        obj = CircleObject(
            Transform(position, scale),
            CircleShape(radius, bg_color, border, bd_color, style),
            self._services, layer, anchor
        )
        
        return obj
    
    
    
    def make_text(
            self, position: Vec2, text: str, font: Font = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        obj = TextObject(
            Transform(position, rotation, scale),
            TextRenderer(text, font),
            self._services, layer, anchor
        )
        
        return obj
    
    def make_button(
            self, position: Vec2, text: str, action: Callable[[], None] | tuple[Callable[[], None]], dims: Vec2 = None, bg_color: Color = None,
            border: int = None, bd_color: Color = None, bd_radius: int = None, margin: int | Vec2 = None, font: Font = None, style: ButtonStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        style = style or ButtonStyle()
        margin = Vec2(margin or style.margin)
        font = font or style.font if style else Font()
        dims = dims or font.get_render_size(text) + Vec2(margin*2)
        
        obj = ButtonObject(
            Transform(position, rotation, scale),
            RectShape(dims, bg_color, border, bd_color, bd_radius, style),
            self.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C),
            action, self._services, layer, anchor
        )
        
        return obj
    
    def make_grid_layout(
            self, position: Vec2, width: int = None, height: int = None, min_col=0, max_col=inf, min_row=0, max_row=inf,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        
        obj = LayoutObject(
            Transform(position, rotation, scale),
            RectShape(Vec2()),
            self._services, layer, anchor
        )
        
        obj.min_col = min_col
        obj.max_col = max_col
        obj.min_row = min_row
        obj.max_row = max_row
        
        if width is not None:
            obj.fix_width(width)
        if height is not None:
            obj.fix_height(height)
        
        return obj
    
    def make_column_layout(
            self, position: Vec2, width: int = None, height: int = None, min_row=0, max_row=inf,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        return self.make_grid_layout(position, width, height, 0, 0, min_row, max_row, rotation, scale, layer, anchor)
    
    def make_row_layout(
            self, position: Vec2, width: int = None, height: int = None, min_col=0, max_col=inf,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C
    ):
        return self.make_grid_layout(position, width, height, min_col, max_col, 0, 0, rotation, scale, layer, anchor)