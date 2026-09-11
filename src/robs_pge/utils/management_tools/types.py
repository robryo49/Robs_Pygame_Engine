from __future__ import annotations

import inspect
from dataclasses import dataclass, replace
from typing import Any, Callable, Optional

import numpy as np

from ..math import vec2, vec3


type Vec2Like = vec2 | np.ndarray | tuple[float, float]
type Vec3Like = vec3 | np.ndarray | tuple[float, float, float]


type Callback[**P, T] = Callable[P, T] | tuple[Callable[P, T], ...] | None

type EasingFunctionType = Callable[[float], float]
type StyleOrName[T] = Optional[T | str]
type ValueOrGetter[T] = T | Callable[[], T]


@dataclass
class Style:
    def with_(self, **kwargs):
        return replace(self, **kwargs)  # type: ignore[arg-type]
    
    def copy(self):
        return replace(self)



def validate_signature(method: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    sig = inspect.signature(method)
    
    try:
        sig.bind_partial(*args, **kwargs)
    except TypeError as e:
        name = getattr(method, "__name__", repr(method))
        raise ValueError(f"Invalid arguments for {name}({sig}): {e}") from e
    
    params = sig.parameters
    accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
    
    if not accepts_kwargs:
        valid_keys = {
            name for name, p in params.items()
            if p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        }
        unknown = set(kwargs.keys()) - valid_keys
        if unknown:
            name = getattr(method, "__name__", repr(method))
            raise ValueError(
                f"{name} does not accept parameter(s): {', '.join(sorted(unknown))}. "
                f"Valid parameters: {', '.join(sorted(valid_keys))}"
            )