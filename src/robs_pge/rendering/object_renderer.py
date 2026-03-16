from typing import Optional

from .draw_commands import DrawCircle, DrawLine, DrawRect, DrawText, DrawTexture, RectStyle
from .styles import *
from ..resources import Texture
from ..utils import Anchor, Color, Font, Transform, Vec2


class ObjectRenderer:
    def __init__(self, cache=True):
        self._cache = cache
    
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


class RectRenderer(ObjectRenderer):
    def __init__(self, dims: Vec2, style: Optional[RectStyle] = None, cache=True):
        super().__init__(cache)

        self._dims = dims
        
        self._style = (style or RectStyle()).copy()
        
    # region PROPERTIES
    
    # region style
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, value: RectStyle):
        self._style = value
    # endregion
    
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
        return self.style.bg_color
    
    @bg_color.setter
    def bg_color(self, value):
        self.style.bg_color = value
    # endregion
    
    # region bd
    @property
    def bd(self):
        return self.style.bd
    
    @bd.setter
    def bd(self, value):
        self.style.bd = value
    # endregion
    
    # region bd_color
    @property
    def bd_color(self):
        return self.style.bd_color
    
    @bd_color.setter
    def bd_color(self, value):
        self.style.bd_color = value
    # endregion
    
    # region bd_radius
    @property
    def bd_radius(self):
        return self.style.bd_radius
    
    @bd_radius.setter
    def bd_radius(self, value):
        self.style.bd_radius = value
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
        submit(DrawRect(transform, layer, anchor, self._cache, self.dims, self.style))


class CircleRenderer(ObjectRenderer):
    def __init__(self, radius: int, style: Optional[CircleStyle] = None, cache=True):
        super().__init__(cache)

        self._radius = radius
        
        self._style = (style or CircleStyle()).copy()
    
    # region PROPERTIES
    
    # region style
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, value: CircleStyle):
        self._style = value
    # endregion
    
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
        return self.style.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        self.style.bg_color = value
    # endregion
    
    # region bd
    @property
    def bd(self):
        return self.style.bd
    
    @bd.setter
    def bd(self, value: int):
        self.style.bd = value
    # endregion
    
    # region bd_color
    @property
    def bd_color(self):
        return self.style.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        self.style.bd_color = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        return self.diameter
    
    def test_hit(self, local_pos: Vec2):
        pos = local_pos - self.get_offset(Anchor.C)
        return pos.length_squared() <= self.radius ** 2
    
    def render(self, submit, transform: Transform, layer: int, anchor: Vec2):
        submit(DrawCircle(transform, layer, anchor, self._cache, self.radius, self.style))


class LineRenderer(ObjectRenderer):
    def __init__(self, points: list[Vec2], style: Optional[LineStyle]=None, cache=True):
        super().__init__(cache)

        self._points = points
        
        self._max_x = max(p.x for p in points)
        self._max_y = max(p.y for p in points)
        
        self._style = (style or LineStyle()).copy()
    
    # region PROPERTIES
    
    @property
    def dims(self):
        return Vec2(self._max_x, self._max_y)
    
    # region points
    @property
    def points(self):
        return self._points
    
    @points.setter
    def points(self, value: list[Vec2]):
        self._points = value
        self._max_x = max(p.x for p in value)
        self._max_y = max(p.y for p in value)
    # endregion
    
    # region style
    @property
    def style(self):
        return self._style
    
    @style.setter
    def style(self, value: LineStyle):
        self._style = value
    # endregion
    
    # region color
    @property
    def color(self):
        return self.style.color
    
    @color.setter
    def color(self, value: Color):
        self.style.color = value
    # endregion
    
    # region width
    @property
    def width(self):
        return self.style.width
    
    @width.setter
    def width(self, value):
        self.style.width = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        return Vec2(self._max_x, self._max_y).length() * 2 if rotation else Vec2(self._max_x, self._max_y) * 2
    
    def test_hit(self, local_pos: Vec2):
        return False
    
    
    def render(self, submit, transform: Transform, layer: int, anchor: Vec2):
        submit(DrawLine(transform, layer, anchor, self._cache, self.points, self.style))


class SpriteRenderer(ObjectRenderer):
    def __init__(self, texture: Texture, cache=True):
        super().__init__(cache)

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
        submit(DrawTexture(transform, layer, anchor, self._cache, self.texture))


class TextRenderer(ObjectRenderer):
    def __init__(self, text: str, font: Optional[Font]=None, cache=True):
        super().__init__(cache)

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
        submit(DrawText(transform, layer, anchor, self._cache, self.text, self.font))