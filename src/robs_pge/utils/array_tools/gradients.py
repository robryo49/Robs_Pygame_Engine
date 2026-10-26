"""Numpy gradient array generators for linear, radial, and angular patterns."""

from math import pi
from typing import Optional

import numpy as np
from glm import vec2


def create_linear_gradient_array(
        dims: vec2 | tuple[int, int],
        start: float = 0.0,
        end: float = 1.0,
        axis: int = 0,
) -> np.ndarray:
    """Create a gradient that ramps linearly along one image axis.

    :param dims: Output dimensions as ``(width, height)``.
    :param start: Value at the beginning of the gradient axis.
    :param end: Value at the end of the gradient axis.
    :param axis: Axis to ramp along, where 0 is horizontal and 1 is vertical.
    :return: A two-dimensional float32 gradient array.
    """
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    
    line = np.linspace(start, end, width if axis == 0 else height, dtype=np.float32)
    
    if axis == 0:
        return np.tile(line, (height, 1))
    else:
        return np.tile(line[:, np.newaxis], (1, width))


def create_radial_gradient_array(
        dims: vec2 | tuple[int, int],
        center: Optional[vec2 | tuple[float, float]] = None,
        inner: float = 0.0,
        outer: float = 1.0,
        clamp: bool = True,
) -> np.ndarray:
    """Create a gradient based on distance from a center point.

    Distances are normalized by the distance from the image origin to the center. Values are
    interpolated from ``inner`` at the center to ``outer`` at that normalized distance.

    :param dims: Output dimensions as ``(width, height)``.
    :param center: Center point in pixels, defaulting to the image center.
    :param inner: Value at the center of the gradient.
    :param outer: Value at the normalized maximum distance.
    :param clamp: Whether to clamp normalized distances to the range 0 to 1.
    :return: A two-dimensional float32 gradient array.
    """
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


def create_angular_gradient_array(
        dims: vec2 | tuple[int, int],
        center: Optional[vec2 | tuple[float, float]] = None,
        start_angle: float = 0.0,
        start: float = 0.0,
        end: float = 1.0,
) -> np.ndarray:
    """Create a gradient that sweeps by angle around a center point.

    :param dims: Output dimensions as ``(width, height)``.
    :param center: Center point in pixels, defaulting to the image center.
    :param start_angle: Angle in radians where the gradient ramp begins.
    :param start: Value at ``start_angle``.
    :param end: Value after one full revolution from ``start_angle``.
    :return: A two-dimensional gradient array.
    """
    width, height = (int(dims.x), int(dims.y)) if isinstance(dims, vec2) else dims
    cx, cy = (center.x, center.y) if isinstance(center, vec2) else (center or (width / 2, height / 2))
    
    xs = np.arange(width, dtype=np.float32)
    ys = np.arange(height, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys)
    
    angles = (np.arctan2(yy - cy, xx - cx) - start_angle) % (2 * pi)
    t = (angles / (2 * pi)).astype(np.float32)
    
    return np.array((end - start) * t + start)