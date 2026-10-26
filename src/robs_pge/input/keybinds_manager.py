"""Stores keybindings and dispatches their actions based on tracked input state."""

from .input_manager import InputManager
from .keybind import Keybind
from .keybind_flags import KeybindFlags
from .keybinds import Keybinds


class KeybindsManager:
    """Groups keybindings by trigger key and evaluates them against an input manager."""

    def __init__(self, input_manager: InputManager) -> None:
        """
        Initialize a keybinds manager.

        :param input_manager: input manager used to query key, button, and scroll state
        """
        self._input_manager = input_manager
        
        self._keybinds: dict = {}
        
    # region PROPERTIES
    
    @property
    def input_manager(self):
        """Return the input manager used to evaluate bindings."""
        return self._input_manager
    
    @property
    def keybinds(self) -> dict:
        """Return the registered bindings grouped by trigger key."""
        return self._keybinds
    
    # endregion
    
    def has(self, kb: int | tuple[int, ...]) -> bool:
        """
        Return whether a trigger key has any registered binding.

        :param kb: key, button, or key sequence to check
        :return: ``True`` if at least one binding uses the trigger
        """
        return kb in self._keybinds
    
    def remove(self, kb: int | tuple[int, ...]) -> "KeybindsManager":
        """
        Remove every binding associated with a trigger key.

        :param kb: key, button, or key sequence to remove
        :return: this manager
        """
        self.keybinds.pop(kb, None)
        return self

    def set(self, keybind: Keybind) -> "KeybindsManager":
        """
        Replace all bindings for the keybind's trigger with the supplied binding.

        :param keybind: binding to store
        :return: this manager
        """
        self.keybinds[keybind.key] = [keybind]
        return self
        
    def register(self, keybind: Keybind) -> "KeybindsManager":
        """
        Add a binding, preserving existing bindings for the same trigger.

        :param keybind: binding to add
        :return: this manager
        """
        if self.has(keybind.key):
            self.keybinds.get(keybind.key).append(keybind)
        else:
            self.set(keybind)
        return self
            
    def _test_mouse_wheel(self, mouse_wheel_kb: int):
        """
        Return whether a mouse-wheel pseudo-key is active this frame.

        :param mouse_wheel_kb: mouse-wheel pseudo-key to test
        :return: ``True`` if the corresponding scroll direction occurred
        """
        if mouse_wheel_kb == Keybinds.MOUSEWHEEL_UP:
            return self.input_manager.mouse_scroll > 0
        elif mouse_wheel_kb == Keybinds.MOUSEWHEEL_DOWN:
            return self.input_manager.mouse_scroll < 0
        elif mouse_wheel_kb == Keybinds.MOUSEWHEEL:
            return bool(self.input_manager.mouse_scroll)
        else:
            return False
        
    def _test_keybind(self, keybind: Keybind) -> bool:
        """
        Evaluate whether a binding's trigger and flags match the current input state.

        :param keybind: binding to evaluate
        :return: ``True`` if the binding should fire
        """
        valid = True
        if isinstance(keybind.key, tuple):
            for key in keybind.key[:-1]:
                
                if self._test_mouse_wheel(key):
                    valid &= bool(self.input_manager.mouse_scroll)
                else:
                    valid &= self.input_manager.held(key)
                
            key = keybind.key[-1]
        else:
            key = keybind.key
            
        scroll = self.input_manager.mouse_scroll and self._test_mouse_wheel(key)
        pressed = keybind.has_flag(KeybindFlags.PRESS) and self.input_manager.pressed(key)
        held = keybind.has_flag(KeybindFlags.HOLD) and self.input_manager.held(key)
        released = keybind.has_flag(KeybindFlags.RELEASE) and self.input_manager.released(key)
        
        return bool(valid and (pressed or held or released or scroll))
    
    def update(self) -> "KeybindsManager":
        """
        Evaluate every binding and invoke the actions of those that match.

        :return: this manager
        """
        for keybinds in self._keybinds.values():
            for keybind in keybinds:
                if self._test_keybind(keybind):
                    if keybind.action is not None:
                        if isinstance(keybind.action, tuple):
                            for action in keybind.action:
                                action()
                        else:
                            keybind.action()

        return self
