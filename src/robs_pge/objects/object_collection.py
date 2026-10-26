"""Deferred-mutation collection used for scene object hierarchies."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import Any, TYPE_CHECKING

from ..rendering import DrawCommand

if TYPE_CHECKING:
    from .object import PygameObject


class ObjectCollection:
    """Ordered object collection with deferred additions and removals."""

    def __init__(self, objects: Iterable[PygameObject] = ()) -> None:
        """
        Initialize a collection with optional initial objects.

        :param objects: Iterable of objects to include immediately.
        """
        self._objects: list[PygameObject] = list(objects)

        self._to_remove: list[PygameObject] = []
        self._to_add: list[PygameObject] = []

        self._frozen = False
        self._rendering_enabled = True

    # region PROPERTIES

    @property
    def frozen(self) -> bool:
        """Return whether updates and rendering are currently suspended."""
        return self._frozen

    @property
    def rendering_enabled(self) -> bool:
        """Return whether this collection is allowed to render."""
        return self._rendering_enabled

    @property
    def size(self) -> int:
        """Return the number of direct objects in the collection."""
        return len(self._objects)

    @property
    def full_size(self) -> int:
        """Return the number of direct objects plus all descendants."""
        return self.size + sum(o.children.full_size for o in self._objects)

    # endregion

    @staticmethod
    def flatten_objects(
        objects: Iterable[PygameObject | Iterable[PygameObject]],
    ) -> Iterator[PygameObject]:
        """
        Yield objects from nested iterables, flattening recursively.

        :param objects: Objects or nested iterables of objects.
        :return: Iterator over flattened objects.
        """
        from .object import PygameObject

        for obj in objects:
            if isinstance(obj, PygameObject):
                yield obj
            elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
                yield from ObjectCollection.flatten_objects(obj)
            else:
                yield obj

    def toggle_rendering(self) -> ObjectCollection:
        """
        Toggle rendering for this collection.

        :return: This collection.
        """
        self._rendering_enabled = not self._rendering_enabled
        return self

    def enable_rendering(self) -> ObjectCollection:
        """
        Enable rendering for this collection.

        :return: This collection.
        """
        self._rendering_enabled = True
        return self

    def disable_rendering(self) -> ObjectCollection:
        """
        Disable rendering for this collection.

        :return: This collection.
        """
        self._rendering_enabled = False
        return self

    def toggle_frozen(self) -> ObjectCollection:
        """
        Toggle the frozen state of this collection.

        :return: This collection.
        """
        self._frozen = not self._frozen
        return self

    def freeze(self) -> ObjectCollection:
        """
        Prevent contained objects from updating or rendering.

        :return: This collection.
        """
        self._frozen = True
        return self

    def unfreeze(self) -> ObjectCollection:
        """
        Allow contained objects to update and render again.

        :return: This collection.
        """
        self._frozen = False
        return self

    def _handle_object_additions(self) -> ObjectCollection:
        """
        Apply queued additions to the object list.

        :return: This collection.
        """
        if not self._to_add:
            return self

        for obj in self._to_add:
            if obj not in self._objects:
                self._objects.append(obj)

        self._to_add.clear()
        return self

    def _handle_object_removals(self) -> ObjectCollection:
        """
        Apply queued removals from the object list.

        :return: This collection.
        """
        if not self._to_remove:
            return self

        for obj in self._to_remove:
            if obj in self._objects:
                self._objects.remove(obj)

        self._to_remove.clear()
        return self

    def add(self, *objects: PygameObject | Iterable[PygameObject]) -> ObjectCollection:
        """
        Queue one or more objects for addition.

        :param objects: Objects or iterables of objects to add.
        :return: This collection.
        """
        return self.add_object(*objects)

    def add_object(self, *objects: PygameObject | Iterable[PygameObject]) -> ObjectCollection:
        """
        Queue one or more objects, or iterables of objects, for addition.

        :param objects: Objects or iterables of objects to add.
        :return: This collection.
        """
        for obj in self.flatten_objects(objects):
            if obj in self._to_remove:
                self._to_remove.remove(obj)
            if self.has(obj):
                continue
            self._to_add.append(obj)
        return self

    def remove(self, *objects: PygameObject | Iterable[PygameObject]) -> ObjectCollection:
        """
        Queue one or more objects for removal.

        :param objects: Objects or iterables of objects to remove.
        :return: This collection.
        """
        return self.remove_object(*objects)

    def remove_object(self, *objects: PygameObject | Iterable[PygameObject]) -> ObjectCollection:
        """
        Queue one or more objects, or iterables of objects, for removal.

        :param objects: Objects or iterables of objects to remove.
        :return: This collection.
        """
        for obj in self.flatten_objects(objects):
            if obj in self._to_add:
                self._to_add.remove(obj)
                continue
            if self.has(obj) and obj not in self._to_remove:
                self._to_remove.append(obj)
        return self

    def clear(self) -> ObjectCollection:
        """
        Queue every contained object for removal.

        :return: This collection.
        """
        return self.remove_object(*self._objects)

    def update(self, dt: float) -> ObjectCollection:
        """
        Apply queued mutations and update all non-frozen objects.

        :param dt: Elapsed time in seconds since the previous update.
        :return: This collection.
        """
        self._handle_object_additions()
        self._handle_object_removals()

        if not self._frozen:
            for obj in self._objects:
                obj.update(dt)

        return self

    def render(self, submit: Callable[[DrawCommand], Any]) -> ObjectCollection:
        """
        Render all contained objects when rendering is enabled.

        :param submit: Callback that accepts draw commands.
        :return: This collection.
        """
        if self._rendering_enabled and not self._frozen:
            for obj in self._objects:
                obj.render(submit)

        return self

    def has(self, item: PygameObject) -> bool:
        """
        Return whether an object is present or queued for addition.

        :param item: Object to check.
        :return: ``True`` when the object is present and not queued for removal.
        """
        return (item in self._objects or item in self._to_add) and item not in self._to_remove

    def __contains__(self, item: object) -> bool:
        """
        Return whether an object is present or queued for addition.

        :param item: Object to check.
        :return: ``True`` when the object is present and not queued for removal.
        """
        return (
            self._objects.__contains__(item) or item in self._to_add
        ) and item not in self._to_remove

    def __iter__(self) -> Iterator[PygameObject]:
        """
        Iterate over direct objects.

        :return: Iterator over direct objects.
        """
        return iter(self._objects)

    def __len__(self) -> int:
        """
        Return the number of direct objects.

        :return: Number of direct objects.
        """
        return self.size

    def __bool__(self) -> bool:
        """
        Return whether the collection contains any direct objects.

        :return: ``True`` when at least one direct object is present.
        """
        return self.size > 0

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"ObjectCollection(size={self.size}, pending_add={len(self._to_add)}, pending_remove={len(self._to_remove)})"
