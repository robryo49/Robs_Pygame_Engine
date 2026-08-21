from typing import Any, Optional

from .button_object_factory import ButtonObjectFactory
from .debug_object_factory import DebugObjectFactory
from .layout_object_factory import LayoutObjectFactory
from .sub_factory import SubObjectFactory
from ..custom import LineChartObject, ProgressBarObject, ScrollbarObject, SliderObject
from ..object import PygameObject
from ...rendering import CircleStyle, LineChartStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, ScrollbarStyle, SliderStyle
from ...utils import Anchor, StyleOrName, length, vec2, Callback, Font


class UIObjectFactory(SubObjectFactory):
    def __init__(self, object_factory):
        super().__init__(object_factory)
        
        self.button = ButtonObjectFactory(object_factory)
        self.layout = LayoutObjectFactory(object_factory)
        self.debug = DebugObjectFactory(object_factory)
    
    def slider(
            self, position: vec2, dims: vec2, min_value: float, max_value: float, step: Optional[float] = None, start_value=None, style: StyleOrName[SliderStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SliderObject:
        
        slider_style = self._get_resource(style, SliderStyle)
        bg_style = slider_style.bg_style
        bar_style = slider_style.bar_style
        handle_style: RectStyle | CircleStyle = slider_style.handle_style
        font = self._get_resource(slider_style.font, Font)
        
        max_text_width = font.get_render_size(str(max_value) + ".00" )[0]
        bar_width = slider_style.bar_width
        handle_size = slider_style.handle_size
        
        text_height = font.get_render_size(str(max_value) + ".00")[1]
        content_height = max(bar_width, text_height)
        margin = round((dims.y - content_height) * 0.5)
        
        bar = self.factory.shape.rect(vec2(), vec2(dims.x - margin * 3 - max_text_width, bar_width), bar_style, layer=layer)
        
        if isinstance(handle_style, RectStyle):
            handle_size: vec2 = vec2(handle_size)
            handle = self.factory.shape.rect(vec2(), vec2(handle_size), handle_style, layer=layer)
        else:
            handle_size: int = handle_size if isinstance(handle_size, int) else round(length(handle_size))
            handle = self.factory.shape.circle(vec2(), handle_size, handle_style, layer=layer)
        
        start_value = start_value if start_value is not None else min_value
        text = self.factory.text.label(vec2(), str(start_value), font, layer=layer)
        
        obj = self._create_object(SliderObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar, handle, text, min_value, max_value, step)
        obj.set_fixed_width(dims.x).set_fixed_height(dims.y)
        obj.set_cell_spacing(margin, True)
        obj.set_fixed_col_width(max_text_width + margin * 0.5, 0 if slider_style.text_position.lower() in ["left", "l"] else 1)

        obj.add(bar, 1 if slider_style.text_position.lower() in ["left", "l"] else 0, 0)
        obj.add(text, 0 if slider_style.text_position.lower() in ["left", "l"] else 1, 0)
        
        if slider_style.hide_bg:
            obj.skip_rendering()
        
        if start_value is not None:
            obj.value = start_value
        else:
            obj.value = min_value
        
        return obj
    
    
    def progress_bar(
            self, position: vec2, dims: vec2, style: StyleOrName[ProgressBarStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, cache_bar: bool = False
    ) -> ProgressBarObject:
        
        progress_bar_style = self._get_resource(style, ProgressBarStyle)
        bg_style = progress_bar_style.bg_style
        bar_style = RectStyle(progress_bar_style.color, bd_radius=(bg_style.bd_radius-bg_style.bd) if bg_style.bd_radius > 0 else 0)
        
        bar = self.factory.shape.rect(vec2(), vec2(0, dims.y), bar_style, 0.0, 1.0, layer, Anchor.C, cache_bar)
        obj = self._create_object(ProgressBarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar)
        
        return obj
    
    def line_chart(
            self, position: vec2, dims: vec2, style: StyleOrName[LineChartStyle] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None,
            max_data_points=None, max_data_x_range=None, update_action: Callback[[PygameObject], Any] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> LineChartObject:
        
        line_chart_style = self._get_resource(style, LineChartStyle)
        bg_style = line_chart_style.bg_style
        line_style = LineStyle(line_chart_style.line_color, line_chart_style.line_width)
        
        line = self.factory.shape.line(vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
        obj: LineChartObject = self._create_object(LineChartObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, line)
        
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
    
    def scrollbar(
            self, position: vec2, dims: vec2, style: ScrollbarStyle,
            start_value: float = 0.0, handle_height: Optional[float] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ScrollbarObject:
        
        scrollbar_style = self._get_resource(style, ScrollbarStyle)
        bg_style = scrollbar_style.bg_style
        handle_style = scrollbar_style.handle_style
        
        margin = scrollbar_style.margin
        
        handle_height = min(handle_height, dims.y - margin*2) if handle_height is not None else dims.y * 0.2
        
        handle = self.factory.shape.rect(vec2(), vec2(dims.x - margin * 2, handle_height), handle_style, layer=layer)
        
        obj = self._create_object(ScrollbarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, handle)
        
        obj.value = start_value
        
        return obj
    
