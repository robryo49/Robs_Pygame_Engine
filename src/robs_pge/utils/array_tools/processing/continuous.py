"""Continuous-array processing helpers for smoothing, slope, and erosion."""

import skimage.morphology
import skimage.segmentation
import skimage.filters
import numpy as np


def smooth_heightmap(arr: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Smooth a heightmap with a Gaussian filter.

    :param arr: Input heightmap array.
    :param sigma: Standard deviation of the Gaussian kernel.
    :return: A float32 array containing the smoothed values.
    """
    return skimage.filters.gaussian(arr, sigma=sigma).astype(np.float32)

def generate_slope_map(arr: np.ndarray) -> np.ndarray:
    """Compute a slope map from an array using the Sobel filter.

    :param arr: Input heightmap array.
    :return: A float32 array containing the Sobel gradient magnitude.
    """
    return np.array(skimage.filters.sobel(arr), dtype=np.float32) # type: ignore[arg-type]

def erode_heightmap(arr: np.ndarray, radius: int = 1) -> np.ndarray:
    """Erode a heightmap with a disk-shaped minimum filter.

    :param arr: Input heightmap array.
    :param radius: Radius in pixels of the disk-shaped footprint.
    :return: A float32 array containing the eroded values.
    """
    footprint = skimage.morphology.disk(radius)
    return skimage.filters.rank.minimum(arr, footprint).astype(np.float32)