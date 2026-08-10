from typing import Optional

import numpy as np
from glm import vec2


def create_circle_mask(
        radius: float,
        dims: Optional[vec2 | tuple[int, int]] = None,
        center: Optional[vec2 | tuple[float, float]] = None,
) -> np.ndarray:
    if dims is None:
        size = int(np.ceil(radius)) * 2 + 1
        width, height = size, size
    else:
        width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    
    if center is None:
        cx, cy = (width - 1) / 2.0, (height - 1) / 2.0
    else:
        cx, cy = (center.x, center.y) if isinstance(center, vec2) else center
    
    ys, xs = np.ogrid[:height, :width]
    distance = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
    
    return (distance <= radius).astype(np.float32)


def create_rect_mask(
        dims: vec2 | tuple[int, int],
        rect: Optional[tuple[int, int, int, int]] = None,
        soft_edge: float = 0.0,
) -> np.ndarray:
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    x, y, w, h = rect if rect else (0, 0, width, height)
    
    xs = np.arange(width, dtype=np.float32)
    ys = np.arange(height, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    
    if soft_edge > 0:
        dx = np.minimum(xx - x, (x + w) - xx)
        dy = np.minimum(yy - y, (y + h) - yy)
        dist = np.minimum(dx, dy)
        return np.clip(dist / soft_edge, 0.0, 1.0).astype(np.float32)
    else:
        mask = ((xx >= x) & (xx < x + w) & (yy >= y) & (yy < y + h))
        return mask.astype(np.float32)
