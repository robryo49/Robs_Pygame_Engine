"""Sprite-backed pygame objects for static, subsurface, chunked, and icon rendering."""

from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from ..object import PygameObject
from ...rendering import ChunkedSpriteRenderer, IconRenderer, SpriteRenderer, SubSurfaceRenderer
from ...utils import Anchor, Color, Rect, Transform, vec2

if TYPE_CHECKING:
    from ...core import ServicesCollection

SR = TypeVar("SR", bound=SpriteRenderer)


class SpriteObject[SR](PygameObject[SR]):
    """Pygame object backed by a generic SpriteRenderer."""
    def __init__(self, transform: Transform, renderer: SpriteRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the sprite object.

        :param transform: Transform applied to the object.
        :param renderer: Sprite renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> SR:
        """Return the sprite renderer."""
        return self._renderer
    
    @property
    def dims(self):
        """Return the sprite dimensions."""
        return self.renderer.dims
    
    @property
    def width(self):
        """Return the sprite width."""
        return self.renderer.width
    
    @property
    def height(self):
        """Return the sprite height."""
        return self.renderer.height
    
    # endregion


class SubSurfaceSpriteObject(PygameObject[SubSurfaceRenderer]):
    """Pygame object that renders a movable sub-rectangle of a larger sprite."""
    def __init__(self, transform: Transform, renderer: SubSurfaceRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the subsurface sprite object.

        :param transform: Transform applied to the object.
        :param renderer: Subsurface renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> SubSurfaceRenderer:
        """Return the subsurface renderer."""
        return self._renderer
    
    @property
    def sub_rect(self) -> Rect:
        """Return the source rectangle drawn from the sprite."""
        return self.renderer.sub_rect
    
    @sub_rect.setter
    def sub_rect(self, value: Rect):
        """
        Set the source rectangle drawn from the sprite.

        :param value: The new source rectangle drawn from the sprite.
        """
        self.renderer.sub_rect = value
    
    def move_subrect(self, vec: vec2):
        """
        Move the source rectangle by the given offset.

        :param vec: Offset added to the source rectangle position.
        """
        self.sub_rect.x = self.sub_rect.x + vec.x
        self.sub_rect.y = self.sub_rect.y + vec.y
    
    @property
    def target_dims(self) -> vec2:
        """Return the target dimensions of the subsurface."""
        return self.renderer.target_dims
    
    @target_dims.setter
    def target_dims(self, value: vec2):
        """
        Set the target dimensions of the subsurface.

        :param value: The new target dimensions of the subsurface.
        """
        self.renderer.target_dims = value
    
    @property
    def dims(self) -> vec2:
        """Return the rendered subsurface dimensions."""
        return self.renderer.dims
    
    @dims.setter
    def dims(self, value: vec2):
        """
        Set the target dimensions of the subsurface.

        :param value: The new target dimensions of the subsurface.
        """
        self.renderer.target_dims = value
    
    @property
    def width(self) -> int:
        """Return the rendered subsurface width."""
        return int(self.renderer.width)
    
    @width.setter
    def width(self, value: int):
        """
        Set the rendered subsurface width.

        :param value: The new rendered subsurface width.
        """
        self.renderer.width = value
    
    @property
    def height(self) -> int:
        """Return the rendered subsurface height."""
        return int(self.renderer.height)
    
    @height.setter
    def height(self, value: int):
        """
        Set the rendered subsurface height.

        :param value: The new rendered subsurface height.
        """
        self.renderer.height = value
    
    # endregion


class ChunkedSpriteObject(PygameObject[ChunkedSpriteRenderer]):
    """Pygame object backed by a ChunkedSpriteRenderer with configurable chunk size."""
    def __init__(self, transform: Transform, renderer: ChunkedSpriteRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the chunked sprite object.

        :param transform: Transform applied to the object.
        :param renderer: Chunked sprite renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    @property
    def renderer(self) -> ChunkedSpriteRenderer:
        """Return the chunked sprite renderer."""
        return self._renderer
    
    @property
    def chunk_size(self) -> int:
        """Return the chunk size."""
        return self.renderer.chunk_size
    
    @chunk_size.setter
    def chunk_size(self, value: int):
        """
        Set the chunk size.

        :param value: The new chunk size.
        """
        self.renderer.chunk_size = value
    
    @property
    def dims(self):
        """Return the sprite dimensions."""
        return self.renderer.dims
    
    @property
    def width(self):
        """Return the sprite width."""
        return self.renderer.width
    
    @property
    def height(self):
        """Return the sprite height."""
        return self.renderer.height
    # endregion
    
    
class IconObject(SpriteObject[IconRenderer]):
    """Sprite object using an IconRenderer with configurable icon, size, and color."""
    def __init__(self, transform: Transform, renderer: IconRenderer, services: ServicesCollection, sub_layer: int = 0, anchor: vec2 = Anchor.C) -> None:
        """
        Initialize the icon object.

        :param transform: Transform applied to the object.
        :param renderer: Icon renderer used by the object.
        :param services: Service collection available to the object.
        :param sub_layer: Sub-layer used for draw ordering.
        :param anchor: Anchor point of the object.
        """
        super().__init__(transform, renderer, services, sub_layer, anchor)
    
    # region PROPERTIES
    
    @property
    def renderer(self) -> IconRenderer:
        """Return the icon renderer."""
        return self._renderer
    
    # region icon
    @property
    def icon(self):
        """Return the icon name."""
        return self.renderer.icon
    
    @icon.setter
    def icon(self, value: str):
        """
        Set the icon name.

        :param value: The new icon name.
        """
        self.renderer.icon = value
    # endregion
    
    # region icon_size
    @property
    def icon_size(self):
        """Return the icon size."""
        return self.renderer.icon_size
    
    @icon_size.setter
    def icon_size(self, value):
        """
        Set the icon size.

        :param value: The new icon size.
        """
        self.renderer.icon_size = value
    # endregion
    
    # region icon_color
    @property
    def icon_color(self):
        """Return the icon color."""
        return self.renderer.icon_color
    
    @icon_color.setter
    def icon_color(self, value: Color):
        """
        Set the icon color.

        :param value: The new icon color.
        """
        self.renderer.icon_color = value
    # endregion
    
    # endregion
    
