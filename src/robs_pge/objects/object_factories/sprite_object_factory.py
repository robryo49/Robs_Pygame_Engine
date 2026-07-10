from typing import Optional

from .sub_factory import SubObjectFactory
from ..custom import SpriteObject, SubSurfaceSpriteObject, ChunkedSpriteObject
from ...rendering import ChunkedSpriteRenderer, SpriteRenderer, SubSurfaceRenderer
from ...resources import Texture
from ...utils import Anchor, Rect, Vec2


class SpriteObjectFactory(SubObjectFactory):
    
    def make_sprite(
            self, position: Vec2, texture: Texture | str,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SpriteObject:
        
        texture = self._get_resource(texture, Texture)
        obj = self._make_object(SpriteObject, position, rotation, scale, SpriteRenderer(texture, cache), layer, anchor)
        
        return obj
    
    
    def make_subsurface_sprite(
            self, position: Vec2, texture: Texture | str, sub_rect: Optional[Rect] = None, target_dims: Optional[Vec2] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> SubSurfaceSpriteObject:
        
        texture = self._get_resource(texture, Texture)
        if target_dims is None: target_dims = Vec2(texture.dims)
        if sub_rect is None: sub_rect = Rect(0, 0, target_dims.x, target_dims.y)
        
        obj = self._make_object(SubSurfaceSpriteObject, position, rotation, scale, SubSurfaceRenderer(texture, sub_rect, target_dims, cache), layer, anchor)
        
        return obj
    
    def make_chunked_sprite(
            self, position: Vec2, texture: Texture | str, chunk_size: int = 256,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: Vec2 = Anchor.C, cache: bool = True
    ) -> ChunkedSpriteObject:
        
        texture = self._get_resource(texture, Texture)
        obj = self._make_object(ChunkedSpriteObject, position, rotation, scale, ChunkedSpriteRenderer(texture, chunk_size, cache), layer, anchor)
        
        return obj

