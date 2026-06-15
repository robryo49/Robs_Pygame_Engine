import numpy as np
from matplotlib.colors import Colormap
from matplotlib.pyplot import colormaps


def normalize_array(arr: np.ndarray, min_v: float = 0.0, max_v: float = 1.0) -> np.ndarray:
    arr_min, arr_max = arr.min(), arr.max()
    if arr_max == arr_min:
        return np.full_like(arr, min_v, dtype=np.float32)
    return ((arr - arr_min) * (max_v - min_v) / (arr_max - arr_min) + min_v).astype(np.float32)

def colorize_array(arr: np.ndarray, normalize=False, cmap: str | Colormap = "binary"):
    if normalize:
        arr = normalize_array(arr.astype(np.float32))
    return colormaps.get_cmap(cmap)(arr) * 255

def blend_arrays(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return (a * (1 - mask) + b * mask).astype(np.float32)

def apply_curve(arr: np.ndarray, gamma: float) -> np.ndarray:
    return np.power(np.clip(arr, 0.0, 1.0), gamma).astype(np.float32)
