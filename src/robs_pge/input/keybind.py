"""Defines a key or button binding and the action it triggers."""

from dataclasses import dataclass
from typing import Any

from ..utils import KeybindFlags, Callback


@dataclass
class Keybind:
    """Binds a key, mouse button, or key sequence to an action and trigger flag."""

    key: int | tuple[int, ...]
    action: Callback[[], Any]
    flag: int = KeybindFlags.PRESS

    def has_flag(self, flag: int) -> bool:
        """
        Return whether this binding includes a trigger flag.

        :param flag: flag to test against the binding's flags
        :return: ``True`` if any of the requested flags are set
        """
        return bool(flag & self.flag)

