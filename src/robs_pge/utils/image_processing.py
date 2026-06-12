from math import cos, pi, sin
from random import randrange

import noise
import numpy as np
#from matplotlib.cm import get_cmap
from matplotlib.colors import Colormap
from pygame import Vector2 as Vec2

from src.robs_pge.utils import invert_uv_y


def normalize_array(arr: np.ndarray, min_v: float, max_v:float):
    arr_min, arr_max = arr.min(), arr.max()
    return (arr - arr_min) * (max_v - min_v) / (arr_max - arr_min) + min_v


def colorize_array(arr: np.ndarray, cmap: str | Colormap="binary"):
    return None #get_cmap(cmap)(arr) * 255


def noise_array(dims: Vec2, seed: int=None, scale: float=100, amplitude: float=1, offset: float=0, octaves: int=8, persistence: float=0.5, lacunarity: float=2.0):
    
    seed = randrange(10000) if seed is None else seed
    width, height = int(dims.x), int(dims.y)
    
    arr = np.zeros((height, width), dtype=np.float32)
    
    for y in range(int(dims.y)):
        for x in range(int(dims.x)):
            arr[y, x] = noise.pnoise3(
                x=x / scale,
                y=y / scale,
                z=hash(seed),
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity
            )
    
    return arr * amplitude + (offset + 0.5)


def rotated_surface_dims(dims, rotation):
    return Vec2(
        abs(dims.x * cos(rotation*pi/180)) + abs(dims.y * sin(rotation*pi/180)),
        abs(dims.y * cos(rotation*pi/180)) + abs(dims.x * sin(rotation*pi/180))
    )


def surface_pos_from_pixel_pos(pixel_pos: Vec2, dims: Vec2, rotation=0):
    if rotation:
        return ((pixel_pos - dims/2).rotate(-rotation) + rotated_surface_dims(dims, rotation) / 2).elementwise()
    else:
        return pixel_pos


def surface_pos_from_uv_pos(uv: Vec2, dims: Vec2, rotation=0):
    return surface_pos_from_pixel_pos(invert_uv_y(uv).elementwise() * dims, dims, rotation)
