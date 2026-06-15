from typing import Any, Callable, Optional

from .objects import ButtonObject, CircleObject, DebugPanelObject, LayoutObject, ProgressBarObject, PygameObject, RectObject, TextObject, DebugOverlay, LineObject, LineRenderer, GraphObject, ActionOnUpdateBehavior
from .behaviors import DynamicAttribute
from rendering import ButtonStyle, CircleRenderer, CircleStyle, DebugPanelStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, SpriteRenderer, TextRenderer, GraphStyle
from resources import Texture
from utils import Anchor, DictCollection, Font, Transform, Vec2, inf


class ObjectFactory:
    def __init__(self):
        self._services = DictCollection()
    
    # region PROPERTIES
    
    @property
    def services(self):
        return self._services
    
    @services.setter
    def services(self, value: DictCollection):
        self._services = value
    
    # endregion
    
    
    def _make_object(self, object_type: type, position, rotation, scale, renderer, layer, anchor, *args):
        return object_type(Transform(position, rotation, scale), renderer, *args, self._services, layer, anchor)
    
    def make_rect(
            self, position: Vec2, dims: Vec2, style: Optional[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> RectObject:
        
        obj = self._make_object(RectObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor)
        
        return obj
    
    def make_circle(
            self, position: Vec2, radius: int, style: Optional[CircleStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> CircleObject:
        obj = self._make_object(CircleObject, position, rotation, scale, CircleRenderer(radius, style, cache), layer, anchor)
        
        return obj
    
    def make_line(
            self, position: Vec2, points: list[Vec2], style: Optional[LineStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> LineObject:
        
        style = style or LineStyle()
        
        obj = self._make_object(LineObject, position, rotation, scale, LineRenderer(points, style, cache), layer, anchor)
        
        return obj
    
    
    
    
    def make_sprite(
            self, position: Vec2, texture: Texture,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> PygameObject:
        
        obj = self._make_object(PygameObject, position, rotation, scale, SpriteRenderer(texture, cache), layer, anchor)
        
        return obj
    
    
    
    
    def make_text(
            self, position: Vec2, text: str, font: Optional[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        obj = self._make_object(TextObject, position, rotation, scale, TextRenderer(text, font, cache), layer, anchor)
        
        return obj
    
    def make_dynamic_text(
            self, position: Vec2, template: str, getter: Callable[[], Any | tuple[Any, ...]], font: Optional[Font] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> TextObject:
        
        obj = self.make_text(position, "", font, rotation, scale, layer, anchor, cache).add_behavior(DynamicAttribute("text", getter, template))
        
        return obj
    
    
    
    def make_button(
            self, position: Vec2, text: str, action: Callable[[], None] | tuple[Callable[[], None]], dims: Optional[Vec2] = None, style: Optional[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ButtonObject:
        style = style or ButtonStyle()
        margin = Vec2(style.margin)
        font = style.font
        dims = dims or font.get_render_size(text) + Vec2(margin*2)
        
        obj = self._make_object(ButtonObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor,
            self.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), action
        )
        
        return obj
    
    
    # region Layouts
    
    def make_grid_layout(
            self, position: Vec2, width: Optional[int] = None, height: Optional[int] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False, style: Optional[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        
        style = style or RectStyle()
        
        obj = self._make_object(LayoutObject, position, rotation, scale, RectRenderer(Vec2(), style, cache), layer, anchor)
        
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
            self, position: Vec2, width: Optional[int] = None, height: Optional[int] = None, min_row=0, max_row=inf, invert_y=False, style: Optional[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.make_grid_layout(
            position, width, height, 0, 0, min_row, max_row, False, invert_y,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_row_layout(
            self, position: Vec2, width: Optional[int] = None, height: Optional[int] = None, min_col=0, max_col=inf, invert_x=False, style: Optional[RectStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.make_grid_layout(
            position, width, height, min_col, max_col, 0, 0, invert_x, False,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_debug_overlay(
            self, position: Vec2, width: Optional[int] = None, height: Optional[int] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> DebugOverlay:
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
            self, position: Vec2, dims: Vec2, style: Optional[ProgressBarStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True, cache_bar: bool = False
    ) -> ProgressBarObject:
        
        bg_style = style or ProgressBarStyle()
        bar_style = RectStyle(bg_style.color, bd_radius=(bg_style.bd_radius-bg_style.bd) if bg_style.bd_radius > 0 else 0)
        
        bar = self.make_rect(Vec2(), Vec2(0, dims.y), bar_style, 0.0, 1.0, layer, Anchor.C, cache_bar)
        obj = self._make_object(ProgressBarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar)
        
        return obj
    
    def make_graph(
            self, position: Vec2, dims: Vec2, style: Optional[GraphStyle] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None, max_data_points=None, max_data_x_range=None, update_action=None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> GraphObject:
        
        bg_style = style or GraphStyle()
        line_style = LineStyle(bg_style.line_color, bg_style.line_width)
        
        line = self.make_line(Vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
        obj: GraphObject = self._make_object(GraphObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, line)
        
        if pad_x: obj.pad_x = pad_x
        if pad_y: obj.pad_y = pad_y
        if min_x is not None: obj.min_x = min_x
        if min_y is not None: obj.min_y = min_y
        if max_x is not None: obj.max_x = max_x
        if max_y is not None: obj.max_y = max_y
        if max_data_points is not None: obj.max_data_points = max_data_points
        if max_data_x_range is not None: obj.max_data_x_range = max_data_x_range
        
        if update_action is not None: obj.add_behavior(ActionOnUpdateBehavior(update_action))
        
        return obj
    
    
    def make_debug_panel(
            self, position: Vec2, dims: Vec2, style: DebugPanelStyle, title: str,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0,
            anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> DebugPanelObject:
    
        width = round(dims.x)
        
        header_height = 4
        title_height = 30
        panel_height = round(dims.y - title_height - header_height)
        
        panel = self.make_grid_layout(
            Vec2(),
            width,
            panel_height,
            style=style.panel_style
        )
        
        title_panel = self.make_rect(
            Vec2(),
            Vec2(width, title_height),
            style=style.title_panel_style
        )
        
        header = self.make_rect(
            Vec2(),
            Vec2(width, header_height),
            style=style.header_style
        )
        
        title_text = self.make_text(
            Vec2(8, -1),
            title.upper(),
            style.title_font,
            anchor=Anchor.L
        )
        
        title_panel.add_child(title_text, Anchor.L)
        
        layout = DebugPanelObject(
            Transform(position, rotation, scale),
            RectRenderer(Vec2(), None, cache),
            self._services,
            panel,
            title_panel,
            header,
            title_text,
            layer,
            anchor
        ).skip_rendering()
        
        layout.fix_width(width)
        layout.fix_height(round(dims.y))
        
        layout.stack_y(panel)
        layout.stack_y(title_panel)
        layout.stack_y(header)
        
        return layout
    
    