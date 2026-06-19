from typing import Protocol, Union

import numpy as np

from .math import Vec2, Vec3

NumberLike = Union[int, float]

Vec2Like = Union[Vec2, np.ndarray[tuple[int, int]], tuple[NumberLike, NumberLike]]
Vec3Like = Union[Vec3, np.ndarray[tuple[int, int]], tuple[NumberLike, NumberLike, NumberLike]]

class ObjectLike(Protocol):
    def render(self, submit, camera): pass
    def update(self, dt: float): pass
