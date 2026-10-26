"""Helpers for creating and managing modal dialogs."""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .custom import RectObject, WindowObject
from .object import PygameObject
from .object_factory import ObjectFactory
from ..rendering import ButtonStyle, Font, RectStyle, ValueCyclerStyle, ValueSelectorStyle, WindowStyle
from ..utils import Anchor, Callback, Color, ObjectFlags, ScreenAnchor, StyleOrName, ValueOrGetter, inf, vec2

if TYPE_CHECKING:
    from .window_manager import WindowManager


class DialogManager:
    """Create and manage modal dialog windows and their backdrops."""
    def __init__(self, object_factory: ObjectFactory, window_manager: WindowManager,
                 object_registration_method: Callable[[PygameObject], Any],
                 object_unregistration_method: Callable[[PygameObject], Any]) -> None:
        
        """
        Initialize dialog creation with object and window management callbacks.

        :param object_factory: Factory used to create dialog content and windows.
        :param window_manager: Window manager used to open and register dialogs.
        :param object_registration_method: Callback that registers a dialog object.
        :param object_unregistration_method: Callback that unregisters a dialog object.
        """
        self._object_factory: ObjectFactory = object_factory
        self._window_manager: WindowManager = window_manager
        
        self._register_object: Callable[[PygameObject], Any] = object_registration_method
        self._unregister_object: Callable[[PygameObject], Any] = object_unregistration_method
        
        self._default_backdrop_color = Color(0, 0, 0, 200)
        self._default_dialog_width: int = 500
    
    # region PROPERTIES
    
    # region default_dialog_width
    @property
    def default_dialog_width(self):
        """Return the default width in pixels for dialogs that do not specify one."""
        return self._default_dialog_width
    
    @default_dialog_width.setter
    def default_dialog_width(self, value):
        """
        Set the default width in pixels for dialogs that do not specify one.

        :param value: The new default width in pixels for dialogs that do not specify one.
        """
        self._default_dialog_width = value
    # endregion
    
    # endregion
    
    # region DIALOG HANDLING METHODS
    
    def _create_dialog_backdrop(self, color):
        """
        Create a full-screen backdrop rectangle for a dialog.

        :param color: Backdrop color, or ``None`` to use the default.
        :return: The created backdrop rectangle.
        """
        color = color if color is not None else self._default_backdrop_color
        return self._object_factory.shape.rect(ScreenAnchor.C, ScreenAnchor.SCREEN_DIMENSIONS, RectStyle(color))
    
    def _create_dialog[T](
            self, content: PygameObject, backdrop: RectObject, values: list[tuple[str, ValueOrGetter[T]]], callback: Callback[[T], Any],
            position: Optional[vec2] = None, anchor: vec2 = Anchor.C, width: Optional[int] = None, height: Optional[int] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None
    ):
        
        """
        Create a dialog window with option buttons from values and a callback.

        :param content: Object rendered as the dialog content.
        :param backdrop: Backdrop rectangle associated with the dialog.
        :param values: Options as text and value or getter pairs.
        :param callback: Callback invoked with the selected value.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param anchor: Anchor used to position the dialog.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :return: The created dialog window.
        """
        position = ScreenAnchor.C if position is None else position
        width = width or self._default_dialog_width
        
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
        """
        Register a dialog and its optional backdrop, then open the dialog.

        :param dialog: Dialog window to register and open.
        :param backdrop: Optional backdrop rectangle to register first.
        """
        if backdrop is not None:
            self._register_object(backdrop)
        
        self._register_object(dialog)
        self._window_manager.register(dialog)
        self._window_manager.open(dialog)
    
    def _close_dialog(self, dialog: WindowObject, backdrop: PygameObject):
        """
        Unregister a dialog and its backdrop and remove them from the window manager.

        :param dialog: Dialog window to close.
        :param backdrop: Backdrop rectangle associated with the dialog.
        """
        self._unregister_object(backdrop)
        self._unregister_object(dialog)
        self._window_manager.unregister(dialog)
    
    # endregion
    
    def open_dialog[T](
            self, content: PygameObject, values: list[tuple[str, ValueOrGetter[T]]], callback: Callback[[T], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, anchor: vec2 = Anchor.C
    ):
        """
        Open a dialog with value options and an optional backdrop.

        :param content: Object rendered as the dialog content.
        :param values: Options as text and value or getter pairs.
        :param callback: Callback invoked with the selected value.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
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
        """
        Open a dialog that selects a numeric value within optional bounds.

        :param message: Message displayed above the value selector.
        :param callback: Callback invoked with the selected value or ``None`` on cancel.
        :param default_value: Initially selected value.
        :param min_value: Minimum selectable value.
        :param max_value: Maximum selectable value.
        :param increments: Step size or list of step sizes.
        :param allow_cancel: Whether to include a cancel option.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param font: Font style or resource name.
        :param value_selector_style: Value selector style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
        width = width or self._default_dialog_width
        
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
        """
        Open a dialog that cycles through a list of values.

        :param message: Message displayed above the value cycler.
        :param callback: Callback invoked with the selected value.
        :param values: Values available for selection.
        :param default_value: Value selected initially, if present in ``values``.
        :param default_value_index: Index selected initially when no default value is given.
        :param allow_cancel: Whether to include a cancel option.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param font: Font style or resource name.
        :param value_cycler_style: Value cycler style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
        width = width or self._default_dialog_width
        default_index = values.index(default_value) if default_value is not None else default_value_index if default_value_index is not None else 0
        
        text = self._object_factory.text(vec2(), message, font)
        value_selector = self._object_factory.ui.value_cycler(vec2(), vec2(width - 20*2, 50), values, default_index, callback, value_cycler_style)
        
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
        """
        Open a dialog with a text message and value options.

        :param message: Text displayed above the options.
        :param values: Options as text and value pairs.
        :param callback: Callback invoked with the selected value.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param font: Font style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
        text = self._object_factory.text(vec2(), message, font)
        
        return self.open_dialog(text, values, callback, position, width, height, backdrop_color, window_style, button_style, anchor)
    
    def open_message_dialog(
            self, message: str, callback: Callback,
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        """
        Open a message dialog with a single confirmation option.

        :param message: Text displayed in the dialog.
        :param callback: Callback invoked when the dialog is confirmed.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param font: Font style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
        return self.open_text_dialog(message, [("Confirm", True)], callback, position, width, height, backdrop_color, window_style, button_style, font, anchor)
    
    def open_yes_no_dialog(
            self, message: str, callback: Callback[[bool], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        """
        Open a dialog with yes and no options.

        :param message: Text displayed in the dialog.
        :param callback: Callback invoked with ``True`` for yes or ``False`` for no.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param font: Font style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
        return self.open_text_dialog(message, [("Yes", True), ("No", False)], callback, position, width, height, backdrop_color, window_style, button_style, font, anchor)
    
    def open_confirm_dialog(
            self, message: str, callback: Callback[[bool], Any],
            position: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, backdrop_color: Optional[Color] = None,
            window_style: StyleOrName[WindowStyle] = None, button_style: StyleOrName[ButtonStyle] = None, font: StyleOrName[Font] = None, anchor: vec2 = Anchor.C
    ):
        """
        Open a dialog with confirm and cancel options.

        :param message: Text displayed in the dialog.
        :param callback: Callback invoked with ``True`` for confirm or ``False`` for cancel.
        :param position: Screen position of the dialog, or ``None`` for the center.
        :param width: Dialog width in pixels, or ``None`` for the default.
        :param height: Dialog height in pixels, or ``None`` for automatic sizing.
        :param backdrop_color: Backdrop color, or ``None`` to use the default.
        :param window_style: Window style or resource name.
        :param button_style: Button style or resource name.
        :param font: Font style or resource name.
        :param anchor: Anchor used to position the dialog.
        :return: The opened dialog window.
        """
        return self.open_text_dialog(message, [("Comfirm", True), ("Cancel", False)], callback, position, width, height, backdrop_color, window_style, button_style, font, anchor)
    
    # endregion
