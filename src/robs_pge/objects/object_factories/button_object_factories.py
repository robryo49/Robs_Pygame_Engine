from typing import Any, Callable, Optional

from .sub_factory import SubObjectFactory
from ..behaviors import MultiplyAttributeOnClickBehavior, MultiplyAttributeOnHoverBehavior, SetAttributeOnHoverBehavior, SetAttributeOnClickBehavior
from ..custom import *
from ..object import PygameObject
from ...rendering import ButtonStyle, CircleRenderer, CircleStyle, IconButtonStyle, RadioButtonStyle, RectRenderer, SpriteButtonStyle, ToggleButtonStyle
from ...resources import Icons, Texture
from ...utils import Anchor, Easing, StyleOrName, vec2, Color, Font

CallBackType = Optional[Callable | tuple[Callable, ...]]
ObjectCallBackType = Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...] | CallBackType]
BooleanCallbackType = Optional[Callable[[bool], Any] | tuple[Callable[[bool], Any]] | CallBackType]


class ButtonObjectFactory(SubObjectFactory):
    
    @staticmethod
    def _add_button_behaviors(obj: PygameObject, buttons: int | list[int], hovered_scale: float, clicked_scale: float,
                              bg_color: Optional[Color], hovered_color: Optional[Color], clicked_color: Optional[Color],
                              content_color_attribute: Optional[str], content_color: Optional[Color], hovered_content_color: Optional[Color], clicked_content_color: Optional[Color],
                              transition_duration: float):
        if hovered_scale != 1:
            obj.add_behavior(MultiplyAttributeOnHoverBehavior("scale", hovered_scale, transition_duration, Easing.EASE_IN_QUAD))
            
        if clicked_scale != 1:
            for b in buttons if isinstance(buttons, list) else [buttons]:
                obj.add_behavior(MultiplyAttributeOnClickBehavior(b, "scale", clicked_scale, transition_duration, Easing.EASE_IN_QUAD))
            
        if bg_color is not None and hovered_color is not None and hovered_color != bg_color:
            obj.add_behavior(SetAttributeOnHoverBehavior("bg_color", bg_color, hovered_color, transition_duration, Easing.EASE_IN_QUAD))
            
        if bg_color is not None and clicked_color is not None and clicked_color != hovered_color:
            for b in buttons if isinstance(buttons, list) else [buttons]:
                obj.add_behavior(SetAttributeOnClickBehavior(b, "bg_color", hovered_color, clicked_color, transition_duration, Easing.EASE_IN_QUAD))
        
        if content_color_attribute is not None and content_color is not None and hovered_content_color is not None and hovered_content_color != content_color:
            obj.add_behavior(SetAttributeOnHoverBehavior(content_color_attribute, content_color, hovered_content_color, transition_duration, Easing.EASE_IN_QUAD))
        
        if content_color_attribute is not None and content_color is not None and clicked_content_color is not None and clicked_content_color != hovered_content_color:
            obj.add_behavior(SetAttributeOnClickBehavior(1, content_color_attribute, clicked_content_color, clicked_content_color, transition_duration, Easing.EASE_IN_QUAD))
    
    
    def make_button(
            self, position: vec2, text: str, action: ObjectCallBackType = None, dims: Optional[vec2] = None, style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ButtonObject:
        
        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = vec2(button_style.margin)
        font = self._get_resource(button_style.font, Font)
        dims = dims or font.get_render_size(text) + vec2(margin*2)
        
        obj = self._make_object(ButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                self.factory.text.make_text(vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), action
                                )
        
        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   "font_color", font.color, button_style.hovered_text_color, button_style.clicked_text_color,
                                   button_style.transition_duration)
        
        return obj
    
    def make_cycle_button(
            self, position: vec2, texts: tuple[str, ...], values: Optional[tuple[Any, ...]] = None, default_index: int = 0, callback: ObjectCallBackType = None, dims: Optional[vec2] = None, style: StyleOrName[ButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> CycleButtonObject:
        
        if values is None:
            values = texts
        
        text = texts[default_index]
        
        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = vec2(button_style.margin)
        font = button_style.font
        text_dims = [font.get_render_size(t) for t in texts]
        dims = dims or vec2(max(d[0] for d in text_dims), max(d[1] for d in text_dims)) + vec2(margin*2)
        
        obj = self._make_object(CycleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                self.factory.text.make_text(vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), texts, values, callback
                                )
        
        
        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   "font_color", font.color, button_style.hovered_text_color, button_style.clicked_text_color,
                                   button_style.transition_duration)
        return obj
    
    def make_sprite_button(
            self, position: vec2, texture: Texture, action: ObjectCallBackType = None, dims: Optional[vec2] = None, style: StyleOrName[SpriteButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        button_style = self._get_resource(style, SpriteButtonStyle)
        bg_style = button_style.bg_style
        margin = vec2(button_style.margin)
        
        sprite = self.factory.sprite.make_sprite(vec2(), texture)
        
        dims = dims or texture.dims + vec2(margin*2)
        
        obj = self._make_object(SpriteButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, action)
        
        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   None, None, None, None,
                                   button_style.transition_duration)
        
        return obj
    
    def make_icon_button(
            self, position: vec2, icon: str, icon_size: int, action: ObjectCallBackType = None, dims: Optional[vec2] = None, style: StyleOrName[IconButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> IconButtonObject:
        
        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style
        bg_style = button_style.bg_style
        margin = vec2(button_style.margin)
        
        sprite: IconObject = self.factory.sprite.make_icon_object(vec2(), icon, icon_size, icon_button_style.icon_color)
        
        dims = dims or sprite.dims + vec2(margin*2)
        
        obj = self._make_object(IconButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, action)
        
        
        self._add_button_behaviors(obj, 1, button_style.hovered_scale, button_style.clicked_scale,
                                   bg_style.bg_color, button_style.hovered_color, button_style.clicked_color,
                                   None, None, None, None,
                                   button_style.transition_duration)
        
        return obj
    
    def make_checkbox(
            self, position: vec2, icon_size, dims: Optional[vec2] = None, callback: ObjectCallBackType = None, checked_icon: str = Icons.CHECK, checked=False, style: StyleOrName[IconButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> CheckBoxObject:
        
        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style
        
        bg_style = button_style.bg_style
        margin = vec2(button_style.margin)
        
        icon = Icons.get(checked_icon, icon_size, icon_button_style.icon_color)
        sprite = self.factory.sprite.make_sprite(vec2(), icon)
        
        dims = dims or vec2(icon_size) + vec2(margin*2)
        
        obj = self._make_object(CheckBoxObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, callback)
        
        if checked: obj.check()
        
        return obj
    
    def make_radio_button(
            self, position: vec2, radius: int, callback: ObjectCallBackType = None, checked=False, style: StyleOrName[RadioButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> RadioButtonObject:
        
        radio_button_style = self._get_resource(style, RadioButtonStyle)
        bg_style = radio_button_style.bg_style
        
        margin = radio_button_style.margin + bg_style.bd
        color = radio_button_style.icon_color
        
        tick = self.factory.shape.make_circle(vec2(), radius-margin, CircleStyle(color), cache=cache)
        
        obj = self._make_object(RadioButtonObject, position, rotation, scale, CircleRenderer(radius, bg_style, cache), layer, anchor, tick, callback)
        
        if checked: obj.check()
        
        return obj
    
    def make_toggle_button(
            self, position: vec2, dims: vec2, toggle_width: Optional[int] = None, enabled=False, callback: Optional[Callable[[PygameObject], Any] | tuple[Callable[[PygameObject], Any], ...]] = None, style: StyleOrName[ToggleButtonStyle] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ToggleButtonObject:
        
        toggle_button_style = self._get_resource(style, ToggleButtonStyle)
        bg_style = toggle_button_style.bg_style
        toggle_style = toggle_button_style.toggle_style
        toggle_bg_color = toggle_button_style.toggle_bg_color
        
        toggle_style.bd_radius = bg_style.bd_radius-bg_style.bd
        toggle_height = dims.y - 2*bg_style.bd
        toggle_width = toggle_width or dims.x * 0.3
        
        toggle_movement_range = (bg_style.bd, dims.x - bg_style.bd - toggle_width)
        
        toggle = self.factory.shape.make_rect(vec2(bg_style.bd, 0), vec2(toggle_width, toggle_height), toggle_style)
        toggle_bg = self.factory.shape.make_rect(vec2(bg_style.bd, 0), vec2(toggle_width/2, toggle_height), toggle_style.with_(bg_color=toggle_bg_color, bd_color=toggle_bg_color))
        
        obj = self._make_object(ToggleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, toggle, toggle_bg, toggle_movement_range, callback)
        
        if enabled: obj.enable()
        
        return obj
        