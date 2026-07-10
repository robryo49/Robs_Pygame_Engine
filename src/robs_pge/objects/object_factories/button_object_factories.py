from typing import Callable, Any, Optional

from .sub_factory import SubObjectFactory

from ..custom import *

from ...resources import Texture
from ...rendering import RectRenderer, SpriteButtonStyle, ButtonStyle, IconButtonStyle
from ...utils import Vec2, Anchor



class ButtonObjectFactory(SubObjectFactory):
    def make_button(
            self, position: Vec2, text: str, action: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[ButtonStyle | str] = None,
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
    
    def make_value_switching_button(
            self, position: Vec2, texts: tuple[str, ...], values: Optional[tuple[Any, ...]] = None, default_index: int = 0, callback: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[ButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ValueSwitchingButtonObject:
        
        if values is None:
            values = texts
        
        text = texts[default_index]
        
        button_style = self._get_resource(style, ButtonStyle)
        bg_style = button_style.bg_style
        margin = Vec2(button_style.margin)
        font = button_style.font
        text_dims = [font.get_render_size(t) for t in texts]
        dims = dims or Vec2(max(d[0] for d in text_dims), max(d[1] for d in text_dims)) + Vec2(margin*2)
        
        obj = self._make_object(ValueSwitchingButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor,
                                self.factory.text.make_text(Vec2(), text, font, 0.0, 1.0, layer, Anchor.C, cache), texts, values, callback
                                )
        
        return obj
    
    def make_sprite_button(
            self, position: Vec2, texture: Texture, action: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[SpriteButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        button_style = self._get_resource(style, SpriteButtonStyle)
        bg_style = button_style.bg_style
        margin = Vec2(button_style.margin)
        
        sprite = self.factory.make_sprite.make_sprite(Vec2(), texture)
        
        dims = dims or texture.dims + Vec2(margin*2)
        
        obj = self._make_object(SpriteButtonObject, position, rotation, scale, RectRenderer(dims, bg_style, cache), layer, anchor, sprite, action)
        
        return obj
    
    def make_icon_button(
            self, position: Vec2, icon: str, icon_size: int, action: Optional[Callable | tuple[Callable, ...]] = None, dims: Optional[Vec2] = None, style: Optional[IconButtonStyle | str] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 0, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteButtonObject:
        
        icon_button_style = self._get_resource(style, IconButtonStyle)
        button_style = icon_button_style.button_style
        
        icon = Texture.icon_from_svg(icon, icon_size, icon_button_style.icon_color)
        
        return self.make_sprite_button(position, icon, action, dims, button_style, rotation, scale, layer, anchor, cache)
