from __future__ import annotations
from ..utils import Transform, Vec2, FRect
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..objects import Layer



class ObjectRenderer:
    def __init__(self, cache=True):
        self._cache = cache
    
    # region PROPERTIES
    @property
    def dims(self) -> Vec2:
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
    
    def get_aabb_size(self, rotation: float) -> Vec2:
        return Vec2(self.dims.length()) if rotation else self.dims
    
    def get_bounding_radius(self) -> float:
        return self.dims.length() * 0.5
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: Vec2, clip_area: Optional[FRect] = None) -> None:
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

