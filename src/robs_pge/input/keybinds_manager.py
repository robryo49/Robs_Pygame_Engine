from .input_manager import InputManager
from .keybind import Keybind
from ..utils import KeybindFlags, Keybinds, DictCollection


class KeybindsManager:
    def __init__(self, input_manager: InputManager):
        
        self._input_manager = input_manager
        
        self._keybinds: DictCollection = DictCollection()
        
    # region PROPERTIES
    
    @property
    def input_manager(self):
        return self._input_manager
    
    @property
    def keybinds(self) -> DictCollection:
        return self._keybinds
    
    # endregion
    
    def has(self, kb: int | tuple[int, ...]) -> bool:
        return self.keybinds.has(kb)
    
    def remove(self, kb: int | tuple[int, ...]) -> "KeybindsManager":
        self.keybinds.pop(kb)
        return self
        
    def set(self, keybind: Keybind) -> "KeybindsManager":
        self.keybinds.set(keybind.key, [keybind])
        return self
        
    def add(self, keybind: Keybind) -> "KeybindsManager":
        if self.has(keybind.key):
            self.keybinds.get(keybind.key).append(keybind)
        else:
            self.set(keybind)
        return self
            
    def _test_mouse_wheel(self, mouse_wheel_kb: int):
        if mouse_wheel_kb == Keybinds.MOUSEWHEEL_UP:
            return self.input_manager.mouse_scroll > 0
        elif mouse_wheel_kb == Keybinds.MOUSEWHEEL_DOWN:
            return self.input_manager.mouse_scroll < 0
        elif mouse_wheel_kb == Keybinds.MOUSEWHEEL:
            return bool(self.input_manager.mouse_scroll)
        else:
            return False
        
    def _test_keybind(self, keybind: Keybind) -> bool:
        
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
    
    def update(self) -> "KeybindsManager":
        for keybinds in self._keybinds.values():
            for keybind in keybinds:
                if self._test_keybind(keybind):
                    keybind.action()
                    
        return self
