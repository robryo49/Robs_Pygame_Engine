from __future__ import annotations

from typing import cast

from ..object import PygameObject
from ...rendering import CircleRenderer, LineRenderer, RectRenderer, TextRenderer
from ...utils import Anchor, Color, DictCollection, Transform, Vec2


class RectObject(PygameObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> RectRenderer:
        return cast(RectRenderer, self._renderer)
    
    
    @property
    def dims(self):
        return self.renderer.dims
    
    @dims.setter
    def dims(self, value: Vec2):
        self.renderer.dims = value
    
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
    
    
    @property
    def height(self):
        return self.renderer.height
    
    @height.setter
    def height(self, value: int):
        self.renderer.height = value
    
    
    @property
    def bg_color(self):
        return self.renderer.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        self.renderer.bg_color = value
    
    
    @property
    def bd(self):
        return self.renderer.bd
    
    @bd.setter
    def bd(self, value: int):
        self.renderer.bd = value
    
    
    @property
    def bd_color(self):
        return self.renderer.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        self.renderer.bd_color = value
    
    
    @property
    def bd_radius(self):
        return self.renderer.bd_radius
    
    @bd_radius.setter
    def bd_radius(self, value: int):
        self.renderer.bd_radius = value
    
    # endregion


class CircleObject(PygameObject):
    def __init__(self, transform: Transform, renderer: CircleRenderer, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> CircleRenderer:
        return cast(CircleRenderer, self._renderer)
    
    
    @property
    def dims(self):
        return self.renderer.dims
    
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
    
    
    @property
    def height(self):
        return self.renderer.height
    
    @height.setter
    def height(self, value):
        self.renderer.height = value
    
    
    @property
    def diameter(self):
        return self.renderer.diameter
    
    @diameter.setter
    def diameter(self, value: int):
        self.renderer.diameter = value
    
    
    @property
    def radius(self):
        return self.renderer.radius
    
    @radius.setter
    def radius(self, value: int):
        self.renderer.radius = value
    
    
    @property
    def bg_color(self):
        return self.renderer.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        self.renderer.bg_color = value
    
    
    @property
    def bd_color(self):
        return self.renderer.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        self.renderer.bd_color = value
    
    
    @property
    def bd(self):
        return self.renderer.bd
    
    @bd.setter
    def bd(self, value: int):
        self.renderer.bd = value
    
    # endregion


class LineObject(PygameObject):
    def __init__(self, transform: Transform, renderer: LineRenderer, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> LineRenderer:
        return cast(LineRenderer, self._renderer)
    
    
    @property
    def points(self):
        return self.renderer.points
    
    @points.setter
    def points(self, value: list[Vec2]):
        self.renderer.points = value
    
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
    
    
    @property
    def color(self):
        return self.renderer.color
    
    @color.setter
    def color(self, value: Color):
        self.renderer.color = value
    
    # endregion


class TextObject(PygameObject):
    def __init__(self, transform: Transform, renderer: TextRenderer, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> TextRenderer:
        return cast(TextRenderer, self._renderer)
    
    @property
    def text(self):
        return self.renderer.text
    
    @text.setter
    def text(self, value: str):
        self.renderer.text = value
    
    # endregion

