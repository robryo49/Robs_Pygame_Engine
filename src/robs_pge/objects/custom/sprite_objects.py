from __future__ import annotations

from typing import TypeVar

from ..object import PygameObject
from ...rendering import ChunkedSpriteRenderer, IconRenderer, SpriteRenderer, SubSurfaceRenderer
from ...utils import Anchor, Color, DictCollection, Rect, Transform, vec2

SR = TypeVar("SR", bound=SpriteRenderer)


class SpriteObject[SR](PygameObject[SR]):
    def __init__(self, transform: Transform, renderer: SpriteRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> SR:
        return self._renderer
    
    @property
    def dims(self):
        return self.renderer.dims
    
    @property
    def width(self):
        return self.renderer.width
    
    @property
    def height(self):
        return self.renderer.height
    
    # endregion


class SubSurfaceSpriteObject(PygameObject[SubSurfaceRenderer]):
    def __init__(self, transform: Transform, renderer: SubSurfaceRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> SubSurfaceRenderer:
        return self._renderer
    
    @property
    def sub_rect(self) -> Rect:
        return self.renderer.sub_rect
    
    @sub_rect.setter
    def sub_rect(self, value: Rect):
        self.renderer.sub_rect = value
    
    def move_subrect(self, vec: vec2):
        self.sub_rect.x = self.sub_rect.x + vec.x
        self.sub_rect.y = self.sub_rect.y + vec.y
    
    @property
    def target_dims(self) -> vec2:
        return self.renderer.target_dims
    
    @target_dims.setter
    def target_dims(self, value: vec2):
        self.renderer.target_dims = value
    
    @property
    def dims(self) -> vec2:
        return self.renderer.dims
    
    @dims.setter
    def dims(self, value: vec2):
        self.renderer.target_dims = value
    
    @property
    def width(self) -> int:
        return int(self.renderer.width)
    
    @width.setter
    def width(self, value: int):
        self.renderer.width = value
    
    @property
    def height(self) -> int:
        return int(self.renderer.height)
    
    @height.setter
    def height(self, value: int):
        self.renderer.height = value
    
    # endregion


class ChunkedSpriteObject(PygameObject[ChunkedSpriteRenderer]):
    def __init__(self, transform: Transform, renderer: ChunkedSpriteRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    @property
    def renderer(self) -> ChunkedSpriteRenderer:
        return self._renderer
    
    @property
    def chunk_size(self) -> int:
        return self.renderer.chunk_size
    
    @chunk_size.setter
    def chunk_size(self, value: int):
        self.renderer.chunk_size = value
    
    @property
    def dims(self):
        return self.renderer.dims
    
    @property
    def width(self):
        return self.renderer.width
    
    @property
    def height(self):
        return self.renderer.height
    # endregion
    
    
class IconObject(SpriteObject[IconRenderer]):
    def __init__(self, transform: Transform, renderer: IconRenderer, services: DictCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C):
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> IconRenderer:
        return self._renderer
    
    # region icon
    @property
    def icon(self):
        return self.renderer.icon
    
    @icon.setter
    def icon(self, value: str):
        self.renderer.icon = value
    # endregion
    
    # region icon_size
    @property
    def icon_size(self):
        return self.renderer.icon_size
    
    @icon_size.setter
    def icon_size(self, value):
        self.renderer.icon_size = value
    # endregion
    
    # region icon_color
    @property
    def icon_color(self):
        return self.renderer.icon_color
    
    @icon_color.setter
    def icon_color(self, value: Color):
        self.renderer.icon_color = value
    # endregion
    
    # endregion
    
