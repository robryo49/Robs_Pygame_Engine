from typing import Union, Protocol
from .math import Vec2


class ObjectLike(Protocol):
    width: int
    height: int
    dims: Vec2


