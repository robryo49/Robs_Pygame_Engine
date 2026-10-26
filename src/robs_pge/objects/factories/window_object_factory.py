"""
Factories for creating windows, menus, and dialogs.
"""

import time
from typing import Any, Optional

from .sub_object_factory import SubObjectFactory
from ..custom import LayoutObject, TextObject, WindowObject, FitMode, LayoutMode
from ..object import PygameObject
from ..object_flags import ObjectFlags
from ...rendering import ButtonStyle, RectRenderer, RectStyle, WindowStyle
from ...resources import Icons
from ...utils import Anchor, Callback, Font, StyleOrName, vec2


class WindowObjectFactory(SubObjectFactory):
    """
    Create window objects, including content windows, menus, and dialogs.
    """

    def create_window[WT](
            self, window_cls: type[WT], position: vec2, title: Optional[str], width: int, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, *args: Any
    ) -> WT:
        """
        Create a window with optional header, title panel, content panel, and scrollbar.

        :param window_cls: Window class to instantiate.
        :param position: World-space position of the object.
        :param title: Window title; generated from the current time when omitted.
        :param width: Fixed width of the window.
        :param height: Fixed height of the window; content height is derived when omitted.
        :param mode: Layout mode for the content panel.
        :param fit_mode: Fit mode used to size content cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the content panel.
        :param draggable: Whether the window can be dragged by its header, title panel, or content.
        :param style: Window style or registered window style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :param args: Additional positional arguments passed to the window constructor.
        :return: The created window object.
        """

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

        if title is None:
            title = str(hash(time.time()))

        if show_title:
            title_object = self._factory.text.label(vec2(), title, title_font, layer=layer)

        if show_header:
            header: LayoutObject = self._factory.layout.grid_layout(vec2(), width, header_height, justification=Anchor.R, style=header_style, layer=layer)

        if title_object is not None and not title_in_header:
            title_panel: LayoutObject = self._factory.layout.grid_layout(vec2(), width, title_panel_height, style=title_panel_style, layer=layer)
            title_panel.set_object_in_cell(title_object, 0, 0, anchor=title_align)
            title_panel.set_padding(title_panel_margin)

        if title_object is not None and header is not None and title_in_header:
            header.set_object_in_cell(title_object, 0, 0, anchor=title_align)
            header.set_padding(header_margin)

        if header is not None and show_header_buttons:
            buttons_dims = vec2(1.2, 1) * (header_height - header_margin * 2)

            header.set_object_in_cell(self._factory.ui.icon_button(vec2(), Icons.XMARK, round(header_height * 0.8), lambda o: window.close(), buttons_dims, style=icon_buttons_style), 1, 0, anchor=Anchor.R)
            header.set_fixed_col_width(round(buttons_dims.x + header_margin * 2), 1)


        content_panel_height = None if height is None else (
                height - (title_panel_height if title_panel is not None else 0) - (header_height if header is not None else 0)
        )
        content_panel = self._factory.layout.grid_layout(vec2(), width, content_panel_height, mode, fit_mode, overflow_mode, justification, layer=layer)
        content_panel.set_padding(margin)

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

        window.add_flag(ObjectFlags.HOVERABLE)

        return window

    def regular(
            self, position: vec2, title: Optional[str], width: int, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        """
        Create a standard window with the configured header, title, and content panel.

        :param position: World-space position of the object.
        :param title: Window title; generated from the current time when omitted.
        :param width: Fixed width of the window.
        :param height: Fixed height of the window; content height is derived when omitted.
        :param mode: Layout mode for the content panel.
        :param fit_mode: Fit mode used to size content cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the content panel.
        :param draggable: Whether the window can be dragged by its header, title panel, or content.
        :param style: Window style or registered window style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created window object.
        """

        return self.create_window(WindowObject, position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, style, rotation, scale, layer, anchor, cache)


    def with_content(
            self, position: vec2, title: Optional[str], width: int, height: Optional[int] = None, content: Optional[LayoutObject] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        """
        Create a standard window and replace its content panel with the given layout.

        :param position: World-space position of the object.
        :param title: Window title; generated from the current time when omitted.
        :param width: Fixed width of the window.
        :param height: Fixed height of the window; content height is derived when omitted.
        :param content: Layout object used as the window content.
        :param mode: Layout mode for the content panel.
        :param fit_mode: Fit mode used to size content cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the content panel.
        :param draggable: Whether the window can be dragged by its header, title panel, or content.
        :param style: Window style or registered window style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created window object.
        """
        window = self.regular(position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, style, rotation, scale, layer, anchor, cache)

        if content is not None:
            window.content = content

        return window

    def menu(
            self, position: vec2, title: Optional[str], options: list[tuple[str, Callback[[PygameObject], Any]]], button_dims: vec2, width: int, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        """
        Create a window whose content is a vertical list of menu option buttons.

        :param position: World-space position of the object.
        :param title: Window title; generated from the current time when omitted.
        :param options: Pairs of button labels and click callbacks.
        :param button_dims: Dimensions of each menu button.
        :param width: Fixed width of the window.
        :param height: Fixed height of the window; content height is derived when omitted.
        :param mode: Layout mode for the content panel.
        :param fit_mode: Fit mode used to size content cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the content panel.
        :param draggable: Whether the window can be dragged by its header, title panel, or content.
        :param window_style: Window style or registered window style name.
        :param button_style: Button style or registered button style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created menu window.
        """

        window = self.regular(position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, window_style, rotation, scale, layer, anchor, cache)

        button_style = self._get_resource(button_style, ButtonStyle)

        for name, action in options:
            window.content.stack_y(self._factory.ui.button(vec2(), name, action, button_dims, style=button_style))

        return window


    def dialog(
            self, position: vec2, content: PygameObject, options: list[tuple[str, Callback[[PygameObject], Any]]], width: int, height: Optional[int] = None,
            buttons_height: int = 30, options_vertical: bool = False, spacing: int = 20,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ):
        """
        Create a window containing arbitrary content and a row or column of option buttons.

        :param position: World-space position of the object.
        :param content: Object placed above the dialog options.
        :param options: Pairs of button labels and click callbacks.
        :param width: Fixed width of the window.
        :param height: Fixed height of the window; content height is derived when omitted.
        :param buttons_height: Height of each dialog button.
        :param options_vertical: Whether the option buttons are stacked vertically.
        :param spacing: Spacing between content and option buttons.
        :param mode: Layout mode for the content panel.
        :param fit_mode: Fit mode used to size content cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the content panel.
        :param draggable: Whether the window can be dragged by its header, title panel, or content.
        :param window_style: Window style or registered window style name.
        :param button_style: Button style or registered button style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created dialog window.
        """
        window = self.regular(position, None, width, height, mode, fit_mode, overflow_mode, justification, draggable, window_style, rotation, scale, layer, anchor, cache)

        button_style = self._get_resource(button_style, ButtonStyle)

        if options_vertical:
            window.content.stack_y(content)
            buttons_width = width - 2*spacing
            for row, (txt, callback) in enumerate(options):
                window.content.stack_y(self._factory.ui.button(vec2(), txt, callback, vec2(buttons_width, buttons_height), style=button_style))
                window.content.set_vertical_fit_mode(window.PRESERVE_MODE, row+1)
        else:
            n = len(options)
            window.content.stack_y(content, span_x=n)
            buttons_width = (width - (n+1) * spacing) / n
            for row, (txt, callback) in enumerate(options):
                window.content.stack_x(self._factory.ui.button(vec2(), txt, callback, vec2(buttons_width, buttons_height), style=button_style), y=1)
                window.content.set_vertical_fit_mode(window.PRESERVE_MODE, row+1)

        window.content.set_cell_spacing(spacing, True)

        return window


    def __call__(
            self, position: vec2, title: Optional[str], width: int, height: Optional[int] = None,
            mode: LayoutMode = LayoutObject.GRID_MODE, fit_mode: FitMode = LayoutObject.STRETCH_MODE,
            overflow_mode: FitMode = LayoutObject.PRESERVE_MODE, justification: vec2 = Anchor.C,
            draggable: bool = False, style: StyleOrName[WindowStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> WindowObject:
        """
        Create a standard window; alias for :meth:`regular`.

        :param position: World-space position of the object.
        :param title: Window title; generated from the current time when omitted.
        :param width: Fixed width of the window.
        :param height: Fixed height of the window; content height is derived when omitted.
        :param mode: Layout mode for the content panel.
        :param fit_mode: Fit mode used to size content cells.
        :param overflow_mode: Fit mode used when content overflows.
        :param justification: Anchor used to justify content within the content panel.
        :param draggable: Whether the window can be dragged by its header, title panel, or content.
        :param style: Window style or registered window style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created window object.
        """
        return self.regular(position, title, width, height, mode, fit_mode, overflow_mode, justification, draggable, style, rotation, scale, layer, anchor, cache)