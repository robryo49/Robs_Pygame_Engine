from typing import Callable, Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject, ScrollbarObject
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, vec2, ObjectFlags


class WindowObject(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject, header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject],
                 services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)

        self._id = title.lower().replace(" ", "_")
        self._title = title

        self._content = content_panel
        self._header = header
        self._title_panel = title_panel
        self._title_object = title_object

    # region PROPERTIES

    @property
    def content(self) -> LayoutObject:
        return self._content

    @property
    def header(self) -> Optional[LayoutObject]:
        return self._header

    @property
    def title_panel(self) -> Optional[RectObject]:
        return self._title_panel

    @property
    def title_object(self) -> Optional[TextObject]:
        return self._title_object

    @property
    def title(self):
        return self._title

    @property
    def id(self):
        return self._id

    @property
    def opened(self):
        return not self.closed

    @property
    def closed(self):
        return self.has_flag(ObjectFlags.HIDDEN)

    def _update_self(self, dt: float):
        super()._update_self(dt)

    # endregion

    def open(self):
        self.show()

    def close(self):
        self.hide()

    def add_content(self, obj: PygameObject, x: int, y: int, anchor: vec2 = Anchor.C) -> "WindowObject":
        self.content.add(obj, x, y, anchor)
        return self

    def stack_content_x(self, obj: PygameObject, row: int = 0, anchor: vec2 = Anchor.C) -> "WindowObject":
        self.content.stack_x(obj, row, anchor)
        return self

    def stack_content_y(self, obj: PygameObject, col: int = 0, anchor: vec2 = Anchor.C) -> "WindowObject":
        self.content.stack_y(obj, col, anchor)
        return self

    def __repr__(self):
        return f"Window('{self.id}')"


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
    
    
        
    