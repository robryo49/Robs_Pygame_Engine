"""Wraps pygame surfaces and generates lower-detail variants for scaled rendering."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pygame as pg
from matplotlib.colors import Colormap

from ..utils import Color, Vec2Like, colorize_array, create_noise_array, normalize_array, vec2


class Texture:
    """Wraps a pygame surface and lazily generates lower-detail variants."""

    def __init__(self, surface: pg.Surface) -> None:
        """
        Initialize a texture around a surface.

        :param surface: base surface used for the texture and its LOD chain
        """
        self._surface = surface
        self._lod_surfaces: list[pg.Surface] = [surface]
        self._lod_factor = 2.0

    @property
    def surface(self) -> pg.Surface:
        """Return the base surface."""
        return self._surface

    @property
    def width(self) -> int:
        """Return the width of the base surface in pixels."""
        return self.surface.get_width()

    @property
    def height(self) -> int:
        """Return the height of the base surface in pixels."""
        return self.surface.get_height()

    @property
    def dims(self) -> vec2:
        """Return the width and height of the base surface as a vector."""
        return vec2(self.surface.get_size())

    @property
    def lod_levels(self) -> int:
        """Return the number of currently generated LOD surfaces, including the base."""
        return len(self._lod_surfaces)

    @property
    def lod_factor(self) -> float:
        """Return the scale factor between successive LOD levels."""
        return self._lod_factor

    @lod_factor.setter
    def lod_factor(self, value: float) -> None:
        """
        Set the scale factor between successive LOD levels and discard cached LODs.

        :param value: new LOD scale factor
        :raises ValueError: if the factor is not greater than 1
        """
        if value <= 1:
            raise ValueError("Texture LOD factor must be greater than 1")
        self._lod_factor = value
        self._invalidate_lod()

    def _invalidate_lod(self) -> None:
        self._lod_surfaces = [self._surface]

    def _extend_lod_to(self, level: int) -> None:
        """
        Generate LOD surfaces until the requested level is available.

        :param level: zero-based LOD level to extend to
        """
        while len(self._lod_surfaces) <= level:
            previous = self._lod_surfaces[-1]
            width, height = previous.get_size()
            if width <= 1 and height <= 1:
                break
            next_width = max(1, int(width / self._lod_factor))
            next_height = max(1, int(height / self._lod_factor))
            self._lod_surfaces.append(pg.transform.smoothscale(previous, (next_width, next_height)))

    def get_lod_surface(self, scale: float) -> tuple[pg.Surface, int]:
        """
        Return the smallest cached surface suitable for a scale and its level.

        :param scale: scale factor at which the texture will be drawn
        :return: the selected surface and its LOD level
        """
        if scale <= 0 or scale >= 1 or self._lod_factor <= 1:
            return self._surface, 0

        level = max(0, int(math.floor(math.log(1.0 / scale, self._lod_factor))))
        self._extend_lod_to(level)
        level = min(level, len(self._lod_surfaces) - 1)
        return self._lod_surfaces[level], level

    def pregenerate_lods(self, scale: float) -> None:
        """
        Generate every LOD needed down to a scale.

        :param scale: smallest scale factor to prepare LODs for
        """
        self.get_lod_surface(scale)

    def get_at_uv(self, uv: vec2) -> Color:
        """
        Return the color at normalized coordinates.

        :param uv: normalized position where ``(0, 0)`` is the top-left and ``(1, 1)`` the bottom-right
        :return: the color at that position, or transparent black when out of bounds
        """
        return self.get_at_pos(self.dims * uv)

    def get_at_pos(self, pos: vec2) -> Color:
        """
        Return the color at a pixel position.

        :param pos: pixel position in the base surface
        :return: the color at that position, or transparent black when out of bounds
        """
        try:
            return self.surface.get_at(pos)
        except IndexError:
            return Color(0, 0, 0, 0)

    @staticmethod
    def _get_dims(
        surface: pg.Surface,
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> vec2:
        """
        Resolve target dimensions while preserving the surface aspect ratio.

        :param surface: surface supplying the fallback aspect ratio
        :param dims: optional target dimensions
        :param width: optional target width
        :param height: optional target height
        :return: the resolved width and height
        """
        w, h = dims or (None, None)
        w = width or w
        h = height or h

        ratio = (w / h) if w and h else surface.get_width() / surface.get_height()
        w = (h * ratio) if not w and h else w
        h = (w / ratio) if not h and w else h
        return vec2(w, h)

    def resize(
        self,
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Resize the base surface in place.

        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: this texture
        """
        if dims or width or height:
            new_dims = self._get_dims(self.surface, dims, width, height)
            self._surface = pg.transform.scale(self.surface, new_dims)
            self._invalidate_lod()
        return self

    def resized(
        self,
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Return a resized copy.

        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: a new resized texture
        """
        return self.copy().resize(dims, width, height)

    def copy(self) -> Texture:
        """
        Return an independent copy of this texture.

        :return: a texture wrapping a copy of the base surface
        """
        return self.from_surface(self.surface.copy())

    @classmethod
    def from_surface(
        cls,
        surface: pg.Surface,
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Create a texture from an existing surface.

        :param surface: surface to copy and wrap
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: the created texture
        """
        texture = cls(surface.convert_alpha())
        texture.resize(dims, width, height)
        return texture

    @classmethod
    def from_path(
        cls,
        path: Union[Path, str],
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Create a texture from an image file.

        :param path: filesystem path of the image
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: the created texture
        """
        return cls.from_surface(pg.image.load(path), dims, width, height)

    @classmethod
    def from_color_array(
        cls,
        arr: np.ndarray,
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Create a texture from an RGB or RGBA color array.

        :param arr: array of shape ``(height, width)``, ``(height, width, 3)``, or ``(height, width, 4)``
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: the created texture
        """
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

        height_px, width_px = arr.shape[:2]
        surface = pg.image.frombuffer(
            np.ascontiguousarray(arr).tobytes(),
            (width_px, height_px),
            "RGBA",
        )
        return cls.from_surface(surface, dims, width, height)

    @classmethod
    def from_grayscale_array(
        cls,
        arr: np.ndarray,
        normalize: bool | tuple[float, float] = False,
        cmap: str | Colormap = "binary",
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Create a texture from a grayscale array, optionally colorized by a colormap.

        :param arr: two-dimensional grayscale array
        :param normalize: whether to normalize using the array range, or an explicit ``(min, max)`` pair
        :param cmap: matplotlib colormap name or instance, or ``"binary"`` for grayscale output
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: the created texture
        """
        if normalize is not False:
            min_v, max_v = (arr.min(), arr.max()) if isinstance(normalize, bool) else normalize
            arr = normalize_array(arr, min_v, max_v)

        if not np.issubdtype(arr.dtype, np.integer):
            if arr.max() > 1.0:
                arr = np.clip(arr / 255.0, 0.0, 1.0)
        elif cmap != "binary":
            arr = arr.astype(np.float32) / 255.0

        if cmap != "binary":
            arr = colorize_array(arr, cmap=cmap)  # type: ignore[arg-type]
        else:
            if not np.issubdtype(arr.dtype, np.integer):
                arr = np.clip(arr, 0.0, 1.0)
                arr = (arr * 255).astype(np.uint8)
            arr = np.stack([arr] * 3, axis=-1)

        return cls.from_color_array(arr, dims, width, height)

    @classmethod
    def from_array(
        cls,
        arr: np.ndarray,
        normalize: bool | tuple[float, float] = False,
        cmap: str | Colormap = "binary",
        dims: Optional[Vec2Like] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Texture:
        """
        Create a texture from either a grayscale or a color array.

        :param arr: two-dimensional grayscale or three-dimensional color array
        :param normalize: whether to normalize using the array range, or an explicit ``(min, max)`` pair
        :param cmap: matplotlib colormap name or instance, or ``"binary"`` for grayscale output
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: the created texture
        :raises ValueError: if the array is neither two- nor three-dimensional
        """
        if len(arr.shape) == 3:
            return cls.from_color_array(arr, dims, width, height)
        if len(arr.shape) == 2:
            return cls.from_grayscale_array(arr, normalize, cmap, dims, width, height)
        raise ValueError("arr given isn't grayscale or color, shape: " + str(arr.shape))

    @classmethod
    def from_noise(
        cls,
        dims: vec2 | tuple[int, int],
        noise_offset: vec2 | tuple[int, int] = (0, 0),
        seed: Optional[int] = None,
        scale: float = 1,
        amplitude: float = 1,
        value_offset: float = 0,
        octaves: int = 8,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        cmap: str | Colormap = "binary",
    ) -> Texture:
        """
        Create a texture from generated fractal noise.

        :param dims: dimensions of the noise texture
        :param noise_offset: offset applied to the noise sampling position
        :param seed: optional random seed
        :param scale: noise feature scale
        :param amplitude: noise amplitude
        :param value_offset: constant added to every noise value
        :param octaves: number of noise octaves to combine
        :param persistence: amplitude falloff between octaves
        :param lacunarity: frequency multiplier between octaves
        :param cmap: matplotlib colormap name or instance, or ``"binary"`` for grayscale output
        :return: the created texture
        """
        return cls.from_grayscale_array(
            create_noise_array(
                dims,
                noise_offset,
                seed,
                scale,
                amplitude,
                value_offset,
                octaves,
                persistence,
                lacunarity,
            ),
            cmap=cmap,
        )
