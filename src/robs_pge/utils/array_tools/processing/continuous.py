import skimage.morphology
import skimage.segmentation
import skimage.filters
import numpy as np


def smooth_heightmap(arr: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    return skimage.filters.gaussian(arr, sigma=sigma).astype(np.float32)

def generate_slope_map(arr: np.ndarray) -> np.ndarray:
    return np.array(skimage.filters.sobel(arr), dtype=np.float32) # type: ignore[arg-type]

def erode_heightmap(arr: np.ndarray, radius: int = 1) -> np.ndarray:
    footprint = skimage.morphology.disk(radius)
    return skimage.filters.rank.minimum(arr, footprint).astype(np.float32)