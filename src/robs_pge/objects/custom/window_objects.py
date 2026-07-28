from typing import Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject, ScrollbarObject
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, Vec2, ObjectFlags


class WindowObject(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject, header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject],
                 services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        
        self._id = title.lower().replace(" ", "_")
        self._title = title
        
        self._content = content_panel
        self._header = header
        self._title_panel = title_panel
        self._title_object = title_object
        
        self._scrollbar: Optional[ScrollbarObject] = None
        
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
    
    @property
    def scrollbar(self) -> Optional[ScrollbarObject]:
        return self._scrollbar
    
    def attach_scrollbar(self, scrollbar: ScrollbarObject):
        self._scrollbar = scrollbar
        scrollbar.hide()
        return self
    
    def _update_self(self, dt: float):
        super()._update_self(dt)
        self._sync_scrollbar()
    
    def _sync_scrollbar(self):
        scrollbar = self._scrollbar
        if scrollbar is None:
            return
        
        max_offset = self.content.get_scroll_range_y()
        needed = max_offset > 0.5
        
        if needed != scrollbar.visible:
            scrollbar.visible = needed
            if not needed:
                scrollbar.value = 0.0
                self.content.scroll_offset = Vec2()
        
        if needed:
            viewport_height = self.content.get_viewport_height()
            content_height = viewport_height + max_offset
            ratio = viewport_height / content_height if content_height > 0 else 1.0
            scrollbar.handle_height = max(scrollbar.handle_width, viewport_height * ratio)
    
    # endregion
    
    def open(self):
        self.show()
        
    def close(self):
        self.hide()
    
    def add_content(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: Vec2 = Anchor.C):
        self.content.add_object(obj, x, y, span_x, span_y, anchor)
        return self
        
    def stack_content_x(self, obj: PygameObject, y: Optional[int] = None, span_y: Optional[int] = None, anchor: Vec2 = Anchor.C):
        self.content.stack_x(obj, y, span_y, anchor)
        return self
    
    def stack_content_y(self, obj: PygameObject, x: Optional[int] = None, span_x: Optional[int] = None, anchor: Vec2 = Anchor.C):
        self.content.stack_y(obj, x, span_x, anchor)
        return self
        
    def __repr__(self):
        return f"Window('{self.id}')"
        