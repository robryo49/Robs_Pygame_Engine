from typing import Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject, ScrollbarObject
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, Vec2, ObjectFlags


class WindowObject(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject, header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject], scrollbar: ScrollbarObject,
                 services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        
        self._id = title.lower().replace(" ", "_")
        self._title = title
        
        self._content = content_panel
        self._header = header
        self._title_panel = title_panel
        self._title_object = title_object
        
        self._scrollbar: ScrollbarObject = scrollbar
        
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
    def scrollbar(self) -> ScrollbarObject:
        return self._scrollbar
    
    def _update_self(self, dt: float):
        super()._update_self(dt)
        self._sync_scrollbar()
        
    def show_scrollbar(self):
        if self._scrollbar.visible:
            return
        
        scrollbar = self._scrollbar
        
        scrollbar.show()
        
        scrollbar_col_width = (
                scrollbar.width
                + self.content.parent.get_cell_padding((1, 0)).x * 2
        )
        
        self.fix_col_width(0, self.width - scrollbar_col_width)
        self.fix_col_width(1, scrollbar_col_width)
        
        self.content.fix_width(self.width - scrollbar_col_width)
        self.content.renderer.dims.x = self.width - scrollbar_col_width
        
        clip = self.content.children_clip_area
        clip.width = self.content.width - clip.x * 2
        
    def hide_scrollbar(self):
        if not self._scrollbar.visible:
            return
        
        scrollbar = self._scrollbar
        
        scrollbar.hide()
        scrollbar.value = 0.0
        self.content.scroll_offset = Vec2()
        
        self.fix_col_width(0, self.width)
        self.fix_col_width(1, 0)
        
        self.content.fix_width(self.width)
        self.content.renderer.dims.x = self.width
        
        clip = self.content.children_clip_area
        clip.width = self.content.width - clip.x * 2
    
    def _sync_scrollbar(self):
        max_offset = self.content.get_scroll_range_y()
        needed = max_offset > 0.5
        
        if needed:
            self.show_scrollbar()
        else:
            self.hide_scrollbar()
        
        if not self.scrollbar.visible:
            return
        
        viewport_height = self.content.get_viewport_height()
        content_height = viewport_height + max_offset
        
        ratio = viewport_height / content_height if content_height > 0 else 1.0
        self.scrollbar.handle_height = max(
            self.scrollbar.handle_width,
            viewport_height * ratio
        )
        
        self.scrollbar.update_movement_range()
    
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
        