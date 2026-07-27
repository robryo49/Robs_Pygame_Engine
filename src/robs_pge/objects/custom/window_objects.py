from typing import Optional

from .primitive_objects import RectObject, TextObject
from .ui_objects import LayoutObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, Transform, Vec2


class WindowObject(LayoutObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, services: DictCollection,
                 title: str, content_panel: LayoutObject, header: Optional[LayoutObject], title_panel: Optional[RectObject], title_object: Optional[TextObject],
                 layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        self._id = title.lower().replace(" ", "_")
        self._title = title
        
        self._content = content_panel
        self._header = header
        self._title_panel = title_panel
        self._title_object = title_object
        
    # region PROPERTIES
    
    @property
    def content(self) -> LayoutObject:
        return self._content
    
    @property
    def header(self) -> Optional[LayoutObject]:
        return self._header
    
    @property
    def title_panel(self) -> Optional[RectObject]:
        return self._title_panel
    
    @property
    def title_object(self) -> Optional[TextObject]:
        return self._title_object
    
    @property
    def title(self):
        return self._title
    
    @property
    def id(self):
        return self._id
    
    # endregion
    
    def __repr__(self):
        return f"Window('{self.id}')"
        
        