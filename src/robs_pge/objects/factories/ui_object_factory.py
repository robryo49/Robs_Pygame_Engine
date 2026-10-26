"""
Factories for creating interactive UI widgets such as sliders, progress bars, charts, and selectors.
"""

from typing import Any, Optional

from .sub_object_factory import SubObjectFactory
from ..behaviors import MultiplyAttributeOnClickBehavior, MultiplyAttributeOnHoverBehavior, SetAttributeOnHoverBehavior, SetAttributeOnClickBehavior
from ..custom import *
from ..object import PygameObject
from ...rendering import ButtonStyle, CircleRenderer, IconButtonStyle, RadioButtonStyle, SpriteButtonStyle, ToggleButtonStyle
from ...rendering import CircleStyle, LineChartStyle, LineStyle, ProgressBarStyle, RectRenderer, RectStyle, ScrollbarStyle, SliderStyle, ValueSelectorStyle, ValueCyclerStyle
from ...resources import Icons
from ...resources import Texture
from ...utils import Anchor, StyleOrName, length, vec2, Callback, Font, inf, clamp
from ...utils import Easing, get_object_dims, Color


class UIObjectFactory(SubObjectFactory):
    """
    Create interactive UI widgets and expose the button, layout, and debug sub-factories.
    """

    # region HELPERS

    @staticmethod
    def _add_button_behaviors(obj: PygameObject, buttons: int | list[int], hovered_scale: float, clicked_scale: float,
                              bg_color: Optional[Color], hovered_color: Optional[Color], clicked_color: Optional[Color],
                              content_color_attribute: Optional[str], content_color: Optional[Color], hovered_content_color: Optional[Color], clicked_content_color: Optional[Color],
                              transition_duration: float):
        """
        Add scale and color transition behaviors to a button object.

        :param obj: Button object to which behaviors are added.
        :param buttons: Mouse button index or indices that trigger click behaviors.
        :param hovered_scale: Scale multiplier applied while the object is hovered.
        :param clicked_scale: Scale multiplier applied while the object is clicked.
        :param bg_color: Base background color used as the click transition start.
        :param hovered_color: Background color applied while the object is hovered.
        :param clicked_color: Background color applied while the object is clicked.
        :param content_color_attribute: Attribute name of the content color to animate.
        :param content_color: Base content color used as the click transition start.
        :param hovered_content_color: Content color applied while the object is hovered.
        :param clicked_content_color: Content color applied while the object is clicked.
        :param transition_duration: Duration of each transition in seconds.
        """
        if hovered_scale != 1:
            obj.add_behavior(MultiplyAttributeOnHoverBehavior("scale", hovered_scale, transition_duration, Easing.EASE_IN_QUAD))

        if clicked_scale != 1:
            for b in buttons if isinstance(buttons, list) else [buttons]:
                obj.add_behavior(MultiplyAttributeOnClickBehavior(b, "scale", clicked_scale, transition_duration, Easing.EASE_IN_QUAD))

        if bg_color is not None and hovered_color is not None and hovered_color != bg_color:
            obj.add_behavior(SetAttributeOnHoverBehavior("bg_color", bg_color, hovered_color, transition_duration, Easing.EASE_IN_QUAD))

        click_start = hovered_color if hovered_color is not None else bg_color
        if bg_color is not None and clicked_color is not None and clicked_color != click_start:
            for b in buttons if isinstance(buttons, list) else [buttons]:
                obj.add_behavior(SetAttributeOnClickBehavior(b, "bg_color", click_start, clicked_color, transition_duration, Easing.EASE_IN_QUAD))

        if content_color_attribute is not None and content_color is not None and hovered_content_color is not None and hovered_content_color != content_color:
            obj.add_behavior(SetAttributeOnHoverBehavior(content_color_attribute, content_color, hovered_content_color, transition_duration, Easing.EASE_IN_QUAD))

        content_click_start = hovered_content_color if hovered_content_color is not None else content_color
        if content_color_attribute is not None and content_color is not None and clicked_content_color is not None and clicked_content_color != content_click_start:
            obj.add_behavior(SetAttributeOnClickBehavior(1, content_color_attribute, content_click_start, clicked_content_color, transition_duration, Easing.EASE_IN_QUAD))

    # endregion

    # region CONSTRUCTORS

    # region BUTTONS

    def button(
            self, position: vec2, text: str, action: Callback[[PygameObject], Any] = None, dims: Optional[vec2] = None, width: Optional[float] = None, height: Optional[float] = None, style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ButtonObject:
        """
        Create a button with a text label and an optional click action.

        :param position: World-space position of the object.
        :param text: Text displayed on the button.
        :param action: Callback invoked when the button is clicked.
        :param dims: Explicit button dimensions; derived from the label and style when omitted.
        :param width: Explicit button width used when ``dims`` is not provided.
        :param height: Explicit button height used when ``dims`` is not provided.
        :param style: Button style or name of a registered button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created button object.
        """

        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = button_style.margin
        font = self._get_resource(button_style.font, Font)
        dims = get_object_dims(dims, width, height, font.get_render_size(text), margin)

        obj = self._create_object(ButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                  self._factory.text.label(vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), action
                                  )

        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   "font_color", font.color, button_style.hovered_text_color, button_style.clicked_text_color,
                                   button_style.transition_duration)

        return obj

    def cycle_button(
            self, position: vec2, texts: tuple[str, ...], values: Optional[tuple[Any, ...]] = None, default_index: int = 0, callback: Callback[[PygameObject], Any] = None, dims: Optional[vec2] = None, width: Optional[float] = None, height: Optional[float] = None, style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> CycleButtonObject:
        """
        Create a button that cycles through a sequence of texts and optional values.

        :param position: World-space position of the object.
        :param texts: Labels the button cycles through.
        :param values: Values corresponding to the texts; defaults to the texts themselves.
        :param default_index: Index of the initially displayed text and value.
        :param callback: Callback invoked when the selected value changes.
        :param dims: Explicit button dimensions; derived from the largest text when omitted.
        :param width: Explicit button width used when ``dims`` is not provided.
        :param height: Explicit button height used when ``dims`` is not provided.
        :param style: Button style or name of a registered button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created cycle button object.
        :raises ValueError: If ``texts`` is empty.
        :raises ValueError: If the lengths of ``texts`` and ``values`` differ.
        :raises ValueError: If ``default_index`` is outside the range of ``texts``.
        """

        if not texts:
            raise ValueError("CycleButton requires at least one text")
        if values is None:
            values = texts
        if len(values) != len(texts):
            raise ValueError("CycleButton texts and values must have the same length")
        if not 0 <= default_index < len(texts):
            raise ValueError(f"Default index {default_index} out of range for texts of length {len(texts)}")

        text = texts[default_index]

        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = button_style.margin
        font = self._get_resource(button_style.font, Font)
        text_dims = [font.get_render_size(t) for t in texts]

        max_text_dims = vec2(max(d[0] for d in text_dims), max(d[1] for d in text_dims))
        dims = get_object_dims(dims, width, height, max_text_dims, margin)

        obj = self._create_object(CycleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                  self._factory.text.label(vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), texts, values, callback
                                  )
        obj.index = default_index

        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   "font_color", font.color, button_style.hovered_text_color, button_style.clicked_text_color,
                                   button_style.transition_duration)
        return obj

    def sprite_button(
            self, position: vec2, texture: Texture, action: Callback[[PygameObject], Any] = None, dims: Optional[vec2] = None, width: Optional[float] = None, height: Optional[float] = None, style: StyleOrName[SpriteButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        """
        Create a button rendered with a sprite texture.

        :param position: World-space position of the object.
        :param texture: Texture or registered texture name used for the sprite.
        :param action: Callback invoked when the button is clicked.
        :param dims: Explicit button dimensions; derived from the texture and style when omitted.
        :param width: Explicit button width used when ``dims`` is not provided.
        :param height: Explicit button height used when ``dims`` is not provided.
        :param style: Sprite button style or name of a registered sprite button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created sprite button object.
        """

        button_style = self._get_resource(style, SpriteButtonStyle)
        bg_style = button_style.bg_style
        margin = button_style.margin

        sprite = self._factory.sprite.sprite(vec2(), texture)

        dims = get_object_dims(dims, width, height, texture.dims, margin)

        obj = self._create_object(SpriteButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, action)

        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   None, None, None, None,
                                   button_style.transition_duration)

        return obj

    def icon_button(
            self, position: vec2, icon: str, icon_size: int, action: Callback[[PygameObject], Any] = None, dims: Optional[vec2] = None, width: Optional[float] = None, height: Optional[float] = None, style: StyleOrName[IconButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> IconButtonObject:
        """
        Create a button rendered with an icon.

        :param position: World-space position of the object.
        :param icon: Icon identifier.
        :param icon_size: Size of the icon in pixels.
        :param action: Callback invoked when the button is clicked.
        :param dims: Explicit button dimensions; derived from the icon and style when omitted.
        :param width: Explicit button width used when ``dims`` is not provided.
        :param height: Explicit button height used when ``dims`` is not provided.
        :param style: Icon button style or name of a registered icon button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created icon button object.
        """

        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style
        bg_style = button_style.bg_style
        margin = button_style.margin

        sprite: IconObject = self._factory.sprite.icon_object(vec2(), icon, icon_size, icon_button_style.icon_color)

        dims =get_object_dims(dims, width, height, sprite.dims, margin)

        obj = self._create_object(IconButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, action)


        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   None, None, None, None,
                                   button_style.transition_duration)

        return obj

    def checkbox(
            self, position: vec2, icon_size, size: Optional[float] = None, callback: Callback[[PygameObject], Any] = None, checked_icon: str = Icons.CHECK, checked=False, style: StyleOrName[IconButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> CheckBoxObject:
        """
        Create a checkbox backed by an icon and an optional callback.

        :param position: World-space position of the object.
        :param icon_size: Size of the checkbox icons in pixels.
        :param size: Size of the checkbox; derived from the icon when omitted.
        :param callback: Callback invoked when the checkbox is toggled.
        :param checked_icon: Icon identifier used when the checkbox is checked.
        :param checked: Whether the checkbox starts checked.
        :param style: Icon button style or name of a registered icon button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created checkbox object.
        """

        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style

        bg_style = button_style.bg_style
        margin = button_style.margin

        icon = Icons.get(checked_icon, icon_size, icon_button_style.icon_color)
        sprite = self._factory.sprite.sprite(vec2(), icon)

        dims = get_object_dims(vec2(size) if size is not None else None, None, None, sprite.dims, margin)

        obj = self._create_object(CheckBoxObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, callback)

        if checked: obj.check()

        return obj

    def radio_button(
            self, position: vec2, radius: int, callback: Callback[[bool], Any] = None, checked=False, style: StyleOrName[RadioButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> RadioButtonObject:
        """
        Create a radio button with a circular track and inner tick.

        :param position: World-space position of the object.
        :param radius: Radius of the radio button in pixels.
        :param callback: Callback invoked with the checked state.
        :param checked: Whether the radio button starts checked.
        :param style: Radio button style or name of a registered radio button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created radio button object.
        """

        radio_button_style = self._get_resource(style, RadioButtonStyle)
        bg_style = radio_button_style.bg_style

        margin = radio_button_style.margin + bg_style.bd
        color = radio_button_style.icon_color

        tick_radius = max(1, radius - margin)
        tick = self._factory.shape.circle(vec2(), tick_radius, CircleStyle(color), cache=cache)

        obj = self._create_object(RadioButtonObject, position, rotation, scale, CircleRenderer(radius, bg_style, cache), layer, anchor, tick, callback)

        if checked: obj.check()

        return obj

    def toggle_button(
            self, position: vec2, dims: vec2, toggle_width: Optional[int] = None, enabled=False, callback: Callback[[bool], Any] = None, style: StyleOrName[ToggleButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ToggleButtonObject:
        """
        Create a toggle switch with a sliding handle.

        :param position: World-space position of the object.
        :param dims: Dimensions of the toggle track.
        :param toggle_width: Width of the toggle handle; defaults to a fraction of the track width.
        :param enabled: Whether the toggle starts enabled.
        :param callback: Callback invoked with the enabled state.
        :param style: Toggle button style or name of a registered toggle button style.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created toggle button object.
        """

        toggle_button_style = self._get_resource(style, ToggleButtonStyle)
        bg_style = toggle_button_style.bg_style
        toggle_style = toggle_button_style.toggle_style.copy()
        toggle_bg_color = toggle_button_style.toggle_bg_color

        toggle_style.bd_radius = bg_style.inset_bd_radius()
        max_toggle_width = max(1.0, dims.x - 2 * bg_style.bd)
        toggle_width = clamp(toggle_width or dims.x * 0.3, 1, max_toggle_width)
        toggle_height = max(1.0, dims.y - 2 * bg_style.bd)

        travel_start = float(bg_style.bd)
        travel_end = max(travel_start, dims.x - bg_style.bd - toggle_width)
        toggle_movement_range = (travel_start, travel_end)

        toggle = self._factory.shape.rect(vec2(bg_style.bd, 0), vec2(toggle_width, toggle_height), toggle_style)
        toggle_bg = self._factory.shape.rect(vec2(bg_style.bd, 0), vec2(toggle_width / 2, toggle_height), toggle_style.with_(bg_color=toggle_bg_color, bd_color=toggle_bg_color))

        obj = self._create_object(ToggleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, toggle, toggle_bg, toggle_movement_range, callback)

        if enabled: obj.enable()

        return obj

    # endregion

    def slider(
            self, position: vec2, dims: vec2, min_value: float, max_value: float, step: Optional[float] = None, start_value=None, style: StyleOrName[SliderStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SliderObject:
        """
        Create a slider with a bar, handle, and value label.

        :param position: World-space position of the object.
        :param dims: Dimensions of the slider.
        :param min_value: Minimum selectable value.
        :param max_value: Maximum selectable value.
        :param step: Increment between values; continuous when omitted.
        :param start_value: Initial value; defaults to the minimum.
        :param style: Slider style or registered slider style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created slider object.
        """

        slider_style = self._get_resource(style, SliderStyle)
        bg_style = slider_style.bg_style
        bar_style = slider_style.bar_style
        handle_style: RectStyle | CircleStyle = slider_style.handle_style
        font = self._get_resource(slider_style.font, Font)

        max_text_width = font.get_render_size(str(max_value) + ".00" )[0]
        bar_width = slider_style.bar_width
        handle_size = slider_style.handle_size

        text_height = font.get_render_size(str(max_value) + ".00")[1]
        content_height: float = max(bar_width, text_height)
        margin = round((dims.y - content_height) * 0.5)

        bar = self._factory.shape.rect(vec2(), vec2(dims.x - margin * 3 - max_text_width, bar_width), bar_style, layer=layer)

        if isinstance(handle_style, RectStyle):
            handle_size: vec2 = vec2(handle_size)
            handle = self._factory.shape.rect(vec2(), vec2(handle_size), handle_style, layer=layer)
        else:
            handle_size: int = handle_size if isinstance(handle_size, int) else round(length(handle_size))
            handle = self._factory.shape.circle(vec2(), handle_size, handle_style, layer=layer)

        start_value = start_value if start_value is not None else min_value
        text = self._factory.text.label(vec2(), str(start_value), font, layer=layer)

        obj = self._create_object(SliderObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar, handle, text, min_value, max_value, step)
        obj.set_fixed_width(round(dims.x)).set_fixed_height(round(dims.y))
        obj.set_cell_spacing(margin, True)
        obj.set_fixed_col_width(round(max_text_width + margin * 0.5), 0 if slider_style.text_position.lower() in ["left", "l"] else 1)

        obj.set_object_in_cell(bar, 1 if slider_style.text_position.lower() in ["left", "l"] else 0, 0)
        obj.set_object_in_cell(text, 0 if slider_style.text_position.lower() in ["left", "l"] else 1, 0)

        if slider_style.hide_bg:
            obj.skip_rendering()

        if start_value is not None:
            obj.value = start_value
        else:
            obj.value = min_value

        return obj

    def progress_bar(
            self, position: vec2, dims: vec2, style: StyleOrName[ProgressBarStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, cache_bar: bool = False
    ) -> ProgressBarObject:
        """
        Create a progress bar filled from the left according to its value.

        :param position: World-space position of the object.
        :param dims: Dimensions of the progress bar.
        :param style: Progress bar style or registered style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :param cache_bar: Whether to cache the bar surface.
        :return: The created progress bar object.
        """

        progress_bar_style = self._get_resource(style, ProgressBarStyle)
        bg_style = progress_bar_style.bg_style
        bar_style = RectStyle(progress_bar_style.color, bd_radius=bg_style.inset_bd_radius())

        bar = self._factory.shape.rect(vec2(), vec2(0, dims.y), bar_style, 0.0, 1.0, layer, Anchor.C, cache_bar)
        obj = self._create_object(ProgressBarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, bar)

        return obj

    def line_chart(
            self, position: vec2, dims: vec2, style: StyleOrName[LineChartStyle] = None, pad_x=0, pad_y=0, min_x=None, max_x=None, min_y=None, max_y=None,
            max_data_points=None, max_data_x_range=None, update_action: Callback[[PygameObject], Any] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True, cache_line: bool = False
    ) -> LineChartObject:
        """
        Create a line chart with configurable axes, data limits, and update callback.

        :param position: World-space position of the object.
        :param dims: Dimensions of the chart.
        :param style: Line chart style or registered style name.
        :param pad_x: Horizontal padding inside the chart.
        :param pad_y: Vertical padding inside the chart.
        :param min_x: Initial minimum x-axis value.
        :param max_x: Initial maximum x-axis value.
        :param min_y: Initial minimum y-axis value.
        :param max_y: Initial maximum y-axis value.
        :param max_data_points: Maximum number of data points retained.
        :param max_data_x_range: Maximum x-value range retained.
        :param update_action: Callback invoked when the chart updates.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :param cache_line: Whether to cache the line surface.
        :return: The created line chart object.
        """

        line_chart_style = self._get_resource(style, LineChartStyle)
        bg_style = line_chart_style.bg_style
        line_style = LineStyle(line_chart_style.line_color, line_chart_style.line_width)

        line = self._factory.shape.line(vec2(), [], line_style, 0.0, 1.0, layer, Anchor.C, cache_line)
        obj: LineChartObject = self._create_object(LineChartObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, line)

        if pad_x: obj.pad_x = pad_x
        if pad_y: obj.pad_y = pad_y
        if min_x is not None: obj.min_x_value = min_x
        if min_y is not None: obj.min_y_value = min_y
        if max_x is not None: obj.max_x_value = max_x
        if max_y is not None: obj.max_y_value = max_y
        if max_data_points is not None: obj.max_data_points = max_data_points
        if max_data_x_range is not None: obj.max_data_x_range = max_data_x_range

        if update_action is not None: obj.do_on_update(update_action)

        return obj

    def scrollbar(
            self, position: vec2, dims: vec2, style: ScrollbarStyle,
            start_value: float = 0.0, handle_height: Optional[float] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ScrollbarObject:
        """
        Create a vertical scrollbar with a draggable handle.

        :param position: World-space position of the object.
        :param dims: Dimensions of the scrollbar.
        :param style: Scrollbar style or registered style name.
        :param start_value: Initial scroll value.
        :param handle_height: Height of the scrollbar handle; defaults to a fraction of the widget height.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created scrollbar object.
        """

        scrollbar_style = self._get_resource(style, ScrollbarStyle)
        bg_style = scrollbar_style.bg_style
        handle_style = scrollbar_style.handle_style

        margin = scrollbar_style.margin

        available_height = max(1.0, dims.y - margin * 2)
        handle_height = clamp(handle_height if handle_height is not None else dims.y * 0.2, 1.0, available_height)

        handle = self._factory.shape.rect(vec2(), vec2(dims.x - margin * 2, handle_height), handle_style, layer=layer)

        obj = self._create_object(ScrollbarObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, handle)

        obj.value = start_value

        return obj

    def value_selector(
            self, position: vec2, dims: vec2, start_value: float = 0, min_value: float = 0, max_value: float = inf,
            increments: Optional[list[float] | tuple[float, ...]] = None, callback: Callback[[float], Any] = None,
            style: StyleOrName[ValueSelectorStyle] = None, rotation: float = 0.0, scale: float = 1.0,
            layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ValueSelectorObject:
        """
        Create a value selector with decrement buttons, a value label, and increment buttons.

        :param position: World-space position of the object.
        :param dims: Dimensions of the selector.
        :param start_value: Initial value, clamped to the allowed range.
        :param min_value: Minimum allowed value.
        :param max_value: Maximum allowed value.
        :param increments: Positive increments offered by the selector.
        :param callback: Callback invoked when the value changes.
        :param style: Value selector style or registered style name.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created value selector object.
        :raises ValueError: If any increment is not positive.
        """
        selector_style = self._get_resource(style, ValueSelectorStyle)
        bg_style = selector_style.bg_style
        button_style = selector_style.button_style
        font = self._get_resource(selector_style.font, Font)
        margin = selector_style.margin

        increments = tuple(increments if increments is not None else (1,))
        for inc in increments:
            if inc <= 0:
                raise ValueError("ValueSelector increments must be positive")

        dec_buttons = []
        for inc in reversed(increments):
            v_inc = int(inc) if inc == int(inc) else inc
            btn = self.button(vec2(), f"-{v_inc}", style=button_style, layer=layer, cache=cache)
            dec_buttons.append((btn, inc))

        start_val = clamp(start_value, min_value, max_value)
        text = self._factory.text.label(vec2(), str(start_val), font, layer=layer, cache=cache)

        inc_buttons = []
        for inc in increments:
            v_inc = int(inc) if inc == int(inc) else inc
            btn = self.button(vec2(), f"+{v_inc}", style=button_style, layer=layer, cache=cache)
            inc_buttons.append((btn, inc))

        obj = self._create_object(
            ValueSelectorObject, position, rotation, scale, RectRenderer(dims, bg_style, cache),
            layer, anchor, text, min_value, max_value, increments, start_val, callback
        )

        for btn, inc in dec_buttons:
            btn.do_on_click(1, lambda _, i=inc: obj.decrement(i))
        for btn, inc in inc_buttons:
            btn.do_on_click(1, lambda _, i=inc: obj.increment(i))

        col_idx = 0
        for btn, _ in dec_buttons:
            obj.set_object_in_cell(btn, col_idx, 0)
            col_idx += 1

        value_col_idx = col_idx
        obj.set_object_in_cell(text, value_col_idx, 0)
        col_idx += 1

        for btn, _ in inc_buttons:
            obj.set_object_in_cell(btn, col_idx, 0)
            col_idx += 1

        obj.set_fixed_width(round(dims.x)).set_fixed_height(round(dims.y))
        obj.set_cell_spacing(margin, True)

        if selector_style.value_width is not None:
            obj.set_fixed_col_width(selector_style.value_width, value_col_idx)
        else:
            if max_value != inf:
                val_w = font.get_render_size(str(max_value))[0]
            else:
                val_w = font.get_render_size(str(start_val))[0]
            obj.set_min_col_width(round(val_w), value_col_idx)

        if selector_style.hide_bg:
            obj.skip_rendering()

        return obj

    def value_cycler(
            self, position: vec2, dims: vec2, values: tuple[Any, ...] | list[Any], default_index: int = 0,
            callback: Callback[[Any], Any] = None, style: StyleOrName[ValueCyclerStyle] = None,
            previous_icon: str = Icons.CHEVRON_LEFT, next_icon: str = Icons.CHEVRON_RIGHT,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ValueCyclerObject:
        """
        Create a value cycler with previous and next icon buttons.

        :param position: World-space position of the object.
        :param dims: Dimensions of the value cycler.
        :param values: Values the cycler can display.
        :param default_index: Index of the initially selected value.
        :param callback: Callback invoked when the selected value changes.
        :param style: Value cycler style or registered style name.
        :param previous_icon: Icon identifier for the previous-value button.
        :param next_icon: Icon identifier for the next-value button.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created value cycler object.
        :raises ValueError: If ``values`` is empty.
        :raises ValueError: If ``default_index`` is outside the range of ``values``.
        """
        vals = tuple(values)
        if not vals:
            raise ValueError("ValueCycler requires at least one value")
        if not (0 <= default_index < len(vals)):
            raise ValueError(f"Default index {default_index} out of range for values of length {len(vals)}")

        cycler_style = self._get_resource(style, ValueCyclerStyle)
        bg_style = cycler_style.bg_style
        icon_btn_style = cycler_style.icon_button_style
        font = self._get_resource(cycler_style.font, Font)
        margin = cycler_style.margin
        icon_size = cycler_style.icon_size

        prev_btn = self.icon_button(vec2(), previous_icon, icon_size, style=icon_btn_style, layer=layer, cache=cache)
        next_btn = self.icon_button(vec2(), next_icon, icon_size, style=icon_btn_style, layer=layer, cache=cache)

        default_val = vals[default_index]
        text = self._factory.text.label(vec2(), str(default_val), font, layer=layer, cache=cache)

        obj = self._create_object(
            ValueCyclerObject, position, rotation, scale, RectRenderer(dims, bg_style, cache),
            layer, anchor, text, vals, default_index, callback
        )

        prev_btn.do_on_click(1, lambda _: obj.cycle_backward())
        next_btn.do_on_click(1, lambda _: obj.cycle_forward())

        obj.set_object_in_cell(prev_btn, 0, 0)
        obj.set_object_in_cell(text, 1, 0)
        obj.set_object_in_cell(next_btn, 2, 0)

        obj.set_fixed_width(round(dims.x)).set_fixed_height(round(dims.y))
        obj.set_cell_spacing(margin, True)

        if cycler_style.value_width is not None:
            obj.set_fixed_col_width(cycler_style.value_width, 1)
        else:
            max_val_str = max((str(v) for v in vals), key=len)
            val_w = font.get_render_size(max_val_str)[0]
            obj.set_min_col_width(round(val_w), 1)

        if cycler_style.hide_bg:
            obj.skip_rendering()

        return obj

    # endregion
    
