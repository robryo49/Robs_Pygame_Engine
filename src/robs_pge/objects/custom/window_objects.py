from .primitive_objects import RectObject
from ..behaviors import *
from ..object import PygameObject
from ...rendering import RectRenderer
from ...utils import Anchor, DictCollection, FRect, Transform, TypedDictCollection, Vec2


class WindowObject(RectObject):
    def __init__(self, transform: Transform, renderer: RectRenderer, margin: int, services: DictCollection, layer: int = 0, anchor: Vec2 = Anchor.C):
        super().__init__(transform, renderer, services, layer, anchor)
        
        self._margin = margin
        
        self._tabs = TypedDictCollection(str, PygameObject)
        self._current_tab: Optional[PygameObject] = None
        self._current_tab_name: Optional[str] = None
        
        self.update_children_clip_area()
    
    # region PROPERTIES
    
    # region width
    
    @property
    def width(self):
        return self.renderer.width
    
    @width.setter
    def width(self, value):
        self.renderer.width = value
        self.update_children_clip_area()
    
    # endregion
    
    # region width
    
    @property
    def height(self):
        return self.renderer.height
    
    @height.setter
    def height(self, value):
        self.renderer.height = value
        self.update_children_clip_area()
    
    # endregion
    
    # region width
    
    @property
    def dims(self):
        return self.renderer.dims
    
    @dims.setter
    def dims(self, value):
        self.renderer.dims = value
        self.update_children_clip_area()
    
    # endregion
    
    # endregion
    
    def update_children_clip_area(self):
        width, height = self.dims
        self.children_clip_area = FRect(self._margin - width*0.5, self._margin - height*0.5, width - 2*self._margin, height - 2*self._margin)
        
        return self
    
    def add_tab(self, name: str, tab: PygameObject):
        self.add_child(tab, Anchor.T)
        tab.anchor = Anchor.T
        tab.pos = Vec2(0, -self._margin)
        
        tab.do_on_scroll(lambda o, s, p: o.move_y(s*10))
        tab.make_attribute_clamped("y_pos", -self._margin, lambda: max(0, tab.height-self.children_clip_area.height)-self._margin)
        
        if self._current_tab is None and len(self._tabs) == 0:
            self._current_tab = tab
            self._current_tab_name = name
        else:
            tab.hide()
        self._tabs[name] = tab
        
        return self
    
    def set_tab(self, tab: Optional[str | PygameObject]):
        if tab is None:
            self.close_tab()
        
        if isinstance(tab, str):
            if self._current_tab is not None:
                self._current_tab.hide()
            
            self._current_tab_name = tab
            self._current_tab = self._tabs[tab]
            if self._current_tab is not None:
                self._current_tab.show()
        
        if isinstance(tab, PygameObject):
            for n, t in self._tabs.items():
                if t is tab:
                    self.set_tab(n)
        
        return self
    
    def close_tab(self):
        if self._current_tab is not None:
            self._current_tab.hide()
        
        self._current_tab = None
        self._current_tab_name = None
        
        return self
        
        
        