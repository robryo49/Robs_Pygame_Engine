from typing import Any, Optional

from .button_object_factory import ButtonObjectFactory
from .debug_object_factory import DebugObjectFactory
from .layout_object_factory import LayoutObjectFactory
from .sub_factory import SubObjectFactory
from ..custom import LineChartObject, ProgressBarObject, ScrollbarObject, SliderObject, ValueSelectorObject, ValueCyclerObject
from ..object import PygameObject
from ...rendering import CircleStyle, LineChartStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, ScrollbarStyle, SliderStyle, ValueSelectorStyle, ValueCyclerStyle
from ...resources import Icons
from ...utils import Anchor, StyleOrName, length, vec2, Callback, Font, inf, clamp


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
    
    def value_selector(
            self, position: vec2, dims: vec2, start_value: float = 0, min_value: float = 0, max_value: float = inf,
            increments: Optional[list[float] | tuple[float, ...]] = None, callback: Callback[[float], Any] = None,
            style: StyleOrName[ValueSelectorStyle] = None, rotation: float = 0.0, scale: float = 1.0,
            layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ValueSelectorObject:
        selector_style = self._get_resource(style, ValueSelectorStyle)
        bg_style = selector_style.bg_style
        button_style = selector_style.button_style
        font = self._get_resource(selector_style.font, Font)
        margin = selector_style.margin
        
        incs = tuple(increments if increments is not None else (1,))
        for inc in incs:
            if inc <= 0:
                raise ValueError("ValueSelector increments must be positive")
                
        dec_buttons = []
        for inc in reversed(incs):
            v_inc = int(inc) if inc == int(inc) else inc
            btn = self.button.button(vec2(), f"-{v_inc}", style=button_style, layer=layer, cache=cache)
            dec_buttons.append((btn, inc))
            
        start_val = clamp(start_value, min_value, max_value)
        text = self.factory.text.label(vec2(), str(start_val), font, layer=layer, cache=cache)
        
        inc_buttons = []
        for inc in incs:
            v_inc = int(inc) if inc == int(inc) else inc
            btn = self.button.button(vec2(), f"+{v_inc}", style=button_style, layer=layer, cache=cache)
            inc_buttons.append((btn, inc))
            
        obj = self._create_object(
            ValueSelectorObject, position, rotation, scale, RectRenderer(dims, bg_style, cache),
            layer, anchor, text, min_value, max_value, incs, start_val, callback
        )
        
        for btn, inc in dec_buttons:
            btn.do_on_click(1, lambda _, i=inc: obj.decrement(i))
        for btn, inc in inc_buttons:
            btn.do_on_click(1, lambda _, i=inc: obj.increment(i))
            
        col_idx = 0
        for btn, _ in dec_buttons:
            obj.add(btn, col_idx, 0)
            col_idx += 1
            
        value_col_idx = col_idx
        obj.add(text, value_col_idx, 0)
        col_idx += 1
        
        for btn, _ in inc_buttons:
            obj.add(btn, col_idx, 0)
            col_idx += 1
            
        obj.set_fixed_width(dims.x).set_fixed_height(dims.y)
        obj.set_cell_spacing(margin, True)
        
        if selector_style.value_width is not None:
            obj.set_fixed_col_width(selector_style.value_width, value_col_idx)
        else:
            if max_value != inf:
                val_w = font.get_render_size(str(max_value))[0]
            else:
                val_w = font.get_render_size(str(start_val))[0]
            obj.set_min_col_width(val_w, value_col_idx)
            
        if selector_style.hide_bg:
            obj.skip_rendering()
            
        return obj
        
    def value_cycler(
            self, position: vec2, dims: vec2, values: tuple[Any, ...] | list[Any], default_index: int = 0,
            callback: Callback[[Any], Any] = None, style: StyleOrName[ValueCyclerStyle] = None,
            previous_icon: str = Icons.CHEVRON_LEFT, next_icon: str = Icons.CHEVRON_RIGHT,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ValueCyclerObject:
        vals = tuple(values)
        if not vals:
            raise ValueError("ValueCycler requires at least one value")
        if not (0 <= default_index < len(vals)):
            raise ValueError(f"Default index {default_index} out of range for values of length {len(vals)}")
            
        cycler_style = self._get_resource(style, ValueCyclerStyle)
        bg_style = cycler_style.bg_style
        icon_btn_style = cycler_style.icon_button_style
        font = self._get_resource(cycler_style.font, Font)
        margin = cycler_style.margin
        icon_size = cycler_style.icon_size
        
        prev_btn = self.button.icon_button(vec2(), previous_icon, icon_size, style=icon_btn_style, layer=layer, cache=cache)
        next_btn = self.button.icon_button(vec2(), next_icon, icon_size, style=icon_btn_style, layer=layer, cache=cache)
        
        default_val = vals[default_index]
        text = self.factory.text.label(vec2(), str(default_val), font, layer=layer, cache=cache)
        
        obj = self._create_object(
            ValueCyclerObject, position, rotation, scale, RectRenderer(dims, bg_style, cache),
            layer, anchor, text, vals, default_index, callback
        )
        
        prev_btn.do_on_click(1, lambda _: obj.cycle_backward())
        next_btn.do_on_click(1, lambda _: obj.cycle_forward())
        
        obj.add(prev_btn, 0, 0)
        obj.add(text, 1, 0)
        obj.add(next_btn, 2, 0)
        
        obj.set_fixed_width(dims.x).set_fixed_height(dims.y)
        obj.set_cell_spacing(margin, True)
        
        if cycler_style.value_width is not None:
            obj.set_fixed_col_width(cycler_style.value_width, 1)
        else:
            max_val_str = max((str(v) for v in vals), key=len)
            val_w = font.get_render_size(max_val_str)[0]
            obj.set_min_col_width(val_w, 1)
            
        if cycler_style.hide_bg:
            obj.skip_rendering()
            
        return obj
    
