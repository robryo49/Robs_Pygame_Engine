"""Discrete-array processing helpers for masks, labels, and distance maps."""

from typing import Any

import numpy as np
import skimage.filters
import skimage.morphology
import skimage.segmentation
from scipy.ndimage import distance_transform_edt
from skimage.filters.rank import majority


def skeletonize_mask(mask: np.ndarray) -> np.ndarray:
    """Reduce a binary mask to a one-pixel-wide skeleton.

    :param mask: Binary input mask.
    :return: A float32 array containing the skeleton.
    """
    return skimage.morphology.skeletonize(mask).astype(np.float32)

def majority_filter(arr: np.ndarray, radius: int) -> np.ndarray:
    """Replace each value with the majority value in a disk-shaped neighborhood.

    :param arr: Input label array.
    :param radius: Radius in pixels of the disk-shaped footprint; values of zero or less skip filtering.
    :return: A filtered array with the original dtype.
    """
    if radius <= 0: return arr.copy()
    
    original_dtype = arr.dtype
    
    unique_vals, inverse = np.unique(arr, return_inverse=True)
    working_arr = inverse.reshape(arr.shape).astype(np.uint16)
    filtered_indices = majority(working_arr, footprint=skimage.morphology.disk(radius))
    
    return unique_vals[filtered_indices].astype(original_dtype)

def remove_small_objects(arr: np.ndarray, max_size: int) -> np.ndarray:
    """Remove connected components smaller than a size threshold.

    Pixels belonging to removed objects are filled from the nearest remaining pixel.

    :param arr: Input label array.
    :param max_size: Maximum component size to remove; values of zero or less skip removal.
    :return: The cleaned array, or a copy when nothing needs removal.
    """
    if max_size <= 0:
        return arr.copy()
    
    labeled_arr = label_array(arr, background=-1)
    
    cleaned_labels = skimage.morphology.remove_small_objects(
        labeled_arr, max_size=max_size, connectivity=1
    )
    
    is_small_object = (labeled_arr > 0) & (cleaned_labels == 0)
    
    if not np.any(is_small_object):
        return arr.copy()
    
    indices = distance_transform_edt(is_small_object, return_distances=False, return_indices=True)
    
    output = arr[indices[0], indices[1]]
    
    return output

def label_array(arr: np.ndarray, background: int = -1) -> np.ndarray:
    """Label connected components in an array.

    :param arr: Input array to label.
    :param background: Value treated as background and excluded from labeling.
    :return: An integer array of connected-component labels.
    """
    return skimage.morphology.label(arr, background, connectivity=1)

def label_array_random(arr: np.ndarray, background: int = -1) -> np.ndarray:
    """Label connected components and assign their labels in random order.

    :param arr: Input array whose non-background values provide the replacement label pool.
    :param background: Value treated as background and preserved.
    :return: A labeled array using randomly assigned values from the input.
    """
    labeled = skimage.morphology.label(arr, background=background, connectivity=1)
    
    num_features = labeled.max()
    if num_features == 0:
        return np.full_like(arr, background)
    
    existing_values = arr[arr != background]
    
    if len(existing_values) == 0:
        return np.full_like(arr, background)
    
    shuffled_pool = np.random.permutation(existing_values)
    shuffled_ids = np.random.choice(shuffled_pool, size=num_features, replace=False if len(np.unique(shuffled_pool)) >= num_features else True)
    
    lookup_table = np.zeros(num_features + 1, dtype=arr.dtype)
    lookup_table[0] = background
    lookup_table[1:] = shuffled_ids
    
    return lookup_table[labeled]

def find_edges(mask:  np.typing.NDArray[Any], mode: str = "outter") -> np.ndarray:
    """Find boundary pixels in a mask.

    :param mask: Binary input mask.
    :param mode: Boundary mode passed to ``skimage.segmentation.find_boundaries``.
    :return: A boolean array marking boundary pixels.
    """
    return skimage.segmentation.find_boundaries(mask, mode=mode) # type: ignore[arg-type]

def generate_distance_map(mask: np.ndarray, sampling=None) -> np.ndarray:
    """Compute the Euclidean distance from each pixel to the nearest masked pixel.

    :param mask: Input mask whose zero pixels are treated as the distance targets.
    :param sampling: Spacing of array elements along each dimension, passed to the distance transform.
    :return: A float32 array of distance values.
    """
    return distance_transform_edt(mask == 0, sampling=sampling).astype(np.float32)

def get_label_centers(labeled_arr: np.ndarray) -> dict:
    """Compute the centroid of each labeled region.

    :param labeled_arr: Input array of connected-component labels.
    :return: A mapping from label to centroid coordinates.
    """
    props = skimage.measure.regionprops(labeled_arr)
    return {prop.label: prop.centroid for prop in props}
