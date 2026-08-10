from typing import Optional

from pygame import FRect

from .sub_factory import SubObjectFactory
from ..custom import LayoutObject, RectObject, TextObject, WindowObject
from ..object import PygameObject
from ...rendering import IconButtonStyle, RectRenderer, RectStyle, ScrollbarStyle, WindowStyle
from ...resources import Icons
from ...utils import Anchor, StyleOrName, clamp, vec2


class WindowObjectFactory(SubObjectFactory):
    def __init__(self, object_factory):
        super().__init__(object_factory)

    def regular(self, position: vec2, dims: vec2, title: str, draggable: bool = False, style: StyleOrName[WindowStyle] = None,
                rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True) -> WindowObject:
        
        window_style = self._get_resource(style, WindowStyle)
        bg_style = window_style.bg_style
        margin = window_style.margin
        
        # region TITLE
        
        title_object: Optional[TextObject] = None
        title_panel: Optional[RectObject] = None
        
        title_panel_height = 0
        if window_style.show_title:
            title_object: TextObject = self.factory.text.label(vec2(), title, window_style.title_font, layer=layer)
            
            if not window_style.title_in_header:
                title_panel_height = window_style.title_panel_height or (title_object.height + window_style.title_panel_margin)
                title_panel: RectObject = self.factory.shape.rect(vec2(), vec2(dims.x, title_panel_height), style=window_style.title_panel_style, layer=layer)
                
                title_offset = window_style.title_panel_margin * (vec2(1) - window_style.title_align * 2)
                title_object.pos = title_offset
                title_object.anchor = window_style.title_align
                title_panel.add_child(title_object, window_style.title_align)
        
        # endregion
        
        # region HEADER
        
        header: Optional[LayoutObject] = None
        
        if window_style.show_header:
            header_height = window_style.header_height
            if header_height is None:
                if title_object is not None and window_style.title_in_header:
                    header_height = title_object.height + window_style.header_margin
                else:
                    raise ValueError("cannot determine header height when creating window, must specify title or header height")
            
            header_style = self._get_resource(window_style.header_style, RectStyle)
            header: LayoutObject = self.factory.ui.layouts.grid_layout(vec2(), dims.x, header_height, style=header_style, layer=layer)
            header.set_constant_padding(window_style.header_margin)
            
            buttons_width = (header_height - window_style.header_margin * 2) * 1.5
            header.set_column_fixed(0, dims.x - buttons_width - window_style.header_margin * 2)
            
            if window_style.title_in_header and title_object is not None:
                title_offset = window_style.header_margin * (vec2(1) - window_style.title_align * 2)
                title_object.pos = title_offset
                title_object.anchor = window_style.title_align
                header.add(title_object, 0, 0, anchor=window_style.title_align)
            
            if window_style.show_header_buttons:
                icon_buttons_style = self._get_resource(window_style.icon_buttons_style, IconButtonStyle)
                button_dims = vec2(buttons_width, header_height - window_style.header_margin * 2)
                
                x_button = self.factory.ui.button.icon_button(
                    vec2(), Icons.XMARK, button_dims * 0.5, lambda: obj.close(), button_dims, style=icon_buttons_style, layer=layer
                )
                header.add(x_button, 1, 0)
        else:
            header_height = 0
        
        # endregion
        
        # region CONTENT PANEL + SCROLLBAR
        
        scrollbar_style = self._get_resource(window_style.scrollbar_style, ScrollbarStyle)
        scrollbar_col_width = window_style.scrollbar_width + window_style.scrollbar_edge_margin * 2
        
        panel_height = dims.y - title_panel_height - header_height
        panel_width = dims.x - scrollbar_col_width
        
        panel = self.factory.ui.layouts.grid_layout(vec2(), panel_width, panel_height, layer=layer)
        panel.set_outer_padding(margin)
        
        scrollbar = self.factory.ui.scrollbar(
            vec2(), vec2(window_style.scrollbar_width, panel_height - window_style.scrollbar_edge_margin * 2),
            scrollbar_style, layer=layer + 1
        )
        
        # endregion
        
        # region ASSEMBLY
        
        obj: WindowObject = self._create_object(
            WindowObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
            title, panel, header, title_panel, title_object, scrollbar
        )
        
        row = 0
        if header is not None:
            obj.add(header, 0, row, span_x=2)
            row += 1
        if title_panel is not None:
            obj.add(title_panel, 0, row, span_x=2)
            row += 1

        obj.add(panel, 0, row)
        obj.set_column_fixed(0, panel_width)

        obj.add(scrollbar, 1, row, anchor=Anchor.R)
        obj.set_column_fixed(1, scrollbar_col_width)
        obj.set_cell_padding(vec2(window_style.scrollbar_edge_margin, 0), (1, row))
        
        # endregion
        
        # region WIRING
        
        def _on_panel_scroll(o: PygameObject, scroll: int, pos: vec2):
            max_offset = panel.get_scroll_range_y()
            if max_offset > 0:
                scrollbar.set_value(clamp(scrollbar.value - scroll * 40 / max_offset, 0.0, 1.0))
        
        panel.do_on_scroll(_on_panel_scroll)
        panel.create_attribute_dynamic("scroll_offset", lambda: vec2(0, scrollbar.value * panel.get_scroll_range_y()), strength=0.2)
        
        if draggable:
            drag_handle = header if header is not None else (title_panel if title_panel is not None else obj)
            drag_handle.make_draggable(1, target=obj)
        
        obj.sync_scrollbar()
        
        # endregion
        
        return obj
