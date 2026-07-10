from typing import Optional

from .button_object_factories import ButtonObjectFactory
from .debug_object_factories import DebugObjectFactory
from .layout_object_factory import LayoutObjectFactory
from .sub_factory import SubObjectFactory
from ..behaviors import ActionOnUpdateBehavior
from ..custom import GraphObject, ProgressBarObject, SliderObject
from ...rendering import RectRenderer, RectStyle, SliderStyle, CircleStyle, ProgressBarStyle, GraphStyle, LineStyle
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
        
        max_text_width = font.get_render_size(str(max_value))[0]
        bar_width = slider_style.bar_width
        handle_size = slider_style.handle_size
        
        bar = self.factory.shape.make_rect(Vec2(), Vec2(dims.x - (dims.y - bar_width) - max_text_width, bar_width), bar_style)
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
        obj.set_constant_padding(round((dims.y - bar_width)*0.5))
        obj.fix_col_width(1, max_text_width)
        
        obj.add_object(bar, 1 if slider_style.text_position.lower() in ["left", "l"] else 0, 0, anchor=Anchor.C)
        obj.add_object(text, 0 if slider_style.text_position.lower() in ["left", "l"] else 1, 0, anchor=Anchor.C)
        
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
    
    def make_graph(
            self, position: Vec2, dims: Vec2, style: Optional[GraphStyle | str] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None, max_data_points=None, max_data_x_range=None, update_action=None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> GraphObject:
        
        graph_style = self._get_resource(style, GraphStyle)
        bg_style = graph_style.bg_style
        line_style = LineStyle(graph_style.line_color, graph_style.line_width)
        
        line = self.factory.shape.make_line(Vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
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


