from typing import Any, Callable, Optional

from pygame import FRect

from .button_object_factories import ButtonObjectFactory
from .debug_object_factories import DebugObjectFactory
from .layout_object_factory import LayoutObjectFactory
from .sub_factory import SubObjectFactory
from ..custom import LineChartObject, ProgressBarObject, SliderObject, WindowObject, TextObject, RectObject, LayoutObject
from ..object import PygameObject
from ...rendering import CircleStyle, LineChartStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, SliderStyle, WindowStyle
from ...resources import Icons
from ...utils import Anchor, Vec2


class UIObjectFactory(SubObjectFactory):
    def __init__(self, object_factory):
        super().__init__(object_factory)
        
        self.buttons = ButtonObjectFactory(object_factory)
        self.layouts = LayoutObjectFactory(object_factory)
        self.debug = DebugObjectFactory(object_factory)
    
    def make_slider(
            self, position: Vec2, dims: Vec2, min_value: float, max_value: float, step: Optional[float] = None, start_value=None, style: Optional[SliderStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SliderObject:
        
        slider_style = self._get_resource(style, SliderStyle)
        bg_style = slider_style.bg_style
        bar_style = slider_style.bar_style
        handle_style: RectStyle | CircleStyle = slider_style.handle_style
        font = slider_style.font
        
        max_text_width = font.get_render_size(str(max_value) + ".00" )[0]
        bar_width = slider_style.bar_width
        handle_size = slider_style.handle_size
        
        text_height = font.get_render_size(str(max_value) + ".00")[1]
        content_height = max(bar_width, text_height)
        margin = round((dims.y - content_height) * 0.5)
        
        bar = self.factory.shape.make_rect(Vec2(), Vec2(dims.x - margin*3 - max_text_width, bar_width), bar_style)
        
        if isinstance(handle_style, RectStyle):
            handle_size: Vec2 = Vec2(handle_size)
            handle = self.factory.shape.make_rect(Vec2(), Vec2(handle_size), handle_style)
        else:
            handle_size: int = handle_size if isinstance(handle_size, int) else round(handle_size.magnitude())
            handle = self.factory.shape.make_circle(Vec2(), handle_size, handle_style)
        
        start_value = start_value if start_value is not None else min_value
        text = self.factory.text.make_text(Vec2(), str(start_value), font)
        
        obj = self._make_object(SliderObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar, handle, text, min_value, max_value, step)
        obj.fix_width(dims.x).fix_height(dims.y)
        obj.set_constant_padding(margin)
        obj.fix_col_width(0 if slider_style.text_position.lower() in ["left", "l"] else 1, max_text_width+margin*0.5)
        
        
        obj.add_object(bar, 1 if slider_style.text_position.lower() in ["left", "l"] else 0, 0)
        obj.add_object(text, 0 if slider_style.text_position.lower() in ["left", "l"] else 1, 0)
        
        if slider_style.hide_bg:
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
        
        progress_bar_style = self._get_resource(style, ProgressBarStyle)
        bg_style = progress_bar_style.bg_style
        bar_style = RectStyle(progress_bar_style.color, bd_radius=(bg_style.bd_radius-bg_style.bd) if bg_style.bd_radius > 0 else 0)
        
        bar = self.factory.shape.make_rect(Vec2(), Vec2(0, dims.y), bar_style, 0.0, 1.0, layer, Anchor.C, cache_bar)
        obj = self._make_object(ProgressBarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar)
        
        return obj
    
    def make_line_chart(
            self, position: Vec2, dims: Vec2, style: Optional[LineChartStyle | str] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None,
            max_data_points=None, max_data_x_range=None, update_action: Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...]]=None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> LineChartObject:
        
        line_chart_style = self._get_resource(style, LineChartStyle)
        bg_style = line_chart_style.bg_style
        line_style = LineStyle(line_chart_style.line_color, line_chart_style.line_width)
        
        line = self.factory.shape.make_line(Vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
        obj: LineChartObject = self._make_object(LineChartObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, line)
        
        if pad_x: obj.pad_x = pad_x
        if pad_y: obj.pad_y = pad_y
        if min_x is not None: obj.min_x_value = min_x
        if min_y is not None: obj.min_y_value = min_y
        if max_x is not None: obj.max_x_value = max_x
        if max_y is not None: obj.max_y_value = max_y
        if max_data_points is not None: obj.max_data_points = max_data_points
        if max_data_x_range is not None: obj.max_data_x_range = max_data_x_range
        
        if update_action is not None: obj.do_on_update(update_action)
        
        return obj
    
    def make_window(
            self, position: Vec2, dims: Vec2, style: Optional[WindowStyle | str],
            title: str,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        
        window_style = self._get_resource(style, WindowStyle)
        bg_style = window_style.bg_style
        margin = window_style.margin
        
        show_title = window_style.show_title
        title_panel_style = window_style.title_panel_style
        title_panel_margin = window_style.title_panel_margin
        title_panel_height = window_style.title_panel_height
        
        title_font = window_style.title_font
        title_align = window_style.title_align
        title_in_header = window_style.title_in_header
        
        title_object: Optional[TextObject] = None
        title_panel: Optional[RectObject] = None
        if show_title:
            title_object: TextObject = self.factory.text.make_text(Vec2(), title, title_font)
            
            if not title_in_header:
                title_panel_height = title_panel_height if title_panel_height is not None else title_object.height + title_panel_margin
                title_panel: RectObject = self.factory.shape.make_rect(Vec2(), Vec2(dims.x, title_panel_height), style=title_panel_style)
                
                title_offset = title_panel_margin  * (Vec2(1) - title_align*2)
                title_object.pos = title_offset
                title_object.anchor = title_align
                title_panel.add_child(title_object, title_align)
        
        
        show_header = window_style.show_header
        header_style = window_style.header_style
        header_height = window_style.header_height
        header_margin = window_style.header_margin
        
        show_header_buttons = window_style.show_header_buttons
        icon_buttons_style = window_style.icon_buttons_style
        
        header: Optional[LayoutObject] = None
        if show_header:
            header_height = header_height if header_height is not None else title_object.height + header_margin if title_object is not None and title_in_header else None
            
            if header_height is None: raise ValueError("cannot determine header height when creating window, must specify title or header height")
            
            header: LayoutObject = self.factory.ui.layouts.make_horizontal_layout(Vec2(), dims.x, header_height, style=header_style)
            header.set_constant_padding(header_margin)
            
            buttons_height = header_height-header_margin*2
            buttons_width = buttons_height * 1.5
            header.fix_col_width(0, dims.x - (buttons_width + header_margin) * 1 - header_margin)
            
            if title_in_header and title_object is not None:
                title_offset = header_margin  * (Vec2(1) - title_align*2)
                title_object.pos = title_offset
                title_object.anchor = title_align
                header.add_object(title_object, 0, 0, anchor=title_align)
                
            if show_header_buttons:
                button_dims = Vec2(buttons_width, buttons_height)
                x_button = self.factory.ui.buttons.make_icon_button(Vec2(), Icons.X, header_height-header_margin*4, None, button_dims, style=icon_buttons_style)
                
                header.add_object(x_button, 1, 0)
        
        panel_height = dims.y - (title_panel_height or 0) - (header_height or 0)
        panel = self.factory.ui.layouts.make_grid_layout(Vec2(), dims.x, panel_height)
        w, h = panel.dims
        panel.set_children_clip_area(FRect(margin, margin, w - margin*2, h - margin*2))
        
        obj = self._make_object(WindowObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, title, panel, header, title_panel, title_object)
        obj.invert_up_down()
        
        if header is not None:
            obj.stack_y(header)
        if title_panel is not None:
            obj.stack_y(title_panel)
        obj.stack_y(panel)
        
        return obj
    
