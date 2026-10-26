"""Higher-level UI objects built from primitive and layout objects."""

from __future__ import annotations

from typing import cast, Callable, TYPE_CHECKING, Any, Optional

from .primitive_objects import CircleObject, LineObject, RectObject, TextObject
from .sprite_objects import IconObject, SpriteObject
from .layout_objects import LayoutObject
from ...animation import SetterAnimation
from ...rendering import CircleRenderer, RectRenderer
from ...utils import Anchor, Callback, Easing, Transform, clamp, inf, invert_y, vec2, Font, split_text

if TYPE_CHECKING:
    from ..object import PygameObject
    from ...core import ServicesCollection



class TextBoxObject(LayoutObject):
    """Layout object that wraps text into line TextObjects inside a rectangle."""
    def __init__(self, transform: Transform, renderer: RectRenderer, text, font: Font, text_objects: list[TextObject],
                 text_object_factory: Callable[..., TextObject], services: ServicesCollection,
                 sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the text box with its font and line object factory.

        :param transform: Transform applied to the text box.
        :param renderer: Rectangle renderer used by the text box.
        :param text: Initial text to display.
        :param font: Font used to render the text.
        :param text_objects: Text objects used for the initial lines.
        :param text_object_factory: Factory used to create additional line objects.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the text box.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)

        self._font = font

        self._text = text
        self._text_objects = text_objects

        self._text_object_factory = text_object_factory

    @property
    def text(self) -> str:
        """Return the text displayed by the box."""
        return self._text

    @text.setter
    def text(self, value: str):
        """
        Set the text and mark the layout dirty when it changes.

        :param value: The new value.
        """
        if value != self._text:
            self._text = value
            self.mark_dirty()

    @property
    def font(self) -> Font:
        """Return the font used by the text box."""
        return self._font

    @font.setter
    def font(self, value: Font):
        """
        Set the font and rebuild the line objects when it changes.

        :param value: The new value.
        """
        if value is not self._font:
            self._font = value
            self._text_objects = []
            self.mark_dirty()

    @property
    def text_align(self):
        """Return the justification used as text alignment."""
        return self.justification

    @text_align.setter
    def text_align(self, value: vec2):
        """
        Set text alignment and apply it to every line cell.

        :param value: The new value.
        """
        self.justification = value
        for cell in list(self._object_placements.values()):
            self.set_cell_anchor(value, cell)

    @property
    def line_spacing(self):
        """Return the spacing between text lines."""
        return self.cell_spacing

    @line_spacing.setter
    def line_spacing(self, value: int):
        """
        Set the spacing between text lines.

        :param value: The new spacing between text lines.
        """
        self.cell_spacing = value

    def _update_lines(self):
        """Rebuild the line TextObjects so they match the wrapped text."""
        font = self._font

        # 1. Determine available width for text wrapping
        fixed_width = self._width_constraint.fixed
        max_width = self._width_constraint.max
        available_width = (
            fixed_width if fixed_width is not None
            else max_width if max_width is not None
            else (self.width if self.width > 0 else None)
        )
        if available_width is not None:
            available_width = max(0, available_width - 2 * round(self._outer_padding.x))

        # 2. Split text into lines
        lines = split_text(self._text, font, available_width)

        # 3. Synchronize TextObjects with lines
        if len(lines) == len(self._text_objects):
            for obj, line in zip(self._text_objects, lines):
                obj.text = line
            return

        old_text_objects = self._text_objects
        template_obj = old_text_objects[0] if old_text_objects else None

        self.clear(ignore_callbacks=True)

        new_text_objects: list[TextObject] = []
        for i, line in enumerate(lines):
            if i < len(old_text_objects):
                obj = old_text_objects[i]
                obj.text = line
            else:
                obj = self._text_object_factory(
                    vec2(),
                    line,
                    font=self._font,
                    layer=template_obj.sub_layer if template_obj is not None else self.sub_layer,
                    anchor=Anchor.C,
                    cache=template_obj.renderer.cache if template_obj is not None else True,
                )
            new_text_objects.append(obj)
            self.stack_y(obj, x=0, anchor=self.text_align)

        self._text_objects = new_text_objects

    def _update_self(self, dt: float) -> LayoutObject:
        """
        Rebuild lines when dirty before running the normal layout update.

        :param dt: Seconds elapsed since the previous update.
        :return: This text box after the update.
        """
        if self._dirty:
            self._update_lines()
        return super()._update_self(dt)


class ButtonObject(RectObject):
    """Rectangle button with a centered text object and a click callback."""
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, action: Callback[..., Any], services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        
        """
        Initialize the button and attach its text and click handler.

        :param transform: Transform applied to the button.
        :param background: Rectangle renderer used as the button background.
        :param text: Text object centered on the button.
        :param action: Callback invoked when the button is clicked.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the button.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._text: TextObject = text
        
        self.add_child(self._text, Anchor.C)
        
        self.do_on_click(1, action)
    
    # region PROPERTIES
    
    @property
    def text(self):
        """Return the button text."""
        return self._text.text
    
    @text.setter
    def text(self, value):
        """
        Set the button text.

        :param value: The new button text.
        """
        self._text.text = value
        
    @property
    def font(self):
        """Return the font used by the button text."""
        return self._text.font
    
    # region font_color
    @property
    def font_color(self):
        """Return the button font color."""
        return self.font.color
    
    @font_color.setter
    def font_color(self, value):
        """
        Set the button font color.

        :param value: The new button font color.
        """
        self.font.color = value
    # endregion
    
    # endregion


class SpriteButtonObject(RectObject):
    """Rectangle button with a centered sprite object and a click callback."""
    def __init__(self, transform: Transform, background: RectRenderer, sprite: SpriteObject, action: Callback[..., Any], services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        
        """
        Initialize the sprite button and attach its sprite and click handler.

        :param transform: Transform applied to the button.
        :param background: Rectangle renderer used as the button background.
        :param sprite: Sprite object centered on the button.
        :param action: Callback invoked when the button is clicked.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the button.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._sprite = sprite
        
        self.add_child(self._sprite, Anchor.C)
        
        self.do_on_click(1, action)
    
    # region PROPERTIES
    
    @property
    def sprite(self) -> SpriteObject:
        """Return the sprite displayed by the button."""
        return self._sprite
    
    # endregion
    

class IconButtonObject(SpriteButtonObject):
    """Sprite button specialized for icon sprites with icon accessors."""
        
    # region PROPERTIES
    
    @property
    def sprite(self) -> IconObject:
        """Return the icon sprite displayed by the button."""
        return cast(IconObject, self._sprite)
    
    # region icon
    @property
    def icon(self):
        """Return the icon name."""
        return self.sprite.icon
    
    @icon.setter
    def icon(self, value):
        """
        Set the icon name.

        :param value: The new icon name.
        """
        self.sprite.icon = value
    # endregion
    
    # region icon_color
    @property
    def icon_color(self):
        """Return the icon color."""
        return self.sprite.icon_color
    
    @icon_color.setter
    def icon_color(self, value):
        """
        Set the icon color.

        :param value: The new icon color.
        """
        self.sprite.icon_color = value
    # endregion
    
    # region icon_size
    @property
    def icon_size(self):
        """Return the icon size."""
        return self.sprite.icon_size
    
    @icon_size.setter
    def icon_size(self, value):
        """
        Set the icon size.

        :param value: The new icon size.
        """
        self.sprite.icon_size = value
    # endregion
    
    # endregion
    


class CycleButtonObject(ButtonObject):
    """Button that cycles through paired texts and values on left and right clicks."""
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, texts: tuple[str, ...], values: tuple[Any, ...], callback: Callback[[Any], Any], services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the cycle button and validate its text and value pairs.

        :param transform: Transform applied to the button.
        :param background: Rectangle renderer used as the button background.
        :param text: Text object centered on the button.
        :param texts: Text labels cycled by the button.
        :param values: Values paired with the text labels.
        :param callback: Optional callback invoked with the new value after cycling.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the button.
        :raises ValueError: texts is empty or values does not match texts in length.
        """
        super().__init__(transform, background, text, None, services, sub_layer, anchor)

        if not texts:
            raise ValueError("CycleButton requires at least one text")
        if len(values) != len(texts):
            raise ValueError("CycleButton texts and values must have the same length")

        self._texts = texts
        self._values = values
        
        self._index = 0
        
        self.do_on_click(1, lambda o: self.cycle_forward())
        self.do_on_click(3, lambda o: self.cycle_backward())
        
        if callback is not None:
            self.do_on_click(1, lambda o: callback(self.value))
            self.do_on_click(3, lambda o: callback(self.value))
    
    
    # region PROPERTIES
    
    @property
    def texts(self):
        """Return the tuple of cycle labels."""
        return self._texts
    
    @property
    def values(self):
        """Return the tuple of cycle values."""
        return self._values
    
    @property
    def value(self):
        """Return the value at the current index."""
        return self._values[self._index]
    
    # region index
    @property
    def index(self):
        """Return the current cycle index."""
        return self._index
    
    @index.setter
    def index(self, value: int):
        """
        Set the cycle index, wrapping it into range and updating the label.

        :param value: The new value.
        """
        self._index = value % len(self._texts)
        self.text = self.texts[self._index]
        
    def cycle_forward(self, amount: int = 1):
        """
        Advance the cycle index and update the label.

        :param amount: Number of steps to advance.
        """
        self.index += amount
        
    def cycle_backward(self, amount: int = 1):
        """
        Move the cycle index backward and update the label.

        :param amount: Number of steps to move backward.
        """
        self.index -= amount
    
    # endregion
    
    # endregion


class CheckBoxObject(RectObject):
    """Checkable rectangle button that toggles a checked icon."""
    def __init__(self, transform: Transform, background: RectRenderer, checked_icon: IconObject, callback: Callback[[PygameObject], Any],
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the check box with a hidden checked icon.

        :param transform: Transform applied to the check box.
        :param background: Rectangle renderer used as the check box background.
        :param checked_icon: Icon shown while the box is checked.
        :param callback: Callback invoked when the check box is clicked.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the check box.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._checked_icon = checked_icon
        self.add_child(self._checked_icon)
        self._checked_icon.hide()
        
        self.do_on_click(1, lambda o: self.toggle())
        if callback is not None:
            self.do_on_click(1, callback)
        
    # region PROPERTIES
    
    @property
    def checked(self):
        """Return whether the check box is checked."""
        return self._checked_icon.visible
    
    @property
    def unchecked(self):
        """Return whether the check box is unchecked."""
        return not self.checked
    
    # endregion
    
    def toggle(self):
        """Toggle the check box state."""
        self._checked_icon.toggle_visible()
    
    def check(self):
        """Show the checked icon."""
        self._checked_icon.show()
    
    def uncheck(self):
        """Hide the checked icon."""
        self._checked_icon.hide()


class RadioButtonObject(CircleObject):
    """Radio-style circle button that toggles a tick circle."""
    def __init__(self, transform: Transform, background: CircleRenderer, tick: CircleObject, callback: Callback[[PygameObject], Any],
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the radio button with a hidden tick.

        :param transform: Transform applied to the radio button.
        :param background: Circle renderer used as the radio button background.
        :param tick: Circle shown while the radio button is selected.
        :param callback: Callback invoked when the radio button is clicked.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the radio button.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._tick = tick
        self.add_child(self._tick)
        self._tick.hide()
        
        self.do_on_click(1, lambda o: self.toggle())
        if callback is not None:
            self.do_on_click(1, callback)
    
    # region PROPERTIES
    
    @property
    def checked(self):
        """Return whether the radio button is selected."""
        return self._tick.visible
    
    @property
    def unchecked(self):
        """Return whether the radio button is not selected."""
        return not self.checked
    
    # endregion
    
    def toggle(self):
        """Toggle the radio button state."""
        self._tick.toggle_visible()
    
    def check(self):
        """Show the tick."""
        self._tick.show()
    
    def uncheck(self):
        """Hide the tick."""
        self._tick.hide()
        

class ToggleButtonObject(RectObject):
    """Sliding switch that animates a toggle handle between two x positions."""
    def __init__(self, transform: Transform, background: RectRenderer, toggle: RectObject, toggle_background: RectObject, toggle_movement_range: tuple[int, int], callback: Callback[[PygameObject], Any],
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the switch and attach its toggle parts.

        :param transform: Transform applied to the switch.
        :param background: Rectangle renderer used as the switch background.
        :param toggle: Handle rectangle that moves between the two positions.
        :param toggle_background: Rectangle that fills the area behind the handle.
        :param toggle_movement_range: Minimum and maximum x positions of the handle.
        :param callback: Callback invoked when the switch is clicked.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the switch.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._toggle_min_x = toggle_movement_range[0]
        self._toggle_max_x = toggle_movement_range[1]
        self._toggle_movement_range = self._toggle_max_x - self._toggle_min_x
        
        self._toggle = toggle
        self._toggle_background = toggle_background
        
        self._enabled = False
        
        self.add_child(toggle_background, Anchor.L)
        self.add_child(toggle, Anchor.L)
        
        toggle.anchor = Anchor.L
        toggle_background.anchor = Anchor.L
        
        self.do_on_click(1, lambda o: self.toggle())
        
        self._toggle_background.make_attribute_dynamic("width", lambda: self._toggle.x_pos + self._toggle.width * 0.5)
        if callback is not None:
            self.do_on_click(1, callback)
    
    # region PROPERTIES
    
    @property
    def enabled(self):
        """Return whether the switch is enabled."""
        return self._enabled
    
    @property
    def disabled(self):
        """Return whether the switch is disabled."""
        return not self.enabled
    
    # endregion
    
    def toggle(self):
        """Toggle the switch between enabled and disabled."""
        if self._enabled:
            self.disable()
        else:
            self.enable()
    
    def enable(self):
        """Enable the switch and animate the handle to its right position."""
        self._enabled = True
        self._toggle.play_animation(
            SetterAnimation(self._toggle, "x_pos", self._toggle_max_x, 0.07, Easing.EASE_IN_QUAD, start_value=self._toggle_min_x)
        )
    
    def disable(self):
        """Disable the switch and animate the handle to its left position."""
        self._enabled = False
        self._toggle.play_animation(
            SetterAnimation(self._toggle, "x_pos", self._toggle_min_x, 0.07, Easing.EASE_IN_QUAD, start_value=self._toggle_max_x)
        )
        
    


class SliderObject(LayoutObject):
    """Slider layout object that maps a draggable handle position to a numeric value."""
    def __init__(self, transform: Transform, background: RectRenderer, bar: RectObject, handle: RectObject | CircleObject, text: TextObject, min_value: float, max_value: float, step: Optional[float],
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the slider and configure its draggable handle.

        :param transform: Transform applied to the slider.
        :param background: Rectangle renderer used as the slider background.
        :param bar: Rectangle that contains the handle.
        :param handle: Draggable rectangle or circle used to select the value.
        :param text: Text object that displays the current value.
        :param min_value: Minimum slider value.
        :param max_value: Maximum slider value, which must exceed min_value.
        :param step: Optional step size for snapping the handle.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the slider.
        :raises ValueError: max_value is not greater than min_value.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        if max_value <= min_value:
            raise ValueError("Slider max_value must be greater than min_value")

        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        
        self._bar = bar
        self._handle = handle
        self._text = text
        
        self._handle_movement_range = max(0.0, self._bar.width - self._bar.height)
        
        if step is not None:
            step = self._handle_movement_range * step / (max_value - min_value)
        
        self._handle.make_draggable(1)
        self._handle.make_attribute_fixed("y_pos")
        self._handle.make_attribute_clamped("x_pos", -self._handle_movement_range * 0.5, self._handle_movement_range * 0.5)
        if step is not None:
            self._handle.make_attribute_snap_on_grid("x_pos", step, self._handle_movement_range * 0.5)
        
        self._text.make_attribute_dynamic("text", lambda: str(self.value))
        
        self._bar.add_child(self._handle, Anchor.C)
        
    # region PROPERTIES
    
    @property
    def min_value(self):
        """Return the minimum slider value."""
        return self._min_value
    
    @property
    def max_value(self):
        """Return the maximum slider value."""
        return self._max_value
    
    @property
    def step(self):
        """Return the optional handle step size."""
        return self._step
    
    @property
    def value_range(self):
        """Return the difference between the maximum and minimum values."""
        return self.max_value - self.min_value
    
    @property
    def normalized_value(self) -> float:
        """Return the handle position normalized to the range zero to one."""
        if self._handle_movement_range == 0:
            return 0.0
        return (self._handle.x_pos + self._handle_movement_range * 0.5) / self._handle_movement_range

    @property
    def value(self):
        """Return the value selected by the handle."""
        return round(self.min_value + self.normalized_value * self.value_range, 2)

    @value.setter
    def value(self, value):
        """
        Set the value, clamping it to the slider range and moving the handle.

        :param value: The new value.
        """
        value = clamp(value, self.min_value, self.max_value)
        normalized_value = (value - self.min_value) / self.value_range
        self._handle.x_pos = (normalized_value - 0.5) * self._handle_movement_range
        
    # endregion


class ValueSelectorObject(LayoutObject):
    """Layout object that displays a clamped numeric value with increment and decrement helpers."""
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, min_value: float, max_value: float, increments: tuple[float, ...], start_value: float, callback: Callback[[float], Any], services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the value selector and display its start value.

        :param transform: Transform applied to the selector.
        :param background: Rectangle renderer used as the selector background.
        :param text: Text object that displays the current value.
        :param min_value: Minimum selectable value.
        :param max_value: Maximum selectable value.
        :param increments: Allowed increment values exposed by the selector.
        :param start_value: Initial value, clamped to the selector range.
        :param callback: Optional callback invoked when the value changes.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the selector.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._min_value = min_value
        self._max_value = max_value
        self._increments = increments
        self._text = text
        self._callback = callback
        self._value = clamp(start_value, min_value, max_value)
        self._text.text = str(self._value)
        
    # region PROPERTIES
    
    @property
    def min_value(self):
        """Return the minimum selectable value."""
        return self._min_value
    
    @property
    def max_value(self):
        """Return the maximum selectable value."""
        return self._max_value
    
    @property
    def increments(self):
        """Return the allowed increment values."""
        return self._increments
    
    @property
    def value_label(self):
        """Return the text object that displays the value."""
        return self._text
    
    @property
    def value(self):
        """Return the current value."""
        return self._value
    
    @value.setter
    def value(self, value: float):
        """
        Set the current value, clamping it and notifying the callback when it changes.

        :param value: The new value.
        """
        new_value = clamp(value, self.min_value, self.max_value)
        if new_value != self._value:
            self._value = new_value
            self._text.text = str(self._value)
            if self._callback is not None:
                self._callback(self._value)
                
    def increment(self, amount: float = 1.0):
        """
        Increase the value by the given amount.

        :param amount: Amount to add before clamping.
        """
        self.value = self._value + amount
        
    def decrement(self, amount: float = 1.0):
        """
        Decrease the value by the given amount.

        :param amount: Amount to subtract before clamping.
        """
        self.value = self._value - amount
        
    # endregion


class ValueCyclerObject(LayoutObject):
    """Layout object that cycles through a tuple of values and updates its label."""
    def __init__(self, transform: Transform, background: RectRenderer, text: TextObject, values: tuple[Any, ...], default_index: int, callback: Callback[[Any], Any], services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the value cycler and validate its values and start index.

        :param transform: Transform applied to the cycler.
        :param background: Rectangle renderer used as the cycler background.
        :param text: Text object that displays the current value.
        :param values: Values cycled by the object.
        :param default_index: Index of the initial value.
        :param callback: Optional callback invoked when the value changes.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the cycler.
        :raises ValueError: values is empty or default_index is outside the value range.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        if not values:
            raise ValueError("ValueCycler requires at least one value")
        if not (0 <= default_index < len(values)):
            raise ValueError(f"Default index {default_index} out of range for values of length {len(values)}")
            
        self._values = values
        self._index = default_index
        self._text = text
        self._callback = callback
        self._text.text = str(self.value)
        
    # region PROPERTIES
    
    @property
    def values(self):
        """Return the tuple of cycled values."""
        return self._values
    
    @property
    def index(self):
        """Return the current value index."""
        return self._index
    
    @index.setter
    def index(self, value: int):
        """
        Set the value index, wrapping it into range and notifying the callback when it changes.

        :param value: The new value.
        """
        new_index = value % len(self._values)
        if new_index != self._index:
            self._index = new_index
            self._text.text = str(self.value)
            if self._callback is not None:
                self._callback(self.value)
                
    @property
    def value(self):
        """Return the value at the current index."""
        return self._values[self._index]
    
    @property
    def value_label(self):
        """Return the text object that displays the value."""
        return self._text
        
    def cycle_forward(self, amount: int = 1):
        """
        Advance the value index and update the label.

        :param amount: Number of steps to advance.
        """
        self.index += amount
        
    def cycle_backward(self, amount: int = 1):
        """
        Move the value index backward and update the label.

        :param amount: Number of steps to move backward.
        """
        self.index -= amount
        
    # endregion


class ProgressBarObject(RectObject):
    """Rectangle progress bar whose child bar width follows a clamped value."""
    def __init__(self, transform: Transform, background: RectRenderer, bar: RectObject, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the progress bar and attach its child bar.

        :param transform: Transform applied to the progress bar.
        :param background: Rectangle renderer used as the progress bar background.
        :param bar: Rectangle whose width represents the progress.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the progress bar.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._value = 0.0
        self._max_value = 1.0
        
        self._progress = 0.0
        
        self._dirty = True
        
        self._bar = bar
        self._bar.anchor = Anchor.TL
        self._bar.pos = invert_y(vec2(self.bd))
        self.add_child(bar, Anchor.TL)
    
    # region PROPERTIES
    
    # region color
    @property
    def color(self):
        """Return the progress bar color."""
        return self._bar.bg_color
    
    @color.setter
    def color(self, value):
        """
        Set the progress bar color.

        :param value: The new progress bar color.
        """
        self._bar.bg_color = value
    # endregion
    
    # region value
    @property
    def value(self):
        """Return the current progress value."""
        return self._value
    
    @value.setter
    def value(self, value):
        """
        Set the value, clamping it and recomputing the progress fraction.

        :param value: The new value.
        """
        self._value = clamp(value, 0, self.max_value)
        self._progress = self._value / self._max_value if self._max_value > 0 else 0.0
        self.mark_dirty()
    # endregion
    
    # region max_value
    @property
    def max_value(self):
        """Return the maximum progress value."""
        return self._max_value
    
    @max_value.setter
    def max_value(self, value):
        """
        Set the maximum value and clamp the current value to it.

        :param value: The new value.
        """
        self._max_value = max(0.0, value)
        self._value = min(self._value, self._max_value)
        self._progress = self._value / self._max_value if self._max_value > 0 else 0.0
        self.mark_dirty()
    # endregion
    
    # region progress
    @property
    def progress(self):
        """Return the progress fraction between zero and one."""
        return self._progress
    
    @progress.setter
    def progress(self, value):
        """
        Set the progress fraction and update the value.

        :param value: The new value.
        """
        self._progress = clamp(value)
        self._value = self._progress * self._max_value
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def mark_dirty(self):
        """Flag the progress bar for a width recalculation."""
        self._dirty = True
    
    def _update_self(self, dt: float):
        """
        Resize the child bar when the progress has changed.

        :param dt: Seconds elapsed since the previous update.
        """
        super()._update_self(dt)
        
        if self._dirty:
            self._bar.width = round((self.width - self.bd*2) * self.progress)
            self._dirty = False


class ScrollbarObject(RectObject):
    """Vertical scrollbar with a draggable handle that exposes a normalized value."""
    def __init__(self, transform: Transform, background: RectRenderer, handle: RectObject,
                 services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the scrollbar and configure its draggable handle.

        :param transform: Transform applied to the scrollbar.
        :param background: Rectangle renderer used as the scrollbar background.
        :param handle: Draggable rectangle used to select the value.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the scrollbar.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._handle = handle
        self._handle_movement_range = 0
        self._min_y = 0
        self._max_y = 0
        
        self.add_child(self._handle, Anchor.C)
        
        self._handle.make_draggable(1)
        self._handle.make_attribute_fixed("x_pos")
        
        self.update_movement_range()
        
        self._handle.make_attribute_clamped("y_pos", lambda: self._min_y, lambda: self._max_y)
    
    # region PROPERTIES
    
    @property
    def handle_width(self):
        """Return the handle width."""
        return self._handle.width
    
    @property
    def handle_height(self) -> float:
        """Return the handle height."""
        return self._handle.height
    
    @handle_height.setter
    def handle_height(self, value: float):
        """
        Set the handle height and refresh the movement range.

        :param value: The new value.
        """
        self._handle.height = clamp(value, 5.0, self.height)
        self.update_movement_range()
        
        self.value = self.value
    
    @property
    def normalized_value(self) -> float:
        """Return the handle position normalized around zero."""
        if self._handle_movement_range == 0:
            return 0.0
        return 0.5 + self._handle.y_pos / self._handle_movement_range
    
    @property
    def value(self) -> float:
        """Return the scroll value clamped between zero and one."""
        return clamp(self.normalized_value, 0.0, 1.0)
    
    @value.setter
    def value(self, value: float):
        """
        Set the scroll value and move the handle.

        :param value: The new value.
        """
        value = clamp(value, 0.0, 1.0)
        self._handle.y_pos = (value - 0.5) * self._handle_movement_range
        
    def set_value(self, value: float):
        """
        Set the scroll value.

        :param value: New scroll value between zero and one.
        """
        self.value = value
    
    # endregion
    
    @property
    def handle_movement_range(self):
        """Return the distance the handle can travel."""
        return self._handle_movement_range
    
    def update_movement_range(self):
        """Recompute the handle movement range and clamp bounds."""
        margin = max(0.0, (self.width - self._handle.width) * 0.5)
        self._handle_movement_range = max(0.0, self.height - self._handle.height - margin * 2)

        self._min_y = -self._handle_movement_range * 0.5
        self._max_y = self._handle_movement_range * 0.5


class LineChartObject(RectObject):
    """Rectangle chart that renders data points as a line with configurable bounds."""
    def __init__(self, transform: Transform, background: RectRenderer, line: LineObject, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the line chart and attach its line object.

        :param transform: Transform applied to the chart.
        :param background: Rectangle renderer used as the chart background.
        :param line: Line object used to draw the data points.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the chart.
        """
        super().__init__(transform, background, services, sub_layer, anchor)
        
        self._pad_x = 0
        self._pad_y = 0
        
        self._min_x_value = None
        self._max_x_value = None
        
        self._min_y_value = None
        self._max_y_value = None
        
        self._min_data_x = inf
        self._max_data_x = 0.0
        
        self._min_data_y = inf
        self._max_data_y = 0.0
        
        self._data_points = []
        self._max_data_points = None
        self._max_data_x_range = None
        
        self._dirty = True
        
        self._line = line
        self.add_child(line, Anchor.TL)
    
    # region PROPERTIES
    
    # region color
    @property
    def color(self):
        """Return the chart line color."""
        return self._line.color
    
    @color.setter
    def color(self, value):
        """
        Set the chart line color.

        :param value: The new chart line color.
        """
        self._line.color = value
    # endregion
    
    # region min_x_value
    @property
    def min_x_value(self):
        """Return the fixed minimum x bound."""
        return self._min_x_value
    
    @min_x_value.setter
    def min_x_value(self, value):
        """
        Set the minimum x bound.

        :param value: The new minimum x bound.
        """
        self._min_x_value = value
        self.mark_dirty()
    # endregion
    
    # region max_x_value
    @property
    def max_x_value(self):
        """Return the fixed maximum x bound."""
        return self._max_x_value
    
    @max_x_value.setter
    def max_x_value(self, value):
        """
        Set the maximum x bound.

        :param value: The new maximum x bound.
        """
        self._max_x_value = value
        self.mark_dirty()
    # endregion
    
    # region min_y_value
    @property
    def min_y_value(self):
        """Return the fixed minimum y bound."""
        return self._min_y_value
    
    @min_y_value.setter
    def min_y_value(self, value):
        """
        Set the minimum y bound.

        :param value: The new minimum y bound.
        """
        self._min_y_value = value
        self.mark_dirty()
    # endregion
    
    # region max_y_value
    @property
    def max_y_value(self):
        """Return the fixed maximum y bound."""
        return self._max_y_value
    
    @max_y_value.setter
    def max_y_value(self, value):
        """
        Set the maximum y bound.

        :param value: The new maximum y bound.
        """
        self._max_y_value = value
        self.mark_dirty()
    # endregion
    
    # region pad_x
    @property
    def pad_x(self):
        """Return the horizontal chart padding."""
        return self._pad_x
    
    @pad_x.setter
    def pad_x(self, value):
        """
        Set the horizontal chart padding.

        :param value: The new horizontal chart padding.
        """
        self._pad_x = value
        self.mark_dirty()
    # endregion
    
    # region pad_y
    @property
    def pad_y(self):
        """Return the vertical chart padding."""
        return self._pad_y
    
    @pad_y.setter
    def pad_y(self, value):
        """
        Set the vertical chart padding.

        :param value: The new vertical chart padding.
        """
        self._pad_y = value
        self.mark_dirty()
    # endregion
    
    # region max_data_points
    @property
    def max_data_points(self):
        """Return the maximum number of retained data points."""
        return self._max_data_points
    
    @max_data_points.setter
    def max_data_points(self, value):
        """
        Set the maximum number of retained data points and trim the data.

        :param value: New maximum count, or None for no limit.
        :raises ValueError: value is negative.
        """
        if value is not None and value < 0:
            raise ValueError("max_data_points must be non-negative")
        self._max_data_points = value
        self._trim_data()
        self._recompute_data_range()
        self.mark_dirty()
    # endregion
    
    # region max_data_x_range
    @property
    def max_data_x_range(self):
        """Return the maximum x range retained in the data."""
        return self._max_data_x_range
    
    @max_data_x_range.setter
    def max_data_x_range(self, value):
        """
        Set the maximum x range retained in the data and trim it.

        :param value: New maximum range, or None for no limit.
        :raises ValueError: value is negative.
        """
        if value is not None and value < 0:
            raise ValueError("max_data_x_range must be non-negative")
        self._max_data_x_range = value
        self._trim_data()
        self._recompute_data_range()
        self.mark_dirty()
    # endregion
    
    # endregion
    
    def insert_point(self, point: vec2):
        """
        Insert a point while keeping the data sorted by x-coordinate.

        :param point: Point to insert.
        """
        index = len(self._data_points)
        for i, existing in enumerate(self._data_points):
            if existing.x > point.x:
                index = i
                break

        self._data_points.insert(index, point)
        self._trim_data()
        self._recompute_data_range()
        self.mark_dirty()

    def _trim_data(self) -> None:
        """Drop old points so the configured count and x-range limits are respected."""
        while self._max_data_points is not None and len(self._data_points) > self._max_data_points:
            self._data_points.pop(0)

        if self._max_data_x_range is not None:
            while len(self._data_points) > 1:
                x_range = self._data_points[-1].x - self._data_points[0].x
                if x_range <= self._max_data_x_range:
                    break
                self._data_points.pop(0)

    def _recompute_data_range(self) -> None:
        """Recompute the minimum and maximum data bounds from the points."""
        if not self._data_points:
            self._min_data_x = inf
            self._max_data_x = 0.0
            self._min_data_y = inf
            self._max_data_y = 0.0
            return

        self._min_data_x = min(p.x for p in self._data_points)
        self._max_data_x = max(p.x for p in self._data_points)
        self._min_data_y = min(p.y for p in self._data_points)
        self._max_data_y = max(p.y for p in self._data_points)

    def remove_point(self, point: vec2):
        """
        Remove a data point and recompute the data bounds.

        :param point: Point to remove.
        """
        self._data_points.remove(point)
        self._recompute_data_range()
        self.mark_dirty()
    
    def remove_last(self):
        """Remove the oldest data point and recompute the data bounds."""
        if self._data_points:
            self._data_points.pop(0)
        self._recompute_data_range()
        self.mark_dirty()
    
    def mark_dirty(self):
        """Flag the chart for a line recalculation."""
        self._dirty = True
    
    def _update_self(self, dt: float):
        """
        Rebuild the line points from the data when the chart is dirty.

        :param dt: Seconds elapsed since the previous update.
        """
        super()._update_self(dt)
        
        if self._dirty:
            points = []
            
            if self._data_points:
                min_x_value = self._min_x_value if self._min_x_value is not None else self._min_data_x
                max_x_value = self._max_x_value if self._max_x_value is not None else self._max_data_x
                min_y_value = self._min_y_value if self._min_y_value is not None else self._min_data_y
                max_y_value = self._max_y_value if self._max_y_value is not None else self._max_data_y
                
                width = max_x_value - min_x_value
                height = max_y_value - min_y_value
                
                x_fac = (self.width - 2*self._pad_x)/width if width else 0
                y_fac = (self.height - 2*self._pad_y)/height if height else 0
                
                for point in self._data_points:
                    if min_x_value <= point.x <= max_x_value and min_y_value <= point.y <= max_y_value:
                        points.append(vec2(
                            self._pad_x + (point.x - min_x_value) * x_fac,
                            (self.height - self._pad_y) - (point.y - min_y_value) * y_fac
                        ))
            
            self._line.points = points
            
            self._dirty = False

