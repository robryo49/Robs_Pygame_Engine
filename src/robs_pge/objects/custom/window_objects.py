from typing import Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, Vec2


class WindowObject(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection,
                 panel: LayoutObject, header: Optional[RectObject], title_panel: Optional[RectObject], title_text: Optional[TextObject],
                 layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        self._panel = panel
        self._header = header
        self._title_panel = title_panel
        self._title_text = title_text
        
    
    
        
        