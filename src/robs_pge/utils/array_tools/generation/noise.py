from random import randrange
from typing import Optional

import noise
import numpy as np
from glm import vec2


def create_noise_array(
        dims: vec2 | tuple[int, int],
        noise_offset: vec2 | tuple[int, int] = (0, 0),
        seed: Optional[int] = None,
        scale: float = 1,
        amplitude: float = 1,
        value_offset: float = 0,
        octaves: int = 8,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
) -> np.ndarray:
    scale *= 100
    seed = randrange(10_000) if seed is None else seed
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    inverse_scale = 1/scale
    
    ox, oy = noise_offset
    
    arr = np.zeros((height, width), dtype=np.float32)
    for y in range(height):
        for x in range(width):
            arr[y, x] = noise.pnoise3(
                x=(x+0.01+ox) * inverse_scale,
                y=(y+0.01+oy) * inverse_scale,
                z=hash(seed),
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
            )
    
    return arr * amplitude*0.5 + (value_offset + 0.5)
