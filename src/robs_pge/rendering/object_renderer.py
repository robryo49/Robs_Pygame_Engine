from typing import Optional

from .draw_commands import DrawCircle, DrawRect, DrawText, DrawTexture, RectStyle
from .styles import *
from ..resources import Texture
from ..utils import Anchor, Color, Font, Transform, Vec2


class ObjectRenderer:
    
    # region PROPERTIES
    @property
    def dims(self):
        raise NotImplementedError
    
    @property
    def width(self):
        raise NotImplementedError
    
    @width.setter
    def width(self, value: int):
        raise NotImplementedError
    
    @property
    def height(self):
        raise NotImplementedError
    
    @height.setter
    def height(self, value: int):
        raise NotImplementedError
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        raise NotImplementedError
    
    def render(self, submit, transform: Transform, layer: int, anchor: Vec2) -> None:
        raise NotImplementedError
    
    def test_hit(self, local_pos: Vec2) -> bool:
        raise NotImplementedError
    
    def get_offset(self, anchor: Vec2) -> Vec2:
        return self.uv_to_local(anchor)
    
    def uv_to_local(self, uv: Vec2):
        return uv.elementwise() * self.dims
    
    def local_to_uv(self, local: Vec2):
        return local.elementwise() / self.dims
    
    def update(self, dt: float):
        pass


class RectShape(ObjectRenderer):
    def __init__(self, dims: Vec2, style: Optional[RectStyle]=None):
        self._dims = dims
        
        style = style or RectStyle()
        
        self._bg_color = style.bg_color
        self._bd = style.bd
        self._bd_color = style.bd_color
        self._bd_radius = style.bd_radius
        
    # region PROPERTIES
    
    # region dims
    @property
    def dims(self):
        return self._dims
    
    @dims.setter
    def dims(self, value: Vec2):
        self._dims = value
        
    @property
    def width(self):
        return self.dims.x
    
    @width.setter
    def width(self, value: int):
        self.dims.x = value
    
    @property
    def height(self):
        return self.dims.y
    
    @height.setter
    def height(self, value: int):
        self.dims.y = value
    
    # endregion
    
    # region bg_color
    @property
    def bg_color(self):
        return self._bg_color
    
    @bg_color.setter
    def bg_color(self, value):
        self._bg_color = value
    # endregion
    
    # region bd
    @property
    def bd(self):
        return self._bd
    
    @bd.setter
    def bd(self, value):
        self._bd = value
    # endregion
    
    # region bd_color
    @property
    def bd_color(self):
        return self._bd_color
    
    @bd_color.setter
    def bd_color(self, value):
        self._bd_color = value
    # endregion
    
    # region bd_radius
    @property
    def bd_radius(self):
        return self._bd_radius
    
    @bd_radius.setter
    def bd_radius(self, value):
        self._bd_radius = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        return Vec2(self.dims.length()) if rotation else self.dims
    
    def test_hit(self, local_pos: Vec2):
        hw, hh = self.dims/2
        r = self.bd_radius
        
        x, y = local_pos
        x, y = abs(x - hw), abs(y - hh)
        
        if x > hw or y > hh:
            return False
        if x < hw - r or y < hh - r:
            return True
        
        x, y = x - (hw - r), y - (hh - r)
        
        return x**2 + y**2 <= r**2
        

    def render(self, submit, transform: Transform, layer: int, anchor: Vec2):
        submit(DrawRect(transform, self.dims, RectStyle(self.bg_color, self.bd, self.bd_color, self.bd_radius), layer, anchor))


class SpriteRenderer(ObjectRenderer):
    def __init__(self, texture: Texture):
        self._texture = texture
    
    # region PROPERTIES
    
    @property
    def texture(self):
        return self._texture
    
    # region dims
    @property
    def dims(self):
        return self.texture.dims
    
    @property
    def width(self):
        return self.texture.width
    
    @property
    def height(self):
        return self.texture.height
    
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        return Vec2(self.dims.length()) if rotation else self.dims
    
    def test_hit(self, local_pos: Vec2):
        
        x, y = local_pos
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        return self.texture.get_at_pos(local_pos).a > 0
    
    def render(self, submit, transform: Transform, layer: int, anchor: Vec2):
        submit(DrawTexture(transform, self.texture, layer, anchor))


class TextRenderer(ObjectRenderer):
    def __init__(self, text: str, font: Optional[Font]=None):
        self._text = text
        
        self._font = font or Font()
        
        self._dims = Vec2(self.font.get_render_size(self.text))
    
    # region PROPERTIES
    
    # region text
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        self._dims = Vec2(self.font.get_render_size(self.text))
    # endregion
    
    @property
    def font(self):
        return self._font
    
    @property
    def dims(self):
        all_dims = list(self.font.get_render_size(txt) for txt in self.text.split("\n"))
        return Vec2(max(v.x for v in all_dims), sum(v.y for v in all_dims) + self.font.line_spacing * (len(all_dims) - 1))
    
    @property
    def width(self):
        return self.dims.x
    
    @property
    def height(self):
        return self.dims.y
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        return Vec2(self.dims.length()) if rotation else self.dims
    
    def test_hit(self, local_pos: Vec2):
        x, y = local_pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def render(self, submit, transform: Transform, layer: int, anchor: Vec2):
        submit(DrawText(transform, self.text, self.font, layer, anchor))


class CircleShape(ObjectRenderer):
    def __init__(self, radius: int, style: Optional[CircleStyle] = None):
        self._radius = radius
        
        style = style or CircleStyle()
        
        self._bg_color = style.bg_color
        self._bd = style.bd
        self._bd_color = style.bd_color
    
    # region PROPERTIES
    
    # region radius
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value: int):
        self._radius = value
    
    @property
    def diameter(self):
        return self.radius * 2
    
    @diameter.setter
    def diameter(self, value: int):
        self.radius = value * 0.5
    
    @property
    def dims(self):
        return Vec2(self.diameter)
    
    @property
    def width(self):
        return self.diameter
    
    @width.setter
    def width(self, value: int):
        self.radius = value * 0.5
    
    @property
    def height(self):
        return self.diameter
    
    @height.setter
    def height(self, value: int):
        self.radius = value * 0.5
    
    # endregion
    
    # region bg_color
    @property
    def bg_color(self):
        return self._bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        self._bg_color = value
    # endregion
    
    # region bd
    @property
    def bd(self):
        return self._bd
    
    @bd.setter
    def bd(self, value: int):
        self._bd = value
    # endregion
    
    # region bd_color
    @property
    def bd_color(self):
        return self._bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        self._bd_color = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        return self.diameter
    
    def test_hit(self, local_pos: Vec2):
        pos = local_pos - self.get_offset(Anchor.C)
        return pos.length_squared() <= self.radius ** 2
    
    def render(self, submit, transform: Transform, layer: int, anchor: Vec2):
        submit(DrawCircle(transform, self.radius, CircleStyle(self.bg_color, self.bd, self.bd_color), layer, anchor))
