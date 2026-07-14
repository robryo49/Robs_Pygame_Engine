from typing import Any, Optional

from .sub_factory import SubObjectFactory
from ..custom import *
from ..custom.ui_objects import ToggleButtonObject
from ...rendering import ButtonStyle, IconButtonStyle, RectRenderer, SpriteButtonStyle, ToggleButtonStyle
from ...resources import Icons, Texture
from ...utils import Anchor, ObjectCallbackLike, Vec2


class ButtonObjectFactory(SubObjectFactory):
    def make_button(
            self, position: Vec2, text: str, action: ObjectCallbackLike = None, dims: Optional[Vec2] = None, style: Optional[ButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ButtonObject:
        
        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = Vec2(button_style.margin)
        font = button_style.font
        dims = dims or font.get_render_size(text) + Vec2(margin*2)
        
        obj = self._make_object(ButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                self.factory.text.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), action
                                )
        
        return obj
    
    def make_cycle_button(
            self, position: Vec2, texts: tuple[str, ...], values: Optional[tuple[Any, ...]] = None, default_index: int = 0, callback: ObjectCallbackLike = None, dims: Optional[Vec2] = None, style: Optional[ButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> CycleButtonObject:
        
        if values is None:
            values = texts
        
        text = texts[default_index]
        
        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = Vec2(button_style.margin)
        font = button_style.font
        text_dims = [font.get_render_size(t) for t in texts]
        dims = dims or Vec2(max(d[0] for d in text_dims), max(d[1] for d in text_dims)) + Vec2(margin*2)
        
        obj = self._make_object(CycleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                self.factory.text.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), texts, values, callback
                                )
        
        return obj
    
    def make_sprite_button(
            self, position: Vec2, texture: Texture, action: ObjectCallbackLike = None, dims: Optional[Vec2] = None, style: Optional[SpriteButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        button_style = self._get_resource(style, SpriteButtonStyle)
        bg_style = button_style.bg_style
        margin = Vec2(button_style.margin)
        
        sprite = self.factory.sprite.make_sprite(Vec2(), texture)
        
        dims = dims or texture.dims + Vec2(margin*2)
        
        obj = self._make_object(SpriteButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, action)
        
        return obj
    
    def make_icon_button(
            self, position: Vec2, icon: str, icon_size: int, action: ObjectCallbackLike = None, dims: Optional[Vec2] = None, style: Optional[IconButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style
        
        icon = Icons.get(icon, icon_size, icon_button_style.icon_color)
        
        return self.make_sprite_button(position, icon, action, dims, button_style, rotation, scale, layer, anchor, cache)
    
    def make_checkbox(
            self, position: Vec2, icon_size, callback: ObjectCallbackLike = None, dims: Optional[Vec2] = None, checked_icon: str = Icons.CHECK, checked=False, style: Optional[IconButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> CheckBoxObject:
        
        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style
        
        bg_style = button_style.bg_style
        margin = Vec2(button_style.margin)
        
        icon = Icons.get(checked_icon, icon_size, icon_button_style.icon_color)
        sprite = self.factory.sprite.make_sprite(Vec2(), icon)
        
        dims = dims or Vec2(icon_size) + Vec2(margin*2)
        
        obj = self._make_object(CheckBoxObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, callback)
        
        if checked: obj.check()
        
        return obj
    
    def make_toggle_button(
            self, position: Vec2, dims: Vec2, toggle_width: Optional[int] = None, enabled=False, callback: ObjectCallbackLike = None, style: Optional[ToggleButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ToggleButtonObject:
        
        toggle_button_style = self._get_resource(style, ToggleButtonStyle)
        bg_style = toggle_button_style.bg_style
        toggle_style = toggle_button_style.toggle_style
        toggle_bg_color = toggle_button_style.toggle_bg_color
        
        toggle_style.bd_radius = bg_style.bd_radius-bg_style.bd
        toggle_height = dims.y - 2*bg_style.bd
        toggle_width = toggle_width or dims.x * 0.3
        
        toggle_movement_range = (bg_style.bd, dims.x - bg_style.bd - toggle_width)
        
        toggle = self.factory.shape.make_rect(Vec2(bg_style.bd, 0), Vec2(toggle_width, toggle_height), toggle_style)
        toggle_bg = self.factory.shape.make_rect(Vec2(bg_style.bd, 0), Vec2(toggle_width/2, toggle_height), toggle_style.with_(bg_color=toggle_bg_color, bd_color=toggle_bg_color))
        
        obj = self._make_object(ToggleButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, toggle, toggle_bg, toggle_movement_range, callback)
        
        if enabled: obj.enable()
        
        return obj
        