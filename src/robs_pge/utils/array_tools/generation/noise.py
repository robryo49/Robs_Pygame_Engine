"""Perlin noise array generation."""

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
    """Generate a two-dimensional Perlin noise array.

    :param dims: Output dimensions as ``(width, height)``.
    :param noise_offset: Spatial offset applied to the noise coordinates.
    :param seed: Random seed, chosen randomly when omitted.
    :param scale: Noise scale multiplied by 100 before the coordinate divisor is derived.
    :param amplitude: Multiplier applied to the centered noise values.
    :param value_offset: Constant added to the centered noise values.
    :param octaves: Number of noise octaves to combine.
    :param persistence: Amplitude multiplier between successive octaves.
    :param lacunarity: Frequency multiplier between successive octaves.
    :return: A float32 array containing the generated noise.
    """
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
