from random import Random, randrange
from typing import Optional

import numpy as np
from glm import vec2


def generate_grid_points(
        canvas_dims: tuple[int, int],
        grid_dims: tuple[int, int],
        jitter: float = 0.7,
        rng: Optional[Random] = None
) -> list[tuple[float, float]]:
    
    c_width, c_height = canvas_dims
    cols, rows = grid_dims
    
    if rng is None:
        rng = Random()
    
    cell_w = c_width / cols
    cell_h = c_height / rows
    
    points = []
    for r in range(rows):
        for c in range(cols):
            cx = (c + 0.5) * cell_w
            cy = (r + 0.5) * cell_h
            
            if jitter > 0:
                max_dx = (cell_w / 2) * jitter
                max_dy = (cell_h / 2) * jitter
                cx += rng.uniform(-max_dx, max_dx)
                cy += rng.uniform(-max_dy, max_dy)
            
            cx = max(0.0, min(c_width - 1.0, cx))
            cy = max(0.0, min(c_height - 1.0, cy))
            points.append((cx, cy))
    
    return points


def make_voronoi_array(
        dims: vec2 | tuple[int, int],
        grid_dims: vec2 | tuple[int, int],
        jitter: float = 0.7,
        metric: str = 'euclidean',
        seed: Optional[int] = None,
) -> np.ndarray:
    """Metric is Euclidean / manhattan / chebyshev"""
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    grid_dims = (int(grid_dims.x), int(grid_dims.y)) if isinstance(grid_dims, vec2) else grid_dims
    
    seed= randrange(10_000) if seed is None else seed
    rng = Random(seed)
    
    points = generate_grid_points((width, height), grid_dims, jitter, rng=rng)
    
    xs = np.arange(width, dtype=np.float32)
    ys = np.arange(height, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    
    arr = np.full((height, width), -1, dtype=np.int32)
    min_dist = np.full((height, width), np.inf, dtype=np.float32)
    
    for i, p in enumerate(points):
        px, py = p
        
        if metric == 'euclidean':
            dist = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
        elif metric == 'manhattan':
            dist = np.abs(xx - px) + np.abs(yy - py)
        elif metric == 'chebyshev':
            dist = np.maximum(np.abs(xx - px), np.abs(yy - py))
        else:
            raise ValueError(f"Unknown metric '{metric}'.")
        
        closer = dist < min_dist
        min_dist[closer] = dist[closer]
        arr[closer] = i
    
    return arr


def make_bfs_voronoi_array(
        dims: vec2 | tuple[int, int],
        grid_dims: vec2 | tuple[int, int],
        jitter: float = 0.7,
        seed: Optional[int] = None,
) -> np.ndarray:
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    grid_dims = (int(grid_dims.x), int(grid_dims.y)) if isinstance(grid_dims, vec2) else grid_dims
    
    seed = randrange(10_000) if seed is None else seed
    rng = Random(seed)
    
    points = generate_grid_points((width, height), grid_dims, jitter, rng=rng)
    
    arr = np.full((height, width), -1, dtype=np.int32)
    queues: list[list[tuple[int, int]]] = [[] for _ in points]
    
    for i, p in enumerate(points):
        px, py = p
        x, y = int(round(px)), int(round(py))
        if 0 <= x < width and 0 <= y < height:
            arr[y, x] = i
            queues[i].append((x, y))
    
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while any(queues):
        for i, queue in enumerate(queues):
            if not queue:
                continue
            x, y = queue.pop(rng.randrange(len(queue)))
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height and arr[ny, nx] == -1:
                    arr[ny, nx] = i
                    queue.append((nx, ny))
    
    return arr
