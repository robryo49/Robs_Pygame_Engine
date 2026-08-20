from typing import Any, Callable, Optional

from .sub_factory import SubObjectFactory
from ..object import PygameObject
from ..custom import LayoutObject, TextObject, WindowObject
from ...rendering import RectRenderer, RectStyle, WindowStyle, ButtonStyle
from ...resources import Icons
from ...utils import Anchor, Font, StyleOrName, vec2, Callback


class WindowObjectFactory(SubObjectFactory):
    def __init__(self, object_factory):
        super().__init__(object_factory)
        
    def create_window[WT](
            self, window_cls: type[WT], position: vec2, title: str, width: int, height: Optional[int] = None,
            mode: WindowObject.Mode = WindowObject.GRID_MODE, fit_mode: WindowObject.FitMode = WindowObject.STRETCH_MODE,
            overflow_mode: WindowObject.FitMode = WindowObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, *args: Any
    ) -> WT:
        
        window_style = self._get_resource(style, WindowStyle)
        bg_style = self._get_resource(window_style.bg_style, RectStyle)
        header_style = self._get_resource(window_style.header_style, RectStyle)
        title_panel_style = self._get_resource(window_style.title_panel_style, RectStyle)
        title_font = self._get_resource(window_style.title_font, Font)
        
        margin = window_style.margin
        
        show_header = window_style.show_header
        header_height = window_style.header_height
        header_margin = window_style.header_margin
        show_header_buttons = window_style.show_header_buttons
        icon_buttons_style = window_style.icon_buttons_style
        
        show_title = window_style.show_title
        title_panel_height = window_style.title_panel_height
        title_panel_margin = window_style.title_panel_margin
        title_align = window_style.title_align
        title_in_header = window_style.title_in_header
        
        scrollbar_style = window_style.scrollbar_style
        scrollbar_width = window_style.scrollbar_width
        scrollbar_edge_margin = window_style.scrollbar_edge_margin
        
        window: WindowObject
        header: Optional[LayoutObject] = None
        title_panel: Optional[LayoutObject] = None
        title_object: Optional[TextObject] = None
        
        if show_title:
            title_object = self.factory.text.label(vec2(), title, title_font, layer=layer)
        
        if show_header:
            header: LayoutObject = self.factory.ui.layouts.grid_layout(vec2(), width, header_height, justification=Anchor.R, style=header_style, layer=layer)
            
        if title_object is not None and not title_in_header:
            title_panel: LayoutObject = self.factory.ui.layouts.grid_layout(vec2(), width, title_panel_height, style=title_panel_style, layer=layer)
            title_panel.add(title_object, 0, 0, anchor=title_align)
            title_panel.set_outer_padding(title_panel_margin)
            
        if title_object is not None and header is not None and title_in_header:
            header.add(title_object, 0, 0, anchor=title_align)
            header.set_outer_padding(header_margin)
        
        if header is not None and show_header_buttons:
            buttons_dims = vec2(1.2, 1) * (header_height - header_margin * 2)
            
            header.add(self.factory.ui.button.icon_button(vec2(), Icons.XMARK, header_height*0.8, lambda: window.close, buttons_dims, style=icon_buttons_style), 1, 0, anchor=Anchor.R)
            header.set_fixed_col_width(round(buttons_dims.x + header_margin * 2), 1)
        
        
        content_panel_height = None if height is None else (height - (title_panel_height or 0) - (header_height or 0))
        content_panel = self.factory.ui.layouts.grid_layout(vec2(), width, content_panel_height, mode, fit_mode, overflow_mode, justification, layer=layer)
        content_panel.set_outer_padding(margin)
        
        window = self._create_object(
            window_cls, position, rotation, scale, RectRenderer(vec2(), bg_style, cache),
            layer, anchor, title, content_panel, header, title_panel, title_object, *args
        )
        
        if header is not None:
            window.stack_y(header, 0)
        if title_panel is not None:
            window.stack_y(title_panel, 0)
        window.stack_y(content_panel)
        
        if draggable:
            if header is not None:
                header.make_draggable(target=window)
            elif title_panel is not None:
                title_panel.make_draggable(target=window)
            else:
                content_panel.make_draggable(target=window)
            
        return window
    
    def regular(
            self, position: vec2, title: str, width: int, height: Optional[int] = None,
            mode: WindowObject.Mode = WindowObject.GRID_MODE, fit_mode: WindowObject.FitMode = WindowObject.STRETCH_MODE,
            overflow_mode: WindowObject.FitMode = WindowObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        
        return self.create_window(WindowObject, position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, style, rotation, scale, layer, anchor, cache)
    
    
    def with_content(
            self, position: vec2, title: str, width: int, height: Optional[int] = None, content: Optional[LayoutObject] = None,
            mode: WindowObject.Mode = WindowObject.GRID_MODE, fit_mode: WindowObject.FitMode = WindowObject.STRETCH_MODE,
            overflow_mode: WindowObject.FitMode = WindowObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        window = self.regular(position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, style, rotation, scale, layer, anchor, cache)
        
        if content is not None:
            window.content = content
        
        return window
    
    def menu(
        self, position: vec2, title: str, options: list[tuple[str, Callback[[PygameObject], Any]]], button_dims: vec2, width: int, height: Optional[int] = None,
        mode: WindowObject.Mode = WindowObject.GRID_MODE, fit_mode: WindowObject.FitMode = WindowObject.STRETCH_MODE,
        overflow_mode: WindowObject.FitMode = WindowObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
        draggable: bool = False, window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None,
        rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        
        window = self.regular(position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, window_style, rotation, scale, layer, anchor, cache)
        
        button_style = self._get_resource(button_style, ButtonStyle)
        
        for name, action in options:
            window.content.stack_y(self.factory.ui.button.button(vec2(), name, action, button_dims, style=button_style))
        
        return window
    