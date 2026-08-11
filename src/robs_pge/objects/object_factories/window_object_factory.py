from typing import Any, Callable, Iterable, Optional, Type

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject, RectObject, TextObject, WindowObject, DebugInfoWindow
from ..object import PygameObject
from ...rendering import IconButtonStyle, RectRenderer, RectStyle, ScrollbarStyle, WindowStyle, Font
from ...resources import Icons
from ...utils import Anchor, StyleOrName, clamp, vec2


class WindowObjectFactory(SubObjectFactory):
    def __init__(self, object_factory):
        super().__init__(object_factory)
    
    def _title_panel(self, window_style: WindowStyle, title: str, layer: int, width: int) -> tuple[Optional[RectObject], Optional[TextObject], float]:
        title_object: Optional[TextObject] = None
        title_panel: Optional[RectObject] = None
        title_panel_height = 0
        
        if window_style.show_title:
            title_object = self.factory.text.label(vec2(), title, window_style.title_font, layer=layer)
            
            if not window_style.title_in_header and title_object is not None:
                title_panel_height = window_style.title_panel_height or (title_object.height + window_style.title_panel_margin)
                title_panel = self.factory.shape.rect(vec2(), vec2(width, title_panel_height), style=window_style.title_panel_style, layer=layer)
                
                title_offset = window_style.title_panel_margin * (vec2(1) - window_style.title_align * 2)
                title_object.pos = title_offset
                title_object.anchor = window_style.title_align
                title_panel.add_child(title_object, window_style.title_align)
        
        return title_panel, title_object, title_panel_height
    
    def _header_panel(self, window_style: WindowStyle, width: int, layer: int, title_object: Optional[TextObject], close_method) -> tuple[Optional[LayoutObject], float]:
        header = None
        header_height = 0
        
        if window_style.show_header:
            header_height = window_style.header_height
            if header_height is None:
                if title_object is not None and window_style.title_in_header:
                    header_height = title_object.height + window_style.header_margin
                else:
                    raise ValueError("Cannot determine header height when creating window. Must specify title or header height.")
            
            header_style = self._get_resource(window_style.header_style, RectStyle)
            header = self.factory.ui.layouts.grid_layout(vec2(), width, header_height, style=header_style, layer=layer)
            header.set_constant_padding(window_style.header_margin)
            
            buttons_width = (header_height - window_style.header_margin * 2) * 1.5
            header.set_column_fixed(0, width - buttons_width - window_style.header_margin * 2)
            
            if window_style.title_in_header and title_object is not None:
                title_offset = window_style.header_margin * (vec2(1) - window_style.title_align * 2)
                title_object.pos = title_offset
                title_object.anchor = window_style.title_align
                header.add(title_object, 0, 0, anchor=window_style.title_align)
            
            if window_style.show_header_buttons:
                icon_buttons_style = self._get_resource(window_style.icon_buttons_style, IconButtonStyle)
                button_dims = vec2(buttons_width, header_height - window_style.header_margin * 2)
                
                x_button = self.factory.ui.button.icon_button(
                    vec2(), Icons.XMARK, button_dims * 0.5, close_method, button_dims, style=icon_buttons_style, layer=layer
                )
                header.add(x_button, 1, 0)
        
        return header, header_height
    
    def _content_panel(self, window_style: WindowStyle, height: Optional[int], header_height: float, title_panel_height: float, width: int, layer: int):

        height = height or (header_height + title_panel_height)
        panel_width = width

        panel = self.factory.ui.layouts.grid_layout(vec2(), panel_width, None, layer=layer)
        panel.set_padding(window_style.margin)

        dims = vec2(width, height)

        return panel, dims, panel_width
    
    @staticmethod
    def _assemble_window(
            obj: WindowObject, header: Optional[LayoutObject], title_panel: Optional[RectObject],
            panel: LayoutObject, panel_width: float, draggable: bool
    ):
        
        row = 0
        if header is not None:
            obj.add(header, 0, row, span_x=2)
            row += 1
        if title_panel is not None:
            obj.add(title_panel, 0, row, span_x=2)
            row += 1
        
        obj.add(panel, 0, row)
        obj.set_column_fixed(0, panel_width)
        
        if draggable:
            drag_handle = header if header is not None else (title_panel if title_panel is not None else obj)
            drag_handle.make_draggable(1, target=obj)
        
        # endregion
    
    def create_window[WT: WindowObject](
            self, window_cls: type[WT], position: vec2, title: str, width: int,
            height: Optional[int] = None, draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C,
            cache: bool = True, *args: Any
    ) -> WT:
        window_style = self._get_resource(style, WindowStyle)
        
        title_panel, title_object, title_panel_height = self._title_panel(window_style, title, layer, width)
        header, header_height = self._header_panel(window_style, width, layer, title_object, lambda: obj.close())
        
        panel, dims, panel_width = self._content_panel(
            window_style, height, header_height, title_panel_height, width, layer
        )
        
        obj = self._create_object(
            window_cls, position, rotation, scale, RectRenderer(dims, window_style.bg_style, cache),
            layer, anchor, title, panel, header, title_panel, title_object, *args
        )
        
        self._assemble_window(obj, header, title_panel, panel, panel_width, draggable)
        obj.fix_width(width)

        return obj
    
    def regular(
            self, position: vec2, title: str, width: int, height: Optional[int] = None,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        
        return self.create_window(WindowObject, position, title, width, height, draggable, style, rotation, scale, layer, anchor, cache)
    