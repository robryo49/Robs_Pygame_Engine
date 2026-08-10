from typing import Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject, ScrollbarObject
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, vec2, ObjectFlags


class WindowObject(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer,
                 title: str, content_panel: LayoutObject, header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject], scrollbar: ScrollbarObject,
                 services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)

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
        self.sync_scrollbar()

    def _apply_content_width(self, width: float):
        self.content.set_fixed_width(width)
        self.content.renderer.dims.x = width

        clip = self.content.children_clip_area
        if clip is not None:
            clip.width = width - clip.x * 2

    def _set_scrollbar_visible(self, visible: bool):
        if visible == self._scrollbar.visible:
            return

        if visible:
            self._scrollbar.show()
            scrollbar_col_width = self._scrollbar.width + self.content.spacing.x * 2
            content_width = self.width - scrollbar_col_width
        else:
            self._scrollbar.hide()
            self._scrollbar.value = 0.0
            self.content.scroll_offset = vec2()
            scrollbar_col_width = 0
            content_width = self.width

        self.set_column_fixed(0, content_width)
        self.set_column_fixed(1, scrollbar_col_width)
        self._apply_content_width(content_width)

    def show_scrollbar(self):
        self._set_scrollbar_visible(True)

    def hide_scrollbar(self):
        self._set_scrollbar_visible(False)

    def sync_scrollbar(self):

        max_offset = self.content.get_scroll_range_y()
        self._set_scrollbar_visible(max_offset > 0.5)

        if not self.scrollbar.visible:
            return

        viewport_height = self.content.get_viewport_height()
        content_height = viewport_height + max_offset
        ratio = viewport_height / content_height if content_height > 0 else 1.0

        self.scrollbar.handle_height = max(self.scrollbar.handle_width, viewport_height * ratio)

    # endregion

    def open(self):
        self.show()

    def close(self):
        self.hide()

    def add_content(self, obj: PygameObject, x: int, y: int, span_x: int = 1, span_y: int = 1, anchor: vec2 = Anchor.C):
        self.content.add(obj, x, y, span_x, span_y, anchor)
        return self

    def stack_content_x(self, obj: PygameObject, y: Optional[int] = None, span_y: Optional[int] = None, anchor: vec2 = Anchor.C):
        if y is not None:
            self.content.add(obj, 0, y, 1, span_y or 1, anchor)
        else:
            self.content.stack_x(obj, anchor=anchor)
        return self

    def stack_content_y(self, obj: PygameObject, x: Optional[int] = None, span_x: Optional[int] = None, anchor: vec2 = Anchor.C):
        if x is not None:
            self.content.add(obj, x, 0, span_x or 1, 1, anchor)
        else:
            self.content.stack_y(obj, anchor=anchor)
        return self

    def __repr__(self):
        return f"Window('{self.id}')"
