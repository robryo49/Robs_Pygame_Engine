"""Array normalization, colorization, blending, and curve helpers for visualization."""

import numpy as np
from matplotlib.colors import Colormap
from matplotlib.pyplot import colormaps


def normalize_array(arr: np.ndarray, min_v: float = 0.0, max_v: float = 1.0) -> np.ndarray:
    """Rescale an array so its minimum and maximum map to the requested range.

    :param arr: Input array to normalize.
    :param min_v: Output value corresponding to the input minimum.
    :param max_v: Output value corresponding to the input maximum.
    :return: A float32 array normalized to the requested range, or filled with ``min_v`` for constant input.
    """
    arr_min, arr_max = arr.min(), arr.max()
    if arr_max == arr_min:
        return np.full_like(arr, min_v, dtype=np.float32)
    return ((arr - arr_min) * (max_v - min_v) / (arr_max - arr_min) + min_v).astype(np.float32)

def colorize_array(arr: np.ndarray, normalize=False, cmap: str | Colormap = "binary"):
    """Map array values to colors with a matplotlib colormap.

    :param arr: Input array of values to colorize.
    :param normalize: Whether to normalize the values to 0 through 1 first.
    :param cmap: Colormap name or colormap instance.
    :return: An RGBA color array with channel values scaled to 0 through 255.
    """
    if normalize:
        arr = normalize_array(arr.astype(np.float32))
    return colormaps.get_cmap(cmap)(arr) * 255

def blend_arrays(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Blend two arrays using a mask as the interpolation weight.

    :param a: Array used where the mask is 0.
    :param b: Array used where the mask is 1.
    :param mask: Blend weights, typically between 0 and 1.
    :return: A float32 array blended element-wise between the inputs.
    """
    return (a * (1 - mask) + b * mask).astype(np.float32)

def apply_curve(arr: np.ndarray, gamma: float) -> np.ndarray:
    """Apply a gamma curve to values clipped to the 0 through 1 range.

    :param arr: Input array to transform.
    :param gamma: Exponent applied to the clipped values.
    :return: A float32 array containing the gamma-adjusted values.
    """
    return np.power(np.clip(arr, 0.0, 1.0), gamma).astype(np.float32)
