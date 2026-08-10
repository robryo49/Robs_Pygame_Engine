from __future__ import annotations
from math import cos, sin, pi
from typing import TYPE_CHECKING
from .functions import clamp

if TYPE_CHECKING:
    from robs_pge.utils.management_tools.types import EasingFunctionType


class Easing:
    JUMP: EasingFunctionType = lambda x: int(clamp(x, 0, 1))
    LINEAR: EasingFunctionType = lambda x: x
    
    EASE_IN_SINE: EasingFunctionType = lambda x: (1 - cos((x * pi) / 2))
    EASE_OUT_SINE: EasingFunctionType = lambda x: (sin((x * pi) / 2))
    EASE_IN_OUT_SINE: EasingFunctionType = lambda x: (-(cos(pi * x) - 1) / 2)
    EASE_IN_QUAD: EasingFunctionType = lambda x: (x**2)
    EASE_OUT_QUAD: EasingFunctionType = lambda x: (1 - (1 - x) * (1 - x))
    EASE_IN_OUT_QUAD: EasingFunctionType = lambda x: (2 * x**2 if x < 0.5 else 1 - (-2 * x + 2)**2 / 2)
    EASE_IN_CUBIC: EasingFunctionType = lambda x: (x**3)
    EASE_OUT_CUBIC: EasingFunctionType = lambda x: (1 - (1 - x)**3)
    EASE_IN_OUT_CUBIC: EasingFunctionType = lambda x: (4 * x**3 if x < 0.5 else 1 - (-2 * x + 2)**3 / 2)
    EASE_IN_QUART: EasingFunctionType = lambda x: (x**4)
    EASE_OUT_QUART: EasingFunctionType = lambda x: (1 - (1 - x)**4)
    EASE_IN_OUT_QUART: EasingFunctionType = lambda x: (8 * x**4 if x < 0.5 else 1 - (-2 * x + 2)**4 / 2)
    EASE_IN_QUINT: EasingFunctionType = lambda x: (x**4 * x)
    EASE_OUT_QUINT: EasingFunctionType = lambda x: (1 - (1 - x)**5)
    EASE_IN_OUT_QUINT: EasingFunctionType = lambda x: (16 * x**4 * x if x < 0.5 else 1 - (-2 * x + 2)**5 / 2)
    EASE_IN_BACK: EasingFunctionType = lambda x: (2.70158 * x**3 - 1.70158 * x**2)
    EASE_OUT_BACK: EasingFunctionType = lambda x: (1 + 2.70158 * (x - 1)**3 + 1.70158 * (x - 1)**2)
    EASE_IN_OUT_BACK: EasingFunctionType = lambda x: (((2 * x)**2 * (3.59491 * 2 * x - 2.59491)) / 2 if x < 0.5 else ((2 * x - 2)**2 * (3.59491 * (x * 2 - 2) + 2.59491) + 2) / 2)
    EASE_IN_ELASTIC: EasingFunctionType = lambda x: (0 if x == 0 else 1 if x == 1 else -(2**(10 * x - 10)) * sin((x * 10 - 10.75) * ((2 * pi) / 3)) if x < 0.5 else (2**(-10 * x + 10)) * sin((x * 10 - 10.75) * ((2 * pi) / 3)) + 1)
    EASE_OUT_ELASTIC: EasingFunctionType = lambda x: (0 if x == 0 else 1 if x == 1 else (2**(-10 * x)) * sin((x * 10 - 0.75) * ((2 * pi) / 3)) + 1)
    EASE_IN_OUT_ELASTIC: EasingFunctionType = lambda x: (0 if x == 0 else 1 if x == 1 else (-(2**(20 * x - 10)) * sin((20 * x - 11.125) * ((2 * pi) / 4.5))) / 2 if x < 0.5 else ((2**(-20 * x + 10)) * sin((20 * x - 11.125) * ((2 * pi) / 4.5))) / 2 + 1)
