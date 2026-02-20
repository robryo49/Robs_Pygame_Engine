from typing import Protocol, Union

import numpy as np

from .math import Vec2, Vec3


Vec2Like = Union[Vec2, np.ndarray, tuple[int | float, int | float]]
Vec3Like = Union[Vec3, np.ndarray, tuple[int | float, int | float, float | int]]

class ObjectLike(Protocol):
    def render(self, submit, camera): pass
    def update(self, dt: float): pass
