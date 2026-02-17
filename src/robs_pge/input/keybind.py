from dataclasses import dataclass
from typing import Callable

from ..utils import KeybindFlags


@dataclass
class Keybind:
    key: int | tuple[int, ...]
    action: Callable
    flag: int = KeybindFlags.PRESS
    
    def has_flag(self, flag: int):
        return bool(flag & self.flag)

