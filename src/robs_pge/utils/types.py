from typing import Union

import numpy as np

from .math import Vec2, Vec3


Vec2Like = Union[Vec2, np.ndarray, tuple[int | float, int | float]]
Vec3Like = Union[Vec3, np.ndarray, tuple[int | float, int | float, float | int]]


