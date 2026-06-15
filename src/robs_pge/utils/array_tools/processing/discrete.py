import numpy as np
import skimage.filters
import skimage.morphology
import skimage.segmentation
from scipy.ndimage import distance_transform_edt
from skimage.filters.rank import majority


def skeletonize_mask(mask: np.ndarray) -> np.ndarray:
    return skimage.morphology.skeletonize(mask).astype(np.float32)

def majority_filter(arr: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0: return arr.copy()
    
    original_dtype = arr.dtype
    
    unique_vals, inverse = np.unique(arr, return_inverse=True)
    working_arr = inverse.reshape(arr.shape).astype(np.uint16)
    filtered_indices = majority(working_arr, footprint=skimage.morphology.disk(radius))
    
    return unique_vals[filtered_indices].astype(original_dtype)

def remove_small_objects(arr: np.ndarray, max_size: int) -> np.ndarray:
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
    return skimage.morphology.label(arr, background, connectivity=1)

def label_array_random(arr: np.ndarray, background: int = -1) -> np.ndarray:
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

def find_edges(mask: np.ndarray, mode: str = "outter") -> np.ndarray:
    return skimage.segmentation.find_boundaries(mask, mode=mode)

def generate_distance_map(mask: np.ndarray, sampling=None) -> np.ndarray:
    return distance_transform_edt(mask == 0, sampling=sampling).astype(np.float32)

def get_label_centers(labeled_arr: np.ndarray) -> dict:
    props = skimage.measure.regionprops(labeled_arr)
    return {prop.label: prop.centroid for prop in props}
