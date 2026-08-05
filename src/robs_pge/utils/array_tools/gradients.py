from math import pi
from typing import Optional

import numpy as np
from glm import vec2


def make_linear_gradient_array(
        dims: vec2 | tuple[int, int],
        start: float = 0.0,
        end: float = 1.0,
        axis: int = 0,
) -> np.ndarray:
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    
    line = np.linspace(start, end, width if axis == 0 else height, dtype=np.float32)
    
    if axis == 0:
        return np.tile(line, (height, 1))
    else:
        return np.tile(line[:, np.newaxis], (1, width))


def make_radial_gradient_array(
        dims: vec2 | tuple[int, int],
        center: Optional[vec2 | tuple[float, float]] = None,
        inner: float = 0.0,
        outer: float = 1.0,
        clamp: bool = True,
) -> np.ndarray:
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    cx, cy = (center.x, center.y) if isinstance(center, vec2) else (center or (width / 2, height / 2))
    
    xs = np.arange(width, dtype=np.float32)
    ys = np.arange(height, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    
    t = dist / max_dist if max_dist > 0 else np.zeros_like(dist)
    if clamp:
        t = np.clip(t, 0.0, 1.0)
    
    return (inner + (outer - inner) * t).astype(np.float32)


def make_angular_gradient_array(
        dims: vec2 | tuple[int, int],
        center: Optional[vec2 | tuple[float, float]] = None,
        start_angle: float = 0.0,
        start: float = 0.0,
        end: float = 1.0,
) -> np.ndarray:
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    cx, cy = (center.x, center.y) if isinstance(center, vec2) else (center or (width / 2, height / 2))
    
    xs = np.arange(width, dtype=np.float32)
    ys = np.arange(height, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    
    angles = (np.arctan2(yy - cy, xx - cx) - start_angle) % (2 * pi)
    t = (angles / (2 * pi)).astype(np.float32)
    
    return np.array((end - start) * t + start)