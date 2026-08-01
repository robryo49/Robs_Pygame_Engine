from typing import cast

from .primitive_objects import LineObject, RectObject, CircleObject, TextObject
from .sprite_objects import SpriteObject, IconObject
from .layout_objects import LayoutObject
from ..behaviors import *
from ...rendering import CircleRenderer, RectRenderer
from ...utils import Anchor, DictCollection, Easing, Transform, Vec2, clamp, inf, invert_y
from ...animation import SetterAnimation


class ButtonObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, action: Optional[Callable | tuple[Callable, ...]], services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        
        super().__init__(transform, background, services, layer, anchor)
        
        self._text: TextObject = text
        
        self.add_child(self._text, Anchor.C)
        
        self.do_on_click(1, action)
    
    # region PROPERTIES
    
    @property
    def text(self):
        return self._text.text
    
    @text.setter
    def text(self, value):
        self._text.text = value
        
    @property
    def font(self):
        return self._text.font
    
    # region font_color
    @property
    def font_color(self):
        return self.font.color
    
    @font_color.setter
    def font_color(self, value):
        self.font.color = value
    # endregion
    
    # endregion


class SpriteButtonObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, sprite: SpriteObject, action: Optional[Callable | tuple[Callable, ...]], services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        
        super().__init__(transform, background, services, layer, anchor)
        
        self._sprite = sprite
        
        self.add_child(self._sprite, Anchor.C)
        
        self.do_on_click(1, action)
    
    # region PROPERTIES
    
    @property
    def sprite(self) -> SpriteObject:
        return self._sprite
    
    # endregion
    

class IconButtonObject(SpriteButtonObject):
        
    # region PROPERTIES
    
    @property
    def sprite(self) -> IconObject:
        return cast(IconObject, self._sprite)
    
    # region icon
    @property
    def icon(self):
        return self.sprite.icon
    
    @icon.setter
    def icon(self, value):
        self.sprite.icon = value
    # endregion
    
    # region icon_color
    @property
    def icon_color(self):
        return self.sprite.icon_color
    
    @icon_color.setter
    def icon_color(self, value):
        self.sprite.icon_color = value
    # endregion
    
    # region icon_size
    @property
    def icon_size(self):
        return self.sprite.icon_size
    
    @icon_size.setter
    def icon_size(self, value):
        self.sprite.icon_size = value
    # endregion
    
    # endregion
    


class CycleButtonObject(ButtonObject):
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, texts: tuple[str, ...], values: tuple[Any, ...], callback: Optional[Callable[[Any], Any] | tuple[Callable[[Any], Any], ...]], services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, text, None, services, layer, anchor)
        
        self._texts = texts
        self._values = values
        
        self._index = 0
        
        self.do_on_click(1, self.cycle_forward)
        self.do_on_click(3, self.cycle_backward)
        
        if callback is not None:
            self.do_on_click(1, lambda: callback(self.value))
            self.do_on_click(3, lambda: callback(self.value))
    
    
    # region PROPERTIES
    
    @property
    def texts(self):
        return self._texts
    
    @property
    def values(self):
        return self._values
    
    @property
    def value(self):
        return self._values[self._index]
    
    # region index
    @property
    def index(self):
        return self._index
    
    @index.setter
    def index(self, value: int):
        self._index = value % len(self._texts)
        self.text = self.texts[self._index]
        
    def cycle_forward(self, amount: int = 1):
        self.index += amount
        
    def cycle_backward(self, amount: int = 1):
        self.index -= amount
    
    # endregion
    
    # endregion


class CheckBoxObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, checked_icon: IconObject, callback: Optional[Callable[[bool], Any] | tuple[Callable[[bool], Any], ...]],
                 services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._checked_icon = checked_icon
        self.add_child(self._checked_icon)
        self._checked_icon.hide()
        
        self.do_on_click(1, self.toggle)
        if callback is not None:
            self.do_on_click(1, lambda: callback(self.checked))
        
    # region PROPERTIES
    
    @property
    def checked(self):
        return self._checked_icon.visible
    
    @property
    def unchecked(self):
        return not self.checked
    
    # endregion
    
    def toggle(self):
        self._checked_icon.toggle_visible()
    
    def check(self):
        self._checked_icon.show()
    
    def uncheck(self):
        self._checked_icon.hide()


class RadioButtonObject(CircleObject):
    def __init__(self, transform: Transform, background: CircleRenderer, tick: CircleObject, callback: Optional[Callable[[bool], Any] | tuple[Callable[[bool], Any], ...]],
                services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._tick = tick
        self.add_child(self._tick)
        self._tick.hide()
        
        self.do_on_click(1, self.toggle)
        if callback is not None:
            self.do_on_click(1, lambda: callback(self.checked))
    
    # region PROPERTIES
    
    @property
    def checked(self):
        return self._tick.visible
    
    @property
    def unchecked(self):
        return not self.checked
    
    # endregion
    
    def toggle(self):
        self._tick.toggle_visible()
    
    def check(self):
        self._tick.show()
    
    def uncheck(self):
        self._tick.hide()
        

class ToggleButtonObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, toggle: RectObject, toggle_background: RectObject, toggle_movement_range: tuple[int, int], callback: Optional[Callable[[bool], Any] | tuple[Callable[[bool], Any], ...]],
                 services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._toggle_min_x = toggle_movement_range[0]
        self._toggle_max_x = toggle_movement_range[1]
        self._toggle_movement_range = self._toggle_max_x - self._toggle_min_x
        
        self._toggle = toggle
        self._toggle_background = toggle_background
        
        self._enabled = False
        
        self.add_child(toggle_background, Anchor.L)
        self.add_child(toggle, Anchor.L)
        
        toggle.anchor = Anchor.L
        toggle_background.anchor = Anchor.L
        
        self.do_on_click(1, self.toggle)
        
        self._toggle_background.make_attribute_dynamic("width", lambda: self._toggle.x_pos + self._toggle.width * 0.5)
        self.do_on_click(1, lambda: callback(self.enabled))
    
    # region PROPERTIES
    
    @property
    def enabled(self):
        return self._enabled
    
    @property
    def disabled(self):
        return not self.enabled
    
    # endregion
    
    def toggle(self):
        if self._enabled:
            self.disable()
        else:
            self.enable()
    
    def enable(self):
        self._enabled = True
        self._toggle.play_animation(
            SetterAnimation(self._toggle, "x_pos", self._toggle_max_x, 0.07, Easing.EASE_IN_QUAD, start_value=self._toggle_min_x)
        )
    
    def disable(self):
        self._enabled = False
        self._toggle.play_animation(
            SetterAnimation(self._toggle, "x_pos", self._toggle_min_x, 0.07, Easing.EASE_IN_QUAD, start_value=self._toggle_max_x)
        )
        
    


class SliderObject(LayoutObject):
    def __init__(self, transform: Transform, background: RectRenderer, bar: RectObject, handle: RectObject | CircleObject, text: TextObject, min_value: float, max_value: float, step: Optional[float],
                 services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        
        self._bar = bar
        self._handle = handle
        self._text = text
        
        self._handle_movement_range = self._bar.width - self._bar.height
        
        if step is not None:
            step = self._handle_movement_range * step / (max_value - min_value)
        
        self._handle.make_draggable(1)
        self._handle.make_attribute_fixed("y_pos")
        self._handle.make_attribute_clamped("x_pos", -self._handle_movement_range*0.5, self._handle_movement_range*0.5)
        if step is not None:
            self._handle.make_attribute_snap_on_grid("x_pos", step, self._handle_movement_range*0.5)
        
        self._text.make_attribute_dynamic("text", lambda: str(self.value))
        
        self._bar.add_child(self._handle, Anchor.C)
        
    # region PROPERTIES
    
    @property
    def min_value(self):
        return self._min_value
    
    @property
    def max_value(self):
        return self._max_value
    
    @property
    def step(self):
        return self._step
    
    @property
    def value_range(self):
        return self.max_value - self.min_value
    
    @property
    def normalized_value(self):
        return (self._handle.x_pos+self._handle_movement_range*0.5) / self._handle_movement_range
    
    @property
    def value(self):
        return round(self.min_value + self.normalized_value * self.value_range, 2)
    
    @value.setter
    def value(self, value):
        value = clamp(value, self.min_value, self.max_value)
        normalized_value = (value - self.min_value) / self.value_range
        self._handle.x_pos = (normalized_value - 0.5) * self._handle_movement_range
        
    
    # endregion
    
    def _update_self(self, dt: float):
        super()._update_self(dt)


class ProgressBarObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, bar: RectObject, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._value = 0.0
        self._max_value = 1.0
        
        self._progress = 0.0
        
        self._dirty = True
        
        self._bar = bar
        self._bar.anchor = Anchor.TL
        self._bar.pos = invert_y(Vec2(self.bd))
        self.add_child(bar, Anchor.TL)
    
    # region PROPERTIES
    
    # region color
    @property
    def color(self):
        return self._bar.bg_color
    
    @color.setter
    def color(self, value):
        self._bar.bg_color = value
    # endregion
    
    # region value
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = clamp(value, 0, self.max_value)
        self._progress = self._value / self._max_value
        self.mark_dirty()
    # endregion
    
    # region max_value
    @property
    def max_value(self):
        return self._max_value
    
    @max_value.setter
    def max_value(self, value):
        self._max_value = value
        self._value = min(self._value, self._max_value)
        self._progress = self._value / value
        self.mark_dirty()
    # endregion
    
    # region progress
    @property
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = clamp(value)
        self._value = self._progress * self._max_value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def mark_dirty(self):
        self._dirty = True
    
    def _update_self(self, dt: float):
        super()._update_self(dt)
        
        if self._dirty:
            self._bar.width = round((self.width - self.bd*2) * self.progress)
            self._dirty = False


class ScrollbarObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, handle: RectObject,
                 services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._handle = handle
        self._handle_movement_range = 0
        self._min_y = 0
        self._max_y = 0
        
        self.add_child(self._handle, Anchor.C)
        
        self._handle.make_draggable(1)
        self._handle.make_attribute_fixed("x_pos")
        
        self.update_movement_range()
        
        self._handle.make_attribute_clamped("y_pos", lambda: self._min_y, lambda: self._max_y)
    
    # region PROPERTIES
    
    @property
    def handle_width(self):
        return self._handle.width
    
    @property
    def handle_height(self) -> float:
        return self._handle.height
    
    @handle_height.setter
    def handle_height(self, value: float):
        self._handle.height = clamp(value, 5.0, self.height)
        self.update_movement_range()
        
        self.value = self.value
    
    @property
    def normalized_value(self) -> float:
        if self._handle_movement_range == 0:
            return 0.0
        return 0.5 + self._handle.y_pos / self._handle_movement_range
    
    @property
    def value(self) -> float:
        return clamp(self.normalized_value, 0.0, 1.0)
    
    @value.setter
    def value(self, value: float):
        value = clamp(value, 0.0, 1.0)
        self._handle.y_pos = (value - 0.5) * self._handle_movement_range
        
    def set_value(self, value: float):
        self.value = value
    
    # endregion
    
    @property
    def handle_movement_range(self):
        return self._handle_movement_range
    
    def update_movement_range(self):
        margin = (self.width - self._handle.width) * 0.5
        self._handle_movement_range = self.height - self._handle.height - margin * 2
        
        self._min_y = -self._handle_movement_range * 0.5
        self._max_y = self._handle_movement_range * 0.5


class LineChartObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, line: LineObject, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, services, layer, anchor)
        
        self._pad_x = 0
        self._pad_y = 0
        
        self._min_x_value = None
        self._max_x_value = None
        
        self._min_y_value = None
        self._max_y_value = None
        
        self._min_data_x = inf
        self._max_data_x = 0.0
        
        self._min_data_y = inf
        self._max_data_y = 0.0
        
        self._data_points = []
        self._max_data_points = None
        self._max_data_x_range = None
        
        self._dirty = True
        
        self._line = line
        self.add_child(line, Anchor.TL)
    
    # region PROPERTIES
    
    # region color
    @property
    def color(self):
        return self._line.color
    
    @color.setter
    def color(self, value):
        self._line.color = value
    # endregion
    
    # region min_x_value
    @property
    def min_x_value(self):
        return self._min_x_value
    
    @min_x_value.setter
    def min_x_value(self, value):
        self._min_x_value = value
    # endregion
    
    # region max_x_value
    @property
    def max_x_value(self):
        return self._max_x_value
    
    @max_x_value.setter
    def max_x_value(self, value):
        self._max_x_value = value
    # endregion
    
    # region min_y_value
    @property
    def min_y_value(self):
        return self._min_y_value
    
    @min_y_value.setter
    def min_y_value(self, value):
        self._min_y_value = value
    # endregion
    
    # region max_y_value
    @property
    def max_y_value(self):
        return self._max_y_value
    
    @max_y_value.setter
    def max_y_value(self, value):
        self._max_y_value = value
    # endregion
    
    # region pad_x
    @property
    def pad_x(self):
        return self._pad_x
    
    @pad_x.setter
    def pad_x(self, value):
        self._pad_x = value
    # endregion
    
    # region pad_y
    @property
    def pad_y(self):
        return self._pad_y
    
    @pad_y.setter
    def pad_y(self, value):
        self._pad_y = value
    # endregion
    
    # region max_data_points
    @property
    def max_data_points(self):
        return self._max_data_points
    
    @max_data_points.setter
    def max_data_points(self, value):
        self._max_data_points = value
    # endregion
    
    # region max_data_x_range
    @property
    def max_data_x_range(self):
        return self._max_data_x_range
    
    @max_data_x_range.setter
    def max_data_x_range(self, value):
        self._max_data_x_range = value
    # endregion
    
    # endregion
    
    def insert_point(self, point: Vec2):
        
        i = 0
        n = len(self._data_points)
        for i in range(n):
            p = self._data_points[n-i-1]
            if p.x < point.x:
                break
        
        self._data_points.insert(n-i, point)
        
        if self._max_data_points and len(self._data_points) > self._max_data_points:
            self.remove_last()
        
        self._min_data_x = min(self._min_data_x, point.x)
        self._max_data_x = max(self._max_data_x, point.x)
        
        self._min_data_y = min(self._min_data_y, point.y)
        self._max_data_y = max(self._max_data_y, point.y)
        
        if self._max_data_x_range and abs(self._max_data_x - self._min_data_x) > self._max_data_x_range:
            self.remove_last()
        
        self.mark_dirty()
    
    def _update_data_range_from_removed_point(self, point: Vec2):
        if point.x == self._min_data_x:
            self._min_data_x = min(p.x for p in self._data_points) if self._data_points else 0
        if point.x == self._max_data_x:
            self._max_data_x = max(p.x for p in self._data_points) if self._data_points else 0
        
        if point.y == self._min_data_y:
            self._min_data_y = min(p.y for p in self._data_points) if self._data_points else 0
        if point.y == self._max_data_y:
            self._max_data_y = max(p.y for p in self._data_points) if self._data_points else 0
    
    
    def remove_point(self, point: Vec2):
        self._data_points.remove(point)
        self._update_data_range_from_removed_point(point)
        self.mark_dirty()
    
    
    def remove_last(self):
        point = self._data_points.pop(0)
        self._update_data_range_from_removed_point(point)
        
        self.mark_dirty()
    
    def mark_dirty(self):
        self._dirty = True
    
    def _update_self(self, dt: float):
        super()._update_self(dt)
        
        if self._dirty:
            points = []
            
            if self._data_points:
                min_x_value = self._min_x_value if self._min_x_value is not None else self._min_data_x
                max_x_value = self._max_x_value if self._max_x_value is not None else self._max_data_x
                min_y_value = self._min_y_value if self._min_y_value is not None else self._min_data_y
                max_y_value = self._max_y_value if self._max_y_value is not None else self._max_data_y
                
                width = max_x_value - min_x_value
                height = max_y_value - min_y_value
                
                x_fac = (self.width - 2*self._pad_x)/width if width else 0
                y_fac = (self.height - 2*self._pad_y)/height if height else 0
                
                for point in self._data_points:
                    if min_x_value <= point.x <= max_x_value and min_y_value <= point.y <= max_y_value:
                        points.append(Vec2(
                            self._pad_x + (point.x - min_x_value) * x_fac,
                            (self.height - self._pad_y) - (point.y - min_y_value) * y_fac
                        ))
            
            self._line.points = points
            
            self._dirty = False

