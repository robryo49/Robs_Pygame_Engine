from typing import Any, Callable, Optional

from pygame import FRect

from .button_object_factories import ButtonObjectFactory
from .debug_object_factories import DebugObjectFactory
from .layout_object_factory import LayoutObjectFactory
from .sub_factory import SubObjectFactory
from ..custom import LineChartObject, ProgressBarObject, SliderObject, WindowObject, TextObject, RectObject, LayoutObject, ScrollbarObject
from ..object import PygameObject
from ...rendering import CircleStyle, LineChartStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, SliderStyle, WindowStyle, ScrollbarStyle, IconButtonStyle
from ...resources import Icons
from ...utils import Anchor, StyleOrName, length, vec2, clamp


class UIObjectFactory(SubObjectFactory):
    def __init__(self, object_factory):
        super().__init__(object_factory)
        
        self.buttons = ButtonObjectFactory(object_factory)
        self.layouts = LayoutObjectFactory(object_factory)
        self.debug = DebugObjectFactory(object_factory)
    
    def make_slider(
            self, position: vec2, dims: vec2, min_value: float, max_value: float, step: Optional[float] = None, start_value=None, style: StyleOrName[SliderStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
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
        
        bar = self.factory.shape.make_rect(vec2(), vec2(dims.x - margin*3 - max_text_width, bar_width), bar_style, layer=layer)
        
        if isinstance(handle_style, RectStyle):
            handle_size: vec2 = vec2(handle_size)
            handle = self.factory.shape.make_rect(vec2(), vec2(handle_size), handle_style, layer=layer)
        else:
            handle_size: int = handle_size if isinstance(handle_size, int) else round(length(handle_size))
            handle = self.factory.shape.make_circle(vec2(), handle_size, handle_style, layer=layer)
        
        start_value = start_value if start_value is not None else min_value
        text = self.factory.text.make_text(vec2(), str(start_value), font, layer=layer)
        
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
            self, position: vec2, dims: vec2, style: StyleOrName[ProgressBarStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, cache_bar: bool = False
    ) -> ProgressBarObject:
        
        progress_bar_style = self._get_resource(style, ProgressBarStyle)
        bg_style = progress_bar_style.bg_style
        bar_style = RectStyle(progress_bar_style.color, bd_radius=(bg_style.bd_radius-bg_style.bd) if bg_style.bd_radius > 0 else 0)
        
        bar = self.factory.shape.make_rect(vec2(), vec2(0, dims.y), bar_style, 0.0, 1.0, layer, Anchor.C, cache_bar)
        obj = self._make_object(ProgressBarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar)
        
        return obj
    
    def make_line_chart(
            self, position: vec2, dims: vec2, style: StyleOrName[LineChartStyle] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None,
            max_data_points=None, max_data_x_range=None, update_action: Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...]]=None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> LineChartObject:
        
        line_chart_style = self._get_resource(style, LineChartStyle)
        bg_style = line_chart_style.bg_style
        line_style = LineStyle(line_chart_style.line_color, line_chart_style.line_width)
        
        line = self.factory.shape.make_line(vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
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

    def make_window(self, position: vec2, dims: vec2, title: str, draggable: bool = False, style: StyleOrName[WindowStyle] = None,
                    rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True) -> WindowObject:
        
        window_style = self._get_resource(style, WindowStyle)
        bg_style = window_style.bg_style
        margin = window_style.margin
        
        # region TITLE
        
        title_object: Optional[TextObject] = None
        title_panel: Optional[RectObject] = None
        
        title_panel_height = 0
        if window_style.show_title:
            title_object: TextObject = self.factory.text.make_text(vec2(), title, window_style.title_font, layer=layer)
            
            if not window_style.title_in_header:
                title_panel_height = window_style.title_panel_height or (title_object.height + window_style.title_panel_margin)
                title_panel: RectObject = self.factory.shape.make_rect(vec2(), vec2(dims.x, title_panel_height), style=window_style.title_panel_style, layer=layer)
                
                title_offset = window_style.title_panel_margin * (vec2(1) - window_style.title_align * 2)
                title_object.pos = title_offset
                title_object.anchor = window_style.title_align
                title_panel.add_child(title_object, window_style.title_align)
        
        # endregion
        
        # region HEADER
        
        header: Optional[LayoutObject] = None
        
        if window_style.show_header:
            header_height = window_style.header_height
            if header_height is None:
                if title_object is not None and window_style.title_in_header:
                    header_height = title_object.height + window_style.header_margin
                else:
                    raise ValueError("cannot determine header height when creating window, must specify title or header height")
            
            header_style = self._get_resource(window_style.header_style, RectStyle)
            header: LayoutObject = self.factory.ui.layouts.make_horizontal_layout(vec2(), dims.x, header_height, style=header_style, layer=layer)
            header.set_constant_padding(window_style.header_margin)
            
            buttons_width = (header_height - window_style.header_margin * 2) * 1.5
            header.fix_col_width(0, dims.x - buttons_width - window_style.header_margin * 2)
            
            if window_style.title_in_header and title_object is not None:
                title_offset = window_style.header_margin * (vec2(1) - window_style.title_align * 2)
                title_object.pos = title_offset
                title_object.anchor = window_style.title_align
                header.add_object(title_object, 0, 0, anchor=window_style.title_align)
            
            if window_style.show_header_buttons:
                icon_buttons_style = self._get_resource(window_style.icon_buttons_style, IconButtonStyle)
                button_dims = vec2(buttons_width, header_height - window_style.header_margin * 2)
                
                x_button = self.factory.ui.buttons.make_icon_button(
                    vec2(), Icons.XMARK, button_dims * 0.5, lambda: obj.close(), button_dims, style=icon_buttons_style, layer=layer
                )
                header.add_object(x_button, 1, 0)
        else:
            header_height = 0
        
        # endregion
        
        # region CONTENT PANEL + SCROLLBAR
        
        scrollbar_style = self._get_resource(window_style.scrollbar_style, ScrollbarStyle)
        scrollbar_col_width = window_style.scrollbar_width + window_style.scrollbar_edge_margin * 2
        
        panel_height = dims.y - title_panel_height - header_height
        panel_width = dims.x - scrollbar_col_width
        
        panel = self.factory.ui.layouts.make_grid_layout(vec2(), panel_width, panel_height, layer=layer)
        panel.set_children_clip_area(
            FRect(margin - panel_width * 0.5, margin - panel_height * 0.5, panel_width - margin * 2, panel_height - margin * 2), True
        )
        
        scrollbar = self.make_scrollbar(
            vec2(), vec2(window_style.scrollbar_width, panel_height - window_style.scrollbar_edge_margin * 2),
            scrollbar_style, layer=layer + 1
        )
        
        # endregion
        
        # region ASSEMBLY
        
        obj: WindowObject = self._make_object(
            WindowObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
            title, panel, header, title_panel, title_object, scrollbar
        )
        
        row = 0
        if header is not None:
            obj.add_object(header, 0, row, span_x=2)
            row += 1
        if title_panel is not None:
            obj.add_object(title_panel, 0, row, span_x=2)
            row += 1
        
        obj.add_object(panel, 0, row)
        obj.fix_col_width(0, panel_width)
        
        obj.add_object(scrollbar, 1, row, anchor=Anchor.R)
        obj.fix_col_width(1, scrollbar_col_width)
        obj.set_cell_padding(vec2(window_style.scrollbar_edge_margin, 0), (1, row))
        
        # endregion
        
        # region WIRING
        
        def _on_panel_scroll(o: PygameObject, scroll: int, pos: vec2):
            max_offset = panel.get_scroll_range_y()
            if max_offset > 0:
                scrollbar.set_value(clamp(scrollbar.value - scroll * 40 / max_offset, 0.0, 1.0))
        
        panel.do_on_scroll(_on_panel_scroll)
        panel.make_attribute_dynamic("scroll_offset", lambda: vec2(0, scrollbar.value * panel.get_scroll_range_y()), strength=0.2)
        
        if draggable:
            drag_handle = header if header is not None else (title_panel if title_panel is not None else obj)
            drag_handle.make_draggable(1, target=obj)
        
        obj.sync_scrollbar()
        
        # endregion
        
        return obj
    
    def make_scrollbar(
            self, position: vec2, dims: vec2, style: ScrollbarStyle,
            start_value: float = 0.0, handle_height: Optional[float] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ScrollbarObject:
        
        scrollbar_style = self._get_resource(style, ScrollbarStyle)
        bg_style = scrollbar_style.bg_style
        handle_style = scrollbar_style.handle_style
        
        margin = scrollbar_style.margin
        
        handle_height = min(handle_height, dims.y - margin*2) if handle_height is not None else dims.y * 0.2
        
        handle = self.factory.shape.make_rect(vec2(), vec2(dims.x - margin*2, handle_height), handle_style, layer=layer)
        
        obj = self._make_object(ScrollbarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, handle)
        
        obj.value = start_value
        
        return obj
    
