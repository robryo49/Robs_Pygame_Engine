"""Shared type aliases, style helpers, and signature validation utilities."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Optional, Union

from glm import vec1, vec2, vec3, vec4

type Callback[**P, T] = Callable[P, T] | tuple[Callable[P, T], ...] | None

type EasingFunctionType = Callable[[float], float]
type StyleOrName[T] = Optional[T | str]
type ValueOrGetter[T] = T | Callable[[], T]


Vec2Like = Union[vec2, tuple[float, float], list[float]]
Vec3Like = Union[vec3, tuple[float, float, float], list[float]]
Vec4Like = Union[vec4, tuple[float, float, float, float], list[float]]


@dataclass
class Style:
    """Base class for immutable dataclass-based style configurations."""

    def with_(self, **kwargs):
        """Return a copy with selected fields replaced.

        :param kwargs: Field values to replace.
        :return: A new style instance with the merged fields.
        """
        return replace(self, **kwargs)  # type: ignore[arg-type]
    
    def copy(self):
        """Return a copy of this style.

        :return: A new style instance with the same fields.
        """
        return replace(self)

