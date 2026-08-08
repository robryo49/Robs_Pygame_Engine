from typing import Optional

from .sub_factory import SubObjectFactory
from ..custom import SpriteObject, SubSurfaceSpriteObject, ChunkedSpriteObject, IconObject
from ...rendering import ChunkedSpriteRenderer, SpriteRenderer, SubSurfaceRenderer, IconRenderer
from ...resources import Texture
from ...utils import Anchor, Rect, get_object_dims, vec2, Color, Colors


class SpriteObjectFactory(SubObjectFactory):
    
    def make_sprite(
            self, position: vec2, texture: Texture | str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SpriteObject:
        
        texture = self._get_resource(texture, Texture)
        
        dims = get_object_dims(dims, width, height, texture.dims)
        if dims != texture.dims:
            texture = texture.resized(dims)
        
        obj = self._make_object(SpriteObject, position, rotation, scale, SpriteRenderer(texture, cache), layer, anchor)
        
        return obj
    
    
    def make_subsurface_sprite(
            self, position: vec2, texture: Texture | str, sub_rect: Optional[Rect] = None, target_dims: Optional[vec2] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SubSurfaceSpriteObject:
        
        texture = self._get_resource(texture, Texture)
        if target_dims is None: target_dims = vec2(texture.dims)
        if sub_rect is None: sub_rect = Rect(0, 0, target_dims.x, target_dims.y)
        
        obj = self._make_object(SubSurfaceSpriteObject, position, rotation, scale, SubSurfaceRenderer(texture, sub_rect, target_dims, cache), layer, anchor)
        
        return obj
    
    def make_chunked_sprite(
            self, position: vec2, texture: Texture | str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, chunk_size: int = 256,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ChunkedSpriteObject:
        
        texture = self._get_resource(texture, Texture)
        
        dims = get_object_dims(dims, width, height, texture.dims)
        if dims != texture.dims:
            texture = texture.resized(dims)
            
        obj = self._make_object(ChunkedSpriteObject, position, rotation, scale, ChunkedSpriteRenderer(texture, chunk_size, cache), layer, anchor)
        
        return obj
    
    def make_icon_object(
        self, position: vec2, icon: str, icon_size: int, icon_color: Color = Colors.WHITE,
        rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> IconObject:
        
        obj = self._make_object(IconObject, position, rotation, scale, IconRenderer(icon, icon_size, icon_color, cache), layer, anchor)
        
        return obj

