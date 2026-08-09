from dataclasses import dataclass
from typing import Any

from ..utils import KeybindFlags, Callback


@dataclass
class Keybind:
    key: int | tuple[int, ...]
    action: Callback[[], Any]
    flag: int = KeybindFlags.PRESS

    def has_flag(self, flag: int) -> bool:
        return bool(flag & self.flag)

