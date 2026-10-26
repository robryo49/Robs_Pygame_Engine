"""
Factories for creating sprite, subsurface, chunked, and icon objects.
"""

from typing import Optional

from .sub_factory import SubObjectFactory
from ..custom import SpriteObject, SubSurfaceSpriteObject, ChunkedSpriteObject, IconObject
from ...rendering import ChunkedSpriteRenderer, SpriteRenderer, SubSurfaceRenderer, IconRenderer
from ...resources import Texture
from ...utils import Anchor, Rect, get_object_dims, vec2, Color, Colors


class SpriteObjectFactory(SubObjectFactory):
    """
    Create sprite objects backed by textures, texture regions, chunked rendering, or icons.
    """
    
    def regular(
            self, position: vec2, texture: Texture | str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SpriteObject[SpriteRenderer]:
        """
        Create a sprite object from a texture, resizing the texture when dimensions differ.

        :param position: World-space position of the object.
        :param texture: Texture or registered texture name used by the sprite.
        :param dims: Target dimensions; defaults to the texture dimensions.
        :param width: Target width used when ``dims`` is not provided.
        :param height: Target height used when ``dims`` is not provided.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created sprite object.
        """
        
        texture = self._get_resource(texture, Texture)
        
        dims = get_object_dims(dims, width, height, texture.dims)
        if dims != texture.dims:
            texture = texture.resized(dims)
        
        obj = self._create_object(SpriteObject, position, rotation, scale, SpriteRenderer(texture, cache), layer, anchor)
        
        return obj
    
    
    def subsurface_sprite(
            self, position: vec2, texture: Texture | str, sub_rect: Optional[Rect] = None, target_dims: Optional[vec2] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SubSurfaceSpriteObject:
        """
        Create a sprite that renders a region of a texture into a target size.

        :param position: World-space position of the object.
        :param texture: Texture or registered texture name used by the sprite.
        :param sub_rect: Source rectangle within the texture; defaults to the target dimensions.
        :param target_dims: Dimensions of the rendered subsurface; defaults to the texture dimensions.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created subsurface sprite object.
        """
        
        texture = self._get_resource(texture, Texture)
        if target_dims is None: target_dims = vec2(texture.dims)
        if sub_rect is None: sub_rect = Rect(0, 0, target_dims.x, target_dims.y)
        
        obj = self._create_object(SubSurfaceSpriteObject, position, rotation, scale, SubSurfaceRenderer(texture, sub_rect, target_dims, cache), layer, anchor)
        
        return obj
    
    def chunked_sprite(
            self, position: vec2, texture: Texture | str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None, chunk_size: int = 256,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> ChunkedSpriteObject:
        """
        Create a sprite rendered in chunks to support very large textures.

        :param position: World-space position of the object.
        :param texture: Texture or registered texture name used by the sprite.
        :param dims: Target dimensions; defaults to the texture dimensions.
        :param width: Target width used when ``dims`` is not provided.
        :param height: Target height used when ``dims`` is not provided.
        :param chunk_size: Maximum size of each rendered chunk in pixels.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created chunked sprite object.
        """
        
        texture = self._get_resource(texture, Texture)
        
        dims = get_object_dims(dims, width, height, texture.dims)
        if dims != texture.dims:
            texture = texture.resized(dims)
            
        obj = self._create_object(ChunkedSpriteObject, position, rotation, scale, ChunkedSpriteRenderer(texture, chunk_size, cache), layer, anchor)
        
        return obj
    
    def icon_object(
        self, position: vec2, icon: str, icon_size: int, icon_color: Color = Colors.WHITE,
        rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> IconObject:
        """
        Create an object that renders a font icon.

        :param position: World-space position of the object.
        :param icon: Icon identifier.
        :param icon_size: Size of the icon in pixels.
        :param icon_color: Color applied to the icon.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created icon object.
        """
        
        obj = self._create_object(IconObject, position, rotation, scale, IconRenderer(icon, icon_size, icon_color, cache), layer, anchor)
        
        return obj
    
    
    def __call__(
            self, position: vec2, texture: Texture | str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None,
            rotation: float = 0.0, scale: float = 1.0, layer: int = 1, anchor: vec2 = Anchor.C, cache: bool = True
    ) -> SpriteObject[SpriteRenderer]:
        """
        Create a regular sprite; alias for :meth:`regular`.

        :param position: World-space position of the object.
        :param texture: Texture or registered texture name used by the sprite.
        :param dims: Target dimensions; defaults to the texture dimensions.
        :param width: Target width used when ``dims`` is not provided.
        :param height: Target height used when ``dims`` is not provided.
        :param rotation: Rotation angle in degrees.
        :param scale: Uniform scale factor.
        :param layer: Rendering layer.
        :param anchor: Anchor point used to position the object.
        :param cache: Whether to cache the rendered surface.
        :return: The created sprite object.
        """
        return self.regular(position, texture, dims, width, height, rotation, scale, layer, anchor, cache)
