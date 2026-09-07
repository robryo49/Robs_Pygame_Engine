from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .custom import RectObject, WindowObject
from .object import PygameObject
from .object_factory import ObjectFactory
from ..rendering import ButtonStyle, Font, RectStyle, ValueCyclerStyle, ValueSelectorStyle, WindowStyle, Style
from ..utils import Anchor, Callback, Color, ObjectFlags, ScreenAnchor, StyleOrName, ValueOrGetter, inf, vec2

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
        
        self._default_styles: dict[type, Any] = {}
    
    # region PROPERTIES
    
    # region default_dialog_width
    @property
    def default_dialog_width(self):
        return self._default_dialog_width
    
    @default_dialog_width.setter
    def default_dialog_width(self, value):
        self._default_dialog_width = value
    # endregion
    
    # endregion
    
    # region STYLE METHODS
    
    def set_default_style[T](self, style_type: type[T], style: StyleOrName[T]):
        self._default_styles[style_type] = style
        return self
    
    def set_default_styles[T](self, styles: dict[type[T], StyleOrName[T]]):
        for t, s in styles.items():
            self.set_default_style(t, s)
        return self
    
    def clear_default_style[T](self, style_type: type[T]):
        self._default_styles.pop(style_type, None)
        return self
    
    def clear_default_styles(self):
        self._default_styles.clear()
    
    def get_default_style[T](self, style_type: type[T]) -> T:
        return self._default_styles.get(style_type, self._object_factory.get_default_style(style_type))
    
    def get_style[T](self, style: Optional[str | Any], style_type: type[T]) -> T:
        if isinstance(style, str):
            return self._object_factory.get_style(style, style_type)
        elif style is not None:
            return style
        else:
            return self.get_default_style(style_type)
    
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
        
        window_style = self.get_style(window_style, WindowStyle)
        button_style = self.get_style(button_style, ButtonStyle)
        
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
    
    def open_value_selection_dialog(
            self, message: Optional[str], callback: Callback[[Optional[float]], Any], default_value: float= 0.0,
            min_value: float = 0.0, max_value: float = inf, increments: float | list[float] = 1, allow_cancel: bool = True,
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None,
            value_selector_style: StyleOrName[ValueSelectorStyle] = None, anchor: vec2 = Anchor.C
    ):
        width = width or self._default_dialog_width
        
        font = self.get_style(font, Font)
        value_selector_style = self.get_style(value_selector_style, ValueSelectorStyle)
        
        text = self._object_factory.text(vec2(), message, font)
        value_selector = self._object_factory.ui.value_selector(vec2(), vec2(width - 20*2, 50), default_value, min_value, max_value, increments, callback, value_selector_style)
        
        content = self._object_factory.ui.layout.stack_in_col(vec2(), None, None, objects = [text, value_selector])
        content.set_cell_spacing(20)
        
        options = [("Confirm", lambda: value_selector.value), ("Cancel", lambda: None)] if allow_cancel else [("Confirm", lambda: value_selector.value)]
        
        return self.open_dialog(content, options, callback, position, width, height, backdrop_color, window_style, button_style, anchor)
    
    def open_value_cycling_dialog[T](
            self, message: Optional[str], callback: Callback[[T], Any], values: list[T],
            default_value: Optional[T] = None, default_value_index: Optional[int] = None, allow_cancel: bool = False,
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None,
            value_cycler_style: StyleOrName[ValueCyclerStyle] = None, anchor: vec2 = Anchor.C
    ):
        width = width or self._default_dialog_width
        default_index = values.index(default_value) if default_value is not None else default_value_index if default_value_index is not None else 0
        
        font = self.get_style(font, Font)
        value_selector_style = self.get_style(value_cycler_style, ValueCyclerStyle)
        
        text = self._object_factory.text(vec2(), message, font)
        value_selector = self._object_factory.ui.value_cycler(vec2(), vec2(width - 20*2, 50), values, default_index, callback, value_selector_style)
        
        content = self._object_factory.ui.layout.stack_in_col(vec2(), None, None, objects = [text, value_selector])
        content.set_cell_spacing(20)
        
        options = [("Confirm", lambda: value_selector.value), ("Cancel", lambda: None)] if allow_cancel else [("Confirm", lambda: value_selector.value)]
        
        return self.open_dialog(content, options, callback, position, width, height, backdrop_color, window_style, button_style, anchor)
    
    # region TEXT DIALOGS
    
    def open_text_dialog[T](
            self, message: str, values: list[tuple[str, T]], callback: Callback[[T], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        font = self.get_style(font, Font)
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
    
    # endregion
