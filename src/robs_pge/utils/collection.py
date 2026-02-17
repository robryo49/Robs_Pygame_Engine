from typing import Any


class Collection:
    def __init__(self, elements: list[Any] = None):
        self._elements: list[Any] = elements or []
    
    @property
    def elements(self):
        return self._elements
    
    def has(self, obj: Any):
        return obj in self.elements

    def add(self, obj: Any | list[Any]):
        if isinstance(obj, list):
            for e in obj:
                self.add(e)
        else:
            self.elements.append(obj)

    def remove(self, obj: Any | list[Any]):
        if isinstance(obj, list):
            for e in obj:
                self.remove(e)
        elif self.has(obj):
            self.elements.remove(obj)
    
    def get(self, index: int):
        return self.elements[index]
    
    def __setitem__(self, index: int, value):
        self.elements[index] = value

    def __getitem__(self, item: int):
        return self.elements[item]
    
    def __iter__(self):
        return iter(self.elements)
    
    def __contains__(self, item):
        return self.has(item)

    def __len__(self):
        return len(self.elements)
        

class DictCollection:
    def __init__(self, elements: dict = None):
        self._elements: dict = elements or {}
    
    @property
    def elements(self):
        return self._elements
    
    @property
    def values(self):
        return self.elements.values()
    
    @property
    def keys(self):
        return self.elements.keys()
    
    def has(self, key: Any):
        return key in self._elements
    
    def set(self, key: Any, obj: Any):
        self.elements[key] = obj
    
    def remove(self, key: Any):
        self.elements.pop(key, None)
        
    def get(self, key: Any, default=None):
        return self.elements.get(key, default)
    
    def __setitem__(self, key, value):
        self.elements[key] = value
    
    def __getitem__(self, key: Any):
        return self.elements[key]
    
    def __iter__(self):
        return iter(self.elements)
    
    def __contains__(self, item):
        return self.has(item)
    
    def __len__(self):
        return len(self._elements)
