from .primitive_objects import LineObject, RectObject, CircleObject, TextObject
from .layout_objects import LayoutObject
from ..behaviors import *
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Easing, Transform, Vec2, clamp, inf, invert_y


class ButtonObject(RectObject):
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, action: Optional[Callable | tuple[Callable, ...]], services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        
        super().__init__(transform, background, services, layer, anchor)
        
        self._text = text
        
        self.add_child(self._text, Anchor.C)
        
        self.add_behavior([
            ScaleOnHoverBehavior(1.1, 0.1, Easing.EASE_OUT_QUAD),
            ScaleOnClickBehavior(1, 0.9, 0.1, Easing.EASE_OUT_QUAD)
        ])
        
        if action is not None:
            self.add_behavior(ActionOnClickBehavior(1, action))
    
    # region PROPERTIES
    
    @property
    def text(self):
        return self._text.text
    
    @text.setter
    def text(self, value):
        self._text.text = value
    
    # endregion
    

class ValueSwitchingButtonObject(ButtonObject):
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, texts: tuple[str, ...], values: tuple[Any, ...], callback: Optional[Callable | tuple[Callable, ...]], services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, background, text, None, services, layer, anchor)
        
        self._texts = texts
        self._values = values
        
        self._index = 0
        
        self.add_behavior([
            ActionOnClickBehavior(1, self.cycle_forward),
            ScaleOnClickBehavior(3, 0.9, 0.1, Easing.EASE_OUT_QUAD),
            ActionOnClickBehavior(3, self.cycle_backward)
        ])
        
        if callback is not None:
            self.add_behavior(ActionOnClickBehavior(1, callback))
        
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
        
        self._handle.add_behavior(DraggableBehavior(1))
        self._handle.add_behavior(AttributeFixingBehavior("y_pos"))
        self._handle.add_behavior(AttributeClampingBehavior("x_pos", -self._handle_movement_range*0.5, self._handle_movement_range*0.5))
        if step is not None:
            self._handle.add_behavior(AttributeGridSnappingBehavior("x_pos", step))
        
        self._text.add_behavior(DynamicAttributeBehavior("text", lambda: str(self.value)))
        
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
        return round(self.min_value + self.normalized_value * self.value_range)
        
    
    # endregion
    


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


class GraphObject(RectObject):
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
        self.add_child(line, Vec2(0.5, -0.5))
    
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
                        points.append(Vec2(self._pad_x + (point.x - min_x_value)*x_fac, self._pad_y + (point.y - min_y_value)*y_fac))
            
            self._line.points = points
            
            self._dirty = False

