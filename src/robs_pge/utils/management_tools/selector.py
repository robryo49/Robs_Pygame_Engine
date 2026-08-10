from typing import Any, Optional

from .types import Callback
from ... import TypedCollection


class Selector[T]:
    def __init__(self, element_type: type[T], selection_callback: Callback[[T], Any] = None, unselection_callback: Callback[[T], Any] = None):
        self.element_type: type[T] = element_type
        self.elements: TypedCollection[T] = TypedCollection(element_type)
        
        self.selected: Optional[T] = None
        
        self.selection_callback = selection_callback
        self.unselection_callback = unselection_callback
        
    def has_selected(self, element: T) -> bool:
        return self.selected is element
        
    def unselect_current(self):
        if self.selected is not None:
            self.unselection_callback(self.selected)
        self.selected = None
    
    def select(self, element: Optional[T] = None) -> T:
        if self.has_selected(element):
            return element
        
        self.unselect_current()
        self.selected = element
        if self.selected is not None:
            self.selection_callback(self.selected)
        
        return element
    
    def unselect(self, element: Optional[T] = None) -> T:
        if self.has_selected(element):
            self.unselect_current()
            
    def add(self, element: T):
        if not self.elements.has(element):
            self.elements.add(element)
    
    def remove(self, element: T):
        if self.elements.has(element):
            self.elements.remove(element)
        if self.has_selected(element):
            self.unselect_current()
            