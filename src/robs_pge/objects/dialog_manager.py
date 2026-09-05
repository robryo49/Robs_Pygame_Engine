from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .custom import RectObject, WindowObject
from .object import PygameObject
from .object_factory import ObjectFactory

from ..rendering import ButtonStyle, Font, RectStyle, WindowStyle, IconButtonStyle, SliderStyle
from ..utils import Anchor, Callback, Color, ObjectFlags, ScreenAnchor, StyleOrName, vec2, ValueOrGetter

if TYPE_CHECKING:
    from .window_manager import WindowManager


class DialogManager:
    
    def __init__(self, object_factory: ObjectFactory, window_manager: WindowManager,
                 object_registration_method: Callable[[PygameObject], Any],
                 object_unregistration_method: Callable[[PygameObject], Any]):
        
        self._object_factory: ObjectFactory = object_factory
        self._window_manager: WindowManager = window_manager
        
        self._register_object: Callable[[PygameObject], Any] = object_registration_method
        self._unregister_object: Callable[[PygameObject], Any] = object_unregistration_method
        
        
        self._default_backdrop_color = Color(0, 0, 0, 200)
        
        self._default_dialog_width: int = 500
        
        self._default_window_style: StyleOrName[WindowStyle] = WindowStyle()
        self._default_button_style: StyleOrName[ButtonStyle] = ButtonStyle()
        self._default_slider_style: StyleOrName[SliderStyle] = SliderStyle()
        self._default_icon_button_style: StyleOrName[IconButtonStyle] = IconButtonStyle()
        self._default_text_font: StyleOrName[Font] = Font()
    
    
    # region PROPERTIES
    
    # region default_dialog_width
    @property
    def default_dialog_width(self):
        return self._default_dialog_width
    
    @default_dialog_width.setter
    def default_dialog_width(self, value):
        self._default_dialog_width = value
    # endregion
    
    # region default_window_style
    @property
    def default_window_style(self):
        return self._default_window_style
    
    @default_window_style.setter
    def default_window_style(self, value):
        self._default_window_style = value
    # endregion
    
    # region default_button_style
    @property
    def default_button_style(self):
        return self._default_button_style
    
    @default_button_style.setter
    def default_button_style(self, value):
        self._default_button_style = value
    # endregion
    
    # region default_font
    @property
    def default_text_font(self):
        return self._default_text_font
    
    @default_text_font.setter
    def default_text_font(self, value):
        self._default_text_font = value
    # endregion
    
    # endregion
    
    # region DIALOG HANDLING METHODS
    
    def _create_dialog_backdrop(self, color):
        color = color if color is not None else self._default_backdrop_color
        return self._object_factory.shape.rect(ScreenAnchor.C, ScreenAnchor.SCREEN_DIMENSIONS, RectStyle(color))
    
    def _create_dialog[T](
            self, content: PygameObject, backdrop: RectObject, values: list[tuple[str, ValueOrGetter[T]]], callback: Callback[[T], Any],
            position: Optional[vec2] = None, anchor: vec2 = Anchor.C, width: Optional[int] = None, height: Optional[int] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None
    ):
        
        position = ScreenAnchor.C if position is None else position
        width = width or self._default_dialog_width
        
        window_style = window_style or self._default_window_style
        button_style = button_style or self._default_button_style
        
        def choose(v):
            self._close_dialog(dialog, backdrop)
            
            if isinstance(callback, tuple):
                for c in callback:
                    c(v)
            elif callback is not None:
                callback(v)
        
        options = []
        for text, value_or_getter in values:
            def on_click(_, value=value_or_getter):
                value = value() if callable(value) else value
                choose(value)
            
            options.append((text, on_click))
        
        dialog = self._object_factory.window.dialog(position, content, options, width, height, window_style=window_style, button_style=button_style, anchor=anchor)
        
        return dialog
    
    def _register_dialog(self, dialog: WindowObject, backdrop: Optional[RectObject] = None):
        if backdrop is not None:
            self._register_object(backdrop)
        
        self._register_object(dialog)
        self._window_manager.register(dialog)
        self._window_manager.open(dialog)
    
    def _close_dialog(self, dialog: WindowObject, backdrop: PygameObject):
        self._unregister_object(backdrop)
        self._unregister_object(dialog)
        self._window_manager.unregister(dialog)
    
    # endregion
    
    def open_dialog[T](
            self, content: PygameObject, values: list[tuple[str, ValueOrGetter[T]]], callback: Callback[[T], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, anchor: vec2 = Anchor.C
    ):
        backdrop = self._create_dialog_backdrop(backdrop_color).add_flag(ObjectFlags.HOVERABLE)
        dialog = self._create_dialog(content, backdrop, values, callback, position, anchor, width, height, window_style, button_style)
        self._register_dialog(dialog, backdrop)
        
        return dialog
    
    def open_text_dialog[T](
            self, message: str, values: list[tuple[str, T]], callback: Callback[[T], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        
        font = font or self.default_text_font
        text = self._object_factory.text(vec2(), message, font)
        
        return self.open_dialog(text, values, callback, position, width, height, backdrop_color, window_style, button_style, anchor)

    def open_message_dialog(
            self, message: str, callback: Callback,
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        return self.open_text_dialog(message, [("Confirm", True)], callback, position, width, height, backdrop_color, window_style, button_style, font, anchor)

    def open_yes_no_dialog(
            self, message: str, callback: Callback[[bool], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        return self.open_text_dialog(message, [("Yes", True), ("No", False)], callback, position, width, height, backdrop_color, window_style, button_style, font, anchor)

    def open_confirm_dialog(
            self, message: str, callback: Callback[[bool], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        return self.open_text_dialog(message, [("Comfirm", True), ("Cancel", False)], callback, position, width, height, backdrop_color, window_style, button_style, font, anchor)
    
    