from pathlib import Path
from typing import Optional
from matplotlib.colors import Colormap

import pygame as pg
import numpy as np
import math


from ..utils import Vec2, Vec2Like, colorize_array, invert_uv_y, Color, make_noise_array, normalize_array


class Texture:
    def __init__(self, surface: pg.Surface):
        self._surface = surface
        
        self._lod_surfaces: list[pg.Surface] = [surface]
        self._lod_factor = 2
    
    # region PROPERTIES
    
    @property
    def surface(self):
        return self._surface
    
    @property
    def width(self):
        return self.surface.get_width()
    
    @property
    def height(self):
        return self.surface.get_height()
    
    @property
    def dims(self):
        return Vec2(self.surface.get_size())
    
    @property
    def lod_levels(self) -> int:
        return len(self._lod_surfaces)
    
    # region lod_factor
    @property
    def lod_factor(self):
        return self._lod_factor
    
    @lod_factor.setter
    def lod_factor(self, value: float):
        self._lod_factor = value
        self._invalidate_lod()
    # endregion
    
    # endregion
    
    def _invalidate_lod(self):
        self._lod_surfaces = [self._surface]
    
    def _extend_lod_to(self, level: int):
        while len(self._lod_surfaces) <= level:
            prev = self._lod_surfaces[-1]
            w, h = prev.get_size()
            if w <= 1 and h <= 1:
                break
            self._lod_surfaces.append(pg.transform.smoothscale(prev, (max(1, w // self.lod_factor), max(1, h // self.lod_factor))))
    
    def get_lod_surface(self, scale: float) -> tuple[pg.Surface, int]:
        
        if scale <= 0 or scale >= 1:
            return self._surface, 1
        
        level = max(0, int(math.floor(round(math.log(1.0 / scale, self.lod_factor), 2))))
        
        self._extend_lod_to(level)
        level = min(level, len(self._lod_surfaces) - 1)
        
        return self._lod_surfaces[level], level
    
    def pregenerate_lods(self, scale):
        self.get_lod_surface(scale)
    
    
    def get_at_uv(self, uv: Vec2):
        pos = self.dims.elementwise() * invert_uv_y(uv)
        return self.get_at_pos(pos)
    
    def get_at_pos(self, pos: Vec2):
        x, y = pos.x, self.height - pos.y
        try:
            return self.surface.get_at((x, y))
        except IndexError:
            return Color(0, 0, 0, 0)
    
    @staticmethod
    def _get_dims(surface, dims: Optional[Vec2Like]=None, width: Optional[int]=None, height: Optional[int]=None):
        w, h = dims or (None, None)
        w = width or w
        h = height or h
        
        ratio = (w / h) if w and h else surface.get_width() / surface.get_height()
        
        w = (h * ratio) if not w and h else w
        h = (w / ratio) if not h and w else h
        
        return Vec2(w, h)
    
    def resize(self, dims=None, width=None, height=None):
        if dims or width or height:
            dims = self._get_dims(self.surface, dims, width, height)
            self._surface = pg.transform.scale(self.surface, dims)
            self._invalidate_lod()
        return self
    
    def resized(self, dims: Optional[Vec2] = None, width: Optional[int] = None, height: Optional[int] = None):
        return self.copy().resize(dims, width, height)
            
    def copy(self):
        return self.from_surface(self.surface.copy())
    
    @classmethod
    def from_surface(cls, surface: pg.Surface, dims: Optional[Vec2]=None, width: Optional[int]=None, height: Optional[int]=None):
        texture = cls(surface.convert_alpha())
        texture.resize(dims, width, height)
        return texture
    
    @classmethod
    def from_path(cls, path: Path, dims: Optional[Vec2] = None, width: Optional[int] = None, height: Optional[int] = None):
        return cls.from_surface(pg.image.load(path), dims, width, height)
    
    @classmethod
    def from_color_array(cls, arr: np.ndarray, dims: Optional[Vec2]=None, width: Optional[int]=None, height: Optional[int]=None):
        if not np.issubdtype(arr.dtype, np.integer):
            if arr.max() <= 1.0 and arr.min() >= 0.0:
                arr = arr * 255.0
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        elif arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        
        if arr.ndim == 2:
            arr = np.stack([arr] * 3, axis=-1)
        
        if arr.ndim == 3 and arr.shape[2] == 3:
            alpha = np.full((arr.shape[0], arr.shape[1], 1), 255, dtype=np.uint8)
            arr = np.concatenate([arr, alpha], axis=-1)
        
        h, w = arr.shape[:2]
        
        surface = pg.image.frombuffer(
            np.ascontiguousarray(arr).tobytes(),
            (w, h),
            "RGBA"
        )
        
        return cls.from_surface(surface, dims, width, height)
    
    @classmethod
    def from_grayscale_array(cls, arr: np.ndarray, normalize: bool | tuple[float, float]=False, cmap: str | Colormap="binary", dims: Optional[Vec2]=None, width: Optional[int]=None, height: Optional[int]=None):
        
        if normalize:
            min_v, max_v = (arr.min(), arr.max()) if normalize is True else normalize
            arr = normalize_array(arr, min_v, max_v)
        
        if not np.issubdtype(arr.dtype, np.integer):
            if arr.max() > 1.0:
                arr = np.clip(arr / 255.0, 0.0, 1.0)
        else:
            if cmap != "binary":
                arr = arr.astype(np.float32) / 255.0
        
        if cmap != "binary":
            arr = colorize_array(arr, cmap=cmap)
        else:
            if not np.issubdtype(arr.dtype, np.integer):
                arr = np.clip(arr, 0.0, 1.0)
                arr = (arr * 255).astype(np.uint8)
            arr = np.stack([arr] * 3, axis=-1)
        
        return cls.from_color_array(arr, dims, width, height)
    
    @classmethod
    def from_array(cls, arr: np.ndarray, normalize: bool | tuple[float, float]=False, cmap: str | Colormap="binary", dims: Optional[Vec2]=None, width: Optional[int]=None, height: Optional[int]=None):
        if len(arr.shape) == 3: return cls.from_color_array(arr, dims, width, height)
        if len(arr.shape) == 2: return cls.from_grayscale_array(arr, normalize, cmap, dims, width, height)
        raise ValueError("arr given isn't grayscale or color, shape :" + str(arr.shape))
    
    @classmethod
    def from_noise(cls, dims: Vec2 | tuple[int, int], noise_offset: Vec2 | tuple[int, int] = (0, 0), seed: Optional[int] = None, scale: float = 1, amplitude: float = 1, value_offset: float = 0, octaves: int = 8, persistence: float = 0.5, lacunarity: float = 2.0, cmap="binary"):
        return cls.from_grayscale_array(make_noise_array(dims, noise_offset, seed, scale, amplitude, value_offset, octaves, persistence, lacunarity), cmap=cmap)
    
    