from __future__ import annotations

import inspect
from typing import Any, Callable, Optional, Protocol, TYPE_CHECKING, runtime_checkable

import numpy as np

from .math import Vec2, Vec3

if TYPE_CHECKING:
    from ..core import Camera
    from ..rendering import DrawCommand
    from ..objects import Layer


type Vec2Like = Vec2 | np.ndarray | tuple[float, float]
type Vec3Like = Vec3 | np.ndarray | tuple[float, float, float]


type CallbackLike = Callable | tuple[Callable, ...] | None

type EasingFunctionType = Callable[[float], float]
type StyleOrName[T] = Optional[T | str]
type ValueOrGetter[T] = T | Callable[[], T]


@runtime_checkable
class RenderableType(Protocol):
    def render(self, submit: Callable[[DrawCommand], Any], camera: Camera): pass


@runtime_checkable
class UpdatableType(Protocol):
    def update(self, dt: float): pass
    

@runtime_checkable
class ObjectLikeType(RenderableType, UpdatableType, Protocol):
    
    @property
    def layer(self): pass
    
    @layer.setter
    def layer(self, value: Layer): pass



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