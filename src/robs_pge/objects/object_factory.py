from typing import Any, Callable

from .objects import ButtonObject, CircleObject, LayoutObject, ProgressBar, PygameObject, RectObject, TextObject, DebugOverlay, ObjectFlags, LineObject, LineRenderer
from .behaviors import DynamicAttribute
from ..rendering import ButtonStyle, CircleRenderer, CircleStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, SpriteRenderer, TextRenderer
from ..resources import Texture
from ..utils import Anchor, DictCollection, Font, Transform, Vec2, inf


class ObjectFactory:
    def __init__(self):
        self._services = DictCollection()
    
    # region PROPERTIES
    
    # endregion
    
    def _get_services(self):
        return self._services
    
    def set_services(self, services: DictCollection):
        self._services = services
    
    def make_sprite(
            self, position: Vec2, texture: Texture,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache=True
    ):
        
        obj = PygameObject(
            Transform(position, rotation, scale),
            SpriteRenderer(texture, cache),
            self._services, layer, anchor
        )
        
        return obj
    
    
    
    def make_rect(
            self, position: Vec2, dims: Vec2, style: RectStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        
        obj = RectObject(
            Transform(position, rotation, scale ),
            RectRenderer(dims, style, cache),
            self._services, layer, anchor
        )
        
        return obj
    
    
    
    def make_circle(
            self, position: Vec2, radius: int, style: CircleStyle = None,
            scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        
        obj = CircleObject(
            Transform(position, scale),
            CircleRenderer(radius, style, cache),
            self._services, layer, anchor
        )
        
        return obj
    
    
    
    def make_text(
            self, position: Vec2, text: str, font: Font = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        obj = TextObject(
            Transform(position, rotation, scale),
            TextRenderer(text, font, cache),
            self._services, layer, anchor
        )
        
        return obj
    
    def make_dynamic_text(
            self, position: Vec2, template: str, getter: Callable[[], Any | tuple[Any, ...]], font: Font = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        
        obj = self.make_text(position, "", font, rotation, scale, layer, anchor, cache)
        obj.add_behavior(DynamicAttribute("text", getter, template))
        
        return obj
    
    
    def make_button(
            self, position: Vec2, text: str, action: Callable[[], None] | tuple[Callable[[], None]], dims: Vec2 = None, style: ButtonStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        style = style or ButtonStyle()
        margin = Vec2(style.margin)
        font = style.font
        dims = dims or font.get_render_size(text) + Vec2(margin*2)
        
        obj = ButtonObject(
            Transform(position, rotation, scale),
            RectRenderer(dims, style, cache),
            self.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache),
            action, self._services, layer, anchor
        )
        
        return obj
    
    
    # region Layouts
    
    def make_grid_layout(
            self, position: Vec2, width: int = None, height: int = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False, style: RectStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ):
        
        style = style or RectStyle()
        
        obj = LayoutObject(
            Transform(position, rotation, scale),
            RectRenderer(Vec2(), style, cache),
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
            
        if invert_x:
            obj.invert_left_right()
        if invert_y:
            obj.invert_up_down()
        
        return obj
    
    def make_column_layout(
            self, position: Vec2, width: int = None, height: int = None, min_row=0, max_row=inf, invert_y=False, style: RectStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ):
        return self.make_grid_layout(
            position, width, height, 0, 0, min_row, max_row, False, invert_y,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_row_layout(
            self, position: Vec2, width: int = None, height: int = None, min_col=0, max_col=inf, invert_x=False, style: RectStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ):
        return self.make_grid_layout(
            position, width, height, min_col, max_col, 0, 0, invert_x, False,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_debug_overlay(
            self, position: Vec2, width: int = None, height: int = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ):
        obj = DebugOverlay(
            Transform(position, rotation, scale),
            RectRenderer(Vec2(), None, cache),
            self._services, layer, anchor
        ).skip_rendering()
        
        obj.min_col = min_col
        obj.max_col = max_col
        obj.min_row = min_row
        obj.max_row = max_row
        
        if width is not None:
            obj.fix_width(width)
        if height is not None:
            obj.fix_height(height)
        
        if invert_x:
            obj.invert_left_right()
        if invert_y:
            obj.invert_up_down()
        
        return obj
    
    # endregion
    
    
    def make_progress_bar(
            self, position: Vec2, dims: Vec2, style: ProgressBarStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        
        bg_style = style or ProgressBarStyle()
        bar_style = RectStyle(style.color, bd_radius=(style.bd_radius-style.bd) if style.bd_radius > 0 else 0)
        
        bar = RectObject(
            Transform(),
            RectRenderer(dims - Vec2(style.bd * 2), bar_style, cache),
            self._services, layer, anchor
        )
        
        obj = ProgressBar(
            Transform(position, rotation, scale),
            RectRenderer(dims, bg_style, cache), bar,
            self._services, layer, anchor
        )
        
        return obj
    
    def make_line(
            self, position: Vec2, points: list[Vec2], style: ProgressBarStyle = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache=True
    ):
        
        style = style or LineStyle()
        
        obj = LineObject(
            Transform(position, rotation, scale),
            LineRenderer(points, style, cache),
            self._services, layer, anchor
        )
        
        return obj
    