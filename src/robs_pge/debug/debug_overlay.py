from typing import Callable

from ..utils import Anchor, Font, Vec2


class DebugOverlay:
    def __init__(self):
        
        self._enabled = False
        self._freeze = False
    
    # region PROPERTIES
    
    @property
    def enabled(self):
        return self._enabled
    
    def toggle(self):
        self._enabled = not self._enabled
    
    def enable(self):
        self._enabled = True
    
    def disable(self):
        self._enabled = False
    
    @property
    def frozen(self):
        return self._freeze
        
    def toggle_freeze(self):
        self._freeze = not self._freeze
    
    def freeze(self):
        self._freeze = True
    
    def unfreeze(self):
        self._freeze = False
    
    # endregion
    
    def add_text(self, position: Vec2, template: str, getter: Callable | tuple[Callable, ...], font: Font, rotation: float=0.0, scale: float=1.0, layer: int=0, anchor: Vec2 = Anchor.TL):
        pass
    
    def render(self, submit):
        pass
        
    def update(self, dt):
        pass

