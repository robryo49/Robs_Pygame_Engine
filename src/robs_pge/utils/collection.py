from typing import Any, Callable, Generic, Iterable, Mapping, SupportsIndex, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Collection(list[T], Generic[T]):
    def __init__(self, iterable: Iterable[T] = ()):
        super().__init__(iterable)
    
    def _new(self, iterable: Iterable[T] = ()) -> "Collection[T]":
        return type(self)(iterable)
    
    def has(self, item: T) -> bool:
        return item in self
    
    def add(self, *items: T) -> None:
        self.extend(items)
    
    def remove_items(self, *items: T) -> None:
        for item in items:
            if item in self:
                super().remove(item)
    
    def copy(self) -> "Collection[T]":
        return self._new(self)
    
    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(index, slice):
            return self._new(result)
        return result
    
    def __add__(self, other):
        if not isinstance(other, list):
            return NotImplemented
        return self._new(super().__add__(other))
    
    def __radd__(self, other):
        if not isinstance(other, list):
            return NotImplemented
        return self._new(other + list(self))
    
    def __mul__(self, value):
        return self._new(super().__mul__(value))
    
    def __rmul__(self, value):
        return self.__mul__(value)
    
    def __iadd__(self, other):
        self.extend(other)
        return self
    
    def __imul__(self, value):
        super().__imul__(value)
        return self
    
    def foreach(self, method: Callable[[T], Any]) -> None:
        for o in self:
            method(o)
    
    def filter(self, predicate: Callable[[T], bool]) -> "Collection[T]":
        return self._new(item for item in self if predicate(item))
    
    def remove_if(self, predicate: Callable[[T], bool]) -> None:
        for i in range(len(self) - 1, -1, -1):
            if predicate(self[i]):
                self.pop(i)
    
    def map[R, T2](self, mapper: Callable[[T2], R]) -> "Collection[R]":
        return Collection(mapper(item) for item in self)
    
    def any_match(self, predicate: Callable[[T], bool]) -> bool:
        return any(predicate(item) for item in self)
    
    def all_match(self, predicate: Callable[[T], bool]) -> bool:
        return all(predicate(item) for item in self)


class DictCollection(dict[K, V], Generic[K, V]):
    def _new(self, mapping=None) -> "DictCollection[K, V]":
        return type(self)(mapping or {})
    
    def has(self, key: K) -> bool:
        return key in self
    
    def set(self, key: K, value: V) -> None:
        self[key] = value
    
    def copy(self) -> "DictCollection[K, V]":
        return self._new(self)
    
    def __or__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        result = self.copy()
        result.update(other)
        return result
    
    def __ror__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        result = self._new(other)
        result.update(self)
        return result
    
    def __ior__(self, other):
        if not isinstance(other, dict):
            return NotImplemented
        self.update(other)
        return self
    
    @classmethod
    def fromkeys(cls, iterable, value=None):
        return cls(dict.fromkeys(iterable, value))
    
    def foreach(self, method: Callable[[V], Any]) -> None:
        for v in self.values():
            method(v)
    
    def filter(self, predicate: Callable[[V], bool]) -> "DictCollection[K, V]":
        return self._new({key: item for key, item in self.items() if predicate(item)})
    
    def remove_if(self, predicate: Callable[[V], bool]) -> None:
        keys_to_remove = [k for k, v in self.items() if predicate(v)]
        for k in keys_to_remove:
            self.pop(k)
    
    def map[R, V2](self, mapper: Callable[[V2], R]) -> "DictCollection[K, R]":
        return DictCollection({key: mapper(item) for key, item in self.items()})
    
    def any_match(self, predicate: Callable[[V], bool]) -> bool:
        return any(predicate(item) for item in self.values())
    
    def all_match(self, predicate: Callable[[V], bool]) -> bool:
        return all(predicate(item) for item in self.values())


class TypedCollection(Collection[T]):
    def __init__(self, item_type: type[T], iterable: Iterable[T] = ()):
        self._item_type = item_type
        super().__init__(iterable)
    
    def _validate(self, item: Any) -> None:
        if not isinstance(item, self.item_type):
            raise TypeError(
                f"Expected {self.item_type.__name__}, got {type(item).__name__}"
            )
    
    @property
    def item_type(self) -> type[T]:
        return self._item_type
    
    def _new(self, iterable: Iterable[T] = ()) -> "TypedCollection[T]":
        return type(self)(self.item_type, iterable)
    
    def append(self, item: T) -> None:
        self._validate(item)
        super().append(item)
    
    def extend(self, iterable: Iterable[T]) -> None:
        items = list(iterable)
        for item in items:
            self._validate(item)
        super().extend(items)
    
    def insert(self, index: SupportsIndex, item: T) -> None:
        self._validate(item)
        super().insert(index, item)
    
    def __setitem__(self, index, value) -> None:
        if isinstance(index, slice):
            values = list(value)
            for item in values:
                self._validate(item)
            super().__setitem__(index, values)
        else:
            self._validate(value)
            super().__setitem__(index, value)
    
    def map[R, T2](self, mapper: Callable[[T2], R], target_type: type[R] | None = None) -> "Collection[R]":
        mapped_items = [mapper(item) for item in self]
        if target_type is not None:
            return TypedCollection(target_type, mapped_items)
        return Collection(mapped_items)


class TypedDictCollection(DictCollection[K, V]):
    def __init__(
            self,
            key_type: type[K],
            value_type: type[V],
            mapping: Mapping[K, V] | Iterable[tuple[K, V]] | None = None,
            **kwargs: V
    ):
        self._key_type = key_type
        self._value_type = value_type
        super().__init__()
        
        if mapping is not None:
            self.update(mapping)
        if kwargs:
            self.update(kwargs)
    
    @property
    def key_type(self) -> type[K]:
        return self._key_type
    
    @property
    def value_type(self) -> type[V]:
        return self._value_type
    
    def _new(self, mapping=None) -> "TypedDictCollection[K, V]":
        return type(self)(self.key_type, self.value_type, mapping or {})
    
    def _validate(self, key: Any, value: Any) -> None:
        if not isinstance(key, self.key_type):
            raise TypeError(f"Expected key {self.key_type.__name__}, got {type(key).__name__}")
        if not isinstance(value, self.value_type):
            raise TypeError(f"Expected value {self.value_type.__name__}, got {type(value).__name__}")
    
    def __setitem__(self, key: K, value: V) -> None:
        self._validate(key, value)
        super().__setitem__(key, value)
    
    def update(self, mapping: Mapping[K, V] | Iterable[tuple[K, V]] = (), **kwargs: V) -> None:
        if hasattr(mapping, "items"):
            for key, value in mapping.items():
                self[key] = value
        else:
            for key, value in mapping:
                self[key] = value
        
        for key, value in kwargs.items():
            self[key] = value
    
    def setdefault(self, key: K, default: V | None = None):
        if key not in self:
            self._validate(key, default)
        return super().setdefault(key, default)