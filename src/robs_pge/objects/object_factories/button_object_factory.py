"""
Factories for creating button and toggle-style UI objects.
"""

from typing import Any, Optional

from .sub_factory import SubObjectFactory
from ..behaviors import MultiplyAttributeOnClickBehavior, MultiplyAttributeOnHoverBehavior, SetAttributeOnHoverBehavior, SetAttributeOnClickBehavior
from ..custom import *
from ..object import PygameObject
from ...rendering import ButtonStyle, CircleRenderer, CircleStyle, IconButtonStyle, RadioButtonStyle, RectRenderer, SpriteButtonStyle, ToggleButtonStyle
from ...resources import Icons, Texture
from ...utils import Anchor, Easing, StyleOrName, clamp, get_object_dims, vec2, Color, Font, Callback


class ButtonObjectFactory(SubObjectFactory):
    """
    Create button variants such as cycle, sprite, icon, checkbox, radio, and toggle buttons.
    """
    
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
                                self.factory.text.label(vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), action
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
                                self.factory.text.label(vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), texts, values, callback
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
        
        sprite = self.factory.sprite.regular(vec2(), texture)
        
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
        
        sprite: IconObject = self.factory.sprite.icon_object(vec2(), icon, icon_size, icon_button_style.icon_color)
        
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
        sprite = self.factory.sprite.regular(vec2(), icon)
        
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
        tick = self.factory.shape.circle(vec2(), tick_radius, CircleStyle(color), cache=cache)
        
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
        
        toggle = self.factory.shape.rect(vec2(bg_style.bd, 0), vec2(toggle_width, toggle_height), toggle_style)
        toggle_bg = self.factory.shape.rect(vec2(bg_style.bd, 0), vec2(toggle_width / 2, toggle_height), toggle_style.with_(bg_color=toggle_bg_color, bd_color=toggle_bg_color))
        
        obj = self._create_object(ToggleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, toggle, toggle_bg, toggle_movement_range, callback)
        
        if enabled: obj.enable()
        
        return obj
    
    
    def __call__(
            self, position: vec2, text: str, action: Callback[[PygameObject], Any] = None, dims: Optional[vec2] = None, width: Optional[float] = None, height: Optional[float] = None, style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ButtonObject:
        """
        Create a button; alias for :meth:`button`.

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
        return self.button(position, text, action, dims, width, height, style, rotation, scale, layer, anchor, cache)
        