from typing import Callable, Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject
from .window_objects import WindowObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, vec2


class DebugOverlay(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    def toggle(self) -> LayoutObject:
        self.visible = not self.visible
        return self
    
    def __repr__(self) -> str:
        return f"DebugOverlay({id(self)})"
    

class DebugInfoWindow(WindowObject):
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject,
                 header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject],
                 title_factory_method, value_factory_method,
                 services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, title, content_panel, header, title_panel, title_object, services, sub_layer, anchor)
        
        self._title_factory = title_factory_method
        self._value_factory = value_factory_method
    
    def add_line(self, title: str, template: str, getter: Callable):
        title = self._title_factory(title)
        value = self._value_factory(template, getter)
        
        self.stack_content_y(title, 0, anchor=Anchor.TL)
        self.stack_content_y(value, 1, anchor=Anchor.TL)
    
    def add_line_break(self):
        title = self._title_factory(" ")
        value = self._title_factory(" ")
        
        self.stack_content_y(title, 0, anchor=Anchor.TL)
        self.stack_content_y(value, 1, anchor=Anchor.TL)