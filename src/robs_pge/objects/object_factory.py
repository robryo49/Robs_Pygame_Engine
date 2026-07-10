from typing import Any, Callable, Optional

from .custom import *
from .behaviors import DynamicAttributeBehavior
from ..rendering import *
from ..rendering.styles import SpriteButtonStyle
from ..resources import Texture, ResourceManager
from ..utils import Anchor, DictCollection, Font, Transform, Vec2, inf, Rect
from .behaviors import ActionOnUpdateBehavior


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
    
    def _get_resource[T](self, resource: Optional[str | Any], style_type: type[T]) -> T:
        if isinstance(resource, str):
            return self._services.get(ResourceManager).get(style_type, resource)
        elif resource is not None:
            return resource
        else:
            return style_type()
    
    def _make_object[T](self, object_type: type[T], position, rotation, scale, renderer, layer, anchor, *args) -> T:
        return object_type(Transform(position, rotation, scale), renderer, *args, self._services, layer, anchor)
    
    def make_rect(
            self, position: Vec2, dims: Vec2, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> RectObject:
        
        style = self._get_resource(style, RectStyle)
        obj = self._make_object(RectObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor)
        
        return obj
    
    def make_circle(
            self, position: Vec2, radius: int, style: Optional[CircleStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> CircleObject:
        
        style = self._get_resource(style, CircleStyle)
        obj = self._make_object(CircleObject, position, rotation, scale, CircleRenderer(radius, style, cache), layer, anchor)
        
        return obj
    
    def make_line(
            self, position: Vec2, points: list[Vec2], style: Optional[LineStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> LineObject:
        
        style = self._get_resource(style, LineStyle)
        obj = self._make_object(LineObject, position, rotation, scale, LineRenderer(points, style, cache), layer, anchor)
        
        return obj
    
    
    def make_sprite(
            self, position: Vec2, texture: Texture | str,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteObject:
        
        texture = self._get_resource(texture, Texture)
        obj = self._make_object(SpriteObject, position, rotation, scale, SpriteRenderer(texture, cache), layer, anchor)
        
        return obj
    
    
    def make_subsurface_sprite(
            self, position: Vec2, texture: Texture | str, sub_rect: Optional[Rect] = None, target_dims: Optional[Vec2] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SubSurfaceSpriteObject:
        
        texture = self._get_resource(texture, Texture)
        if target_dims is None: target_dims = Vec2(texture.dims)
        if sub_rect is None: sub_rect = Rect(0, 0, target_dims.x, target_dims.y)
        
        obj = self._make_object(SubSurfaceSpriteObject, position, rotation, scale, SubSurfaceRenderer(texture, sub_rect, target_dims, cache), layer, anchor)
        
        return obj
    
    def make_chunked_sprite(
            self, position: Vec2, texture: Texture | str, chunk_size: int = 256,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ChunkedSpriteObject:
        
        texture = self._get_resource(texture, Texture)
        obj = self._make_object(ChunkedSpriteObject, position, rotation, scale, ChunkedSpriteRenderer(texture, chunk_size, cache), layer, anchor)
        
        return obj
    
    
    
    
    
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
        obj = self.make_text(position, "", font, rotation, scale, layer, anchor, cache).add_behavior(DynamicAttributeBehavior("text", getter, template))
        
        return obj
    
    
    
    def make_button(
            self, position: Vec2, text: str, action: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[ButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ButtonObject:
        
        
        style = self._get_resource(style, ButtonStyle)
        margin = Vec2(style.margin)
        font = style.font
        dims = dims or font.get_render_size(text) + Vec2(margin*2)
        
        obj = self._make_object(ButtonObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor,
            self.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), action
        )
        
        return obj
    
    def make_value_switching_button(
            self, position: Vec2, texts: tuple[str, ...], values: Optional[tuple[Any, ...]] = None, default_index: int = 0, callback: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[ButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ValueSwitchingButtonObject:
        
        if values is None:
            values = texts
            
        text = texts[default_index]
        
        style = self._get_resource(style, ButtonStyle)
        margin = Vec2(style.margin)
        font = style.font
        text_dims = [font.get_render_size(t) for t in texts]
        dims = dims or Vec2(max(d[0] for d in text_dims), max(d[1] for d in text_dims)) + Vec2(margin*2)
        
        obj = self._make_object(ValueSwitchingButtonObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor,
                                self.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), texts, values, callback
                                )
        
        return obj
    
    def make_sprite_button(
            self, position: Vec2, texture: Texture, action: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[SpriteButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        style = self._get_resource(style, SpriteButtonStyle)
        margin = Vec2(style.margin)
        
        sprite = self.make_sprite(Vec2(), texture)
        
        dims = dims or texture.dims + Vec2(margin*2)
        
        obj = self._make_object(SpriteButtonObject, position, rotation, scale, RectRenderer(dims, style, cache), layer, anchor, sprite, action)
        
        return obj
    
    def make_icon_button(
            self, position: Vec2, icon: str, icon_size: int, action: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[IconButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        style = self._get_resource(style, IconButtonStyle)
        button_style = SpriteButtonStyle(style.bg_color, style.bd, style.bd_color, style.bd_radius, style.margin)
        
        return self.make_sprite_button(position, Texture.icon_from_svg(icon, icon_size, style.icon_color), action, dims, button_style, rotation, scale, layer, anchor)
    
    
    # region Layouts
    
    def make_grid_layout(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        
        style = self._get_resource(style, RectStyle)
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
    
    def make_vertical_layout(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_row=0, max_row=inf, invert_y=False, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.make_grid_layout(
            position, width, height, 0, 0, min_row, max_row, False, invert_y,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_horizontal_layout(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_col=0, max_col=inf, invert_x=False, style: Optional[RectStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool=True
    ) -> LayoutObject:
        return self.make_grid_layout(
            position, width, height, min_col, max_col, 0, 0, invert_x, False,
            style, rotation, scale, layer, anchor, cache
        )
    
    def make_debug_overlay(
            self, position: Vec2, width: Optional[int | float] = None, height: Optional[int | float] = None, min_col=0, max_col=inf, min_row=0, max_row=inf, invert_x=False, invert_y=False,
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
    
    
    def make_slider(
            self, position: Vec2, dims: Vec2, min_value: float, max_value: float, step: Optional[float] = None, start_value=None, style: Optional[SliderStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SliderObject:
        
        bg_style = self._get_resource(style, SliderStyle)
        bar_style = bg_style.bar_style
        handle_style: RectStyle | CircleStyle = bg_style.handle_style
        font = bg_style.font
        
        max_text_width = font.get_render_size(str(max_value))[0]
        bar_width = bg_style.bar_width
        handle_size = bg_style.handle_size
        
        bar = self.make_rect(Vec2(), Vec2(dims.x - (dims.y - bar_width) - max_text_width, bar_width), bar_style)
        if isinstance(handle_style, RectStyle):
            handle_size: Vec2 = Vec2(handle_size)
            handle = self.make_rect(Vec2(), Vec2(handle_size), handle_style)
        else:
            handle_size: int = handle_size if isinstance(handle_size, int) else round(handle_size.magnitude())
            handle = self.make_circle(Vec2(), handle_size, handle_style)
        
        start_value = start_value if start_value is not None else min_value
        text = self.make_text(Vec2(), str(start_value), font)
        
        obj = self._make_object(SliderObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar, handle, text, min_value, max_value, step)
        obj.fix_width(dims.x).fix_height(dims.y)
        obj.set_constant_padding(round((dims.y - bar_width)*0.5))
        obj.fix_col_width(1, max_text_width)
        
        obj.add_object(bar, 1 if bg_style.text_position.lower() in ["left", "l"] else 0, 0, anchor=Anchor.C)
        obj.add_object(text, 0 if bg_style.text_position.lower() in ["left", "l"] else 1, 0, anchor=Anchor.C)
        
        if bg_style.hide_bg:
            obj.skip_rendering()
            
        if start_value is not None:
            obj.value = start_value
        else:
            obj.value = min_value
        
        return obj
    
    
    def make_progress_bar(
            self, position: Vec2, dims: Vec2, style: Optional[ProgressBarStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True, cache_bar: bool = False
    ) -> ProgressBarObject:
        
        bg_style = self._get_resource(style, ProgressBarStyle)
        bar_style = RectStyle(bg_style.color, bd_radius=(bg_style.bd_radius-bg_style.bd) if bg_style.bd_radius > 0 else 0)
        
        bar = self.make_rect(Vec2(), Vec2(0, dims.y), bar_style, 0.0, 1.0, layer, Anchor.C, cache_bar)
        obj = self._make_object(ProgressBarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar)
        
        return obj
    
    def make_graph(
            self, position: Vec2, dims: Vec2, style: Optional[GraphStyle | str] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None, max_data_points=None, max_data_x_range=None, update_action=None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> GraphObject:
        
        bg_style = self._get_resource(style, GraphStyle)
        line_style = LineStyle(bg_style.line_color, bg_style.line_width)
        
        line = self.make_line(Vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
        obj: GraphObject = self._make_object(GraphObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, line)
        
        if pad_x: obj.pad_x = pad_x
        if pad_y: obj.pad_y = pad_y
        if min_x is not None: obj.min_x_value = min_x
        if min_y is not None: obj.min_y_value = min_y
        if max_x is not None: obj.max_x_value = max_x
        if max_y is not None: obj.max_y_value = max_y
        if max_data_points is not None: obj.max_data_points = max_data_points
        if max_data_x_range is not None: obj.max_data_x_range = max_data_x_range
        
        if update_action is not None: obj.add_behavior(ActionOnUpdateBehavior(update_action))
        
        return obj
    
    
    def make_debug_panel(
            self, position: Vec2, dims: Vec2, style: DebugPanelStyle | str, title: str,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0,
            anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> DebugPanelObject:
        
        style = self._get_resource(style, DebugPanelStyle)
    
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
    
    