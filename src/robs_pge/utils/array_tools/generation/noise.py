from random import randrange
from typing import Optional

import noise
import numpy as np
from pygame import Vector2 as Vec2


def make_noise_array(
        dims: Vec2 | tuple[int, int],
        seed: Optional[int] = None,
        scale: float = 1,
        amplitude: float = 1,
        offset: float = 0,
        octaves: int = 8,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
) -> np.ndarray:
    scale *= 100
    seed = randrange(10_000) if seed is None else seed
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, Vec2) else dims
    inverse_scale = 1/scale
    
    arr = np.zeros((height, width), dtype=np.float32)
    for y in range(height):
        for x in range(width):
            arr[y, x] = noise.pnoise3(
                x=(x+0.01) * inverse_scale,
                y=(y+0.01) * inverse_scale,
                z=hash(seed),
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
            )
    
    return arr * amplitude + (offset + 0.5)
