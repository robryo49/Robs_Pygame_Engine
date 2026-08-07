from __future__ import annotations
from ..utils import Transform, vec2, FRect
from typing import Optional, TYPE_CHECKING

from pyglm import glm

if TYPE_CHECKING:
    from ..objects import Layer



class ObjectRenderer:
    def __init__(self, cache=True):
        self._cache = cache
        self._cached_bounding_radius: float = 0.0
        self._bounding_radius_dirty: bool = True
        self._cached_dims: Optional[vec2] = None

    # region PROPERTIES
    @property
    def dims(self) -> vec2:
        raise NotImplementedError
    
    @property
    def width(self) -> float:
        raise NotImplementedError
    
    @width.setter
    def width(self, value: int):
        raise NotImplementedError
    
    @property
    def height(self) -> float:
        raise NotImplementedError
    
    @height.setter
    def height(self, value: int):
        raise NotImplementedError
    
    # endregion
    
    def get_aabb_size(self, rotation: float) -> vec2:
        return vec2(glm.length(self.dims)) if rotation else self.dims
    
    def get_bounding_radius(self) -> float:
        dims = self.dims
        if self._bounding_radius_dirty or dims != self._cached_dims:
            self._cached_bounding_radius = glm.length(dims) * 0.5
            self._cached_dims = dims
            self._bounding_radius_dirty = False
        return self._cached_bounding_radius

    def _invalidate_bounding_radius(self):
        self._bounding_radius_dirty = True
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None) -> None:
        raise NotImplementedError
    
    def test_hit(self, local_pos: vec2) -> bool:
        raise NotImplementedError
    
    def get_offset(self, anchor: vec2) -> vec2:
        return self.uv_to_local(anchor)
    
    def uv_to_local(self, uv: vec2):
        return uv * self.dims
    
    def local_to_uv(self, local: vec2):
        return local / self.dims
    
    def update(self, dt: float):
        pass

