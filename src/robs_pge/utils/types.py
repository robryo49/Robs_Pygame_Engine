from __future__ import annotations

import inspect
from typing import Any, Callable

import numpy as np

from .math import Vec2, Vec3

NumberLike = int | float

Vec2Like = Vec2 | np.ndarray | tuple[NumberLike, NumberLike]
Vec3Like = Vec3 | np.ndarray | tuple[NumberLike, NumberLike, NumberLike]


CallbackLike = Callable | tuple[Callable, ...] | None


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
