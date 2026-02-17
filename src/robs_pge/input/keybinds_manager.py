from .input_manager import InputManager
from .keybind import Keybind
from ..utils import KeybindFlags, Keybinds


class KeybindsManager:
    def __init__(self, input_manager: InputManager):
        
        self._input_manager = input_manager
        
        self._keybinds: dict[int | tuple[int, ...], list[Keybind]] = {}
        
    # region PROPERTIES
    
    @property
    def input_manager(self):
        return self._input_manager
    
    @property
    def keybinds(self):
        return dict(self._keybinds)
    
    # endregion
    
    def has(self, kb: int | tuple[int, ...]):
        return kb in self._keybinds
    
    def remove(self, kb: int | tuple[int, ...]):
        self._keybinds.pop(kb, None)
        
    def set(self, keybind: Keybind):
        self._keybinds[keybind.key] = [keybind]
        
    def add(self, keybind: Keybind):
        if self.has(keybind.key):
            self._keybinds[keybind.key].append(keybind)
        else:
            self.set(keybind)
            
    def _test_mouse_wheel(self, mouse_wheel_kb: int):
        if mouse_wheel_kb == Keybinds.MOUSEWHEEL_UP:
            return self.input_manager.mouse_scroll > 0
        elif mouse_wheel_kb == Keybinds.MOUSEWHEEL_DOWN:
            return self.input_manager.mouse_scroll < 0
        elif mouse_wheel_kb == Keybinds.MOUSEWHEEL:
            return bool(self.input_manager.mouse_scroll)
        
        return False
        
            
    def _test_keybind(self, keybind: Keybind):
        
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
        
        return valid and (pressed or held or released or scroll)
    
    def update(self):
        for keybinds in self._keybinds.values():
            for keybind in keybinds:
                if self._test_keybind(keybind):
                    keybind.action()
