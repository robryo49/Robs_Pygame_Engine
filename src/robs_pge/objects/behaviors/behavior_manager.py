"""Behavior managers that dispatch events to attached behaviors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Iterator

from .behavior import ObjectBehavior, LayoutObjectBehavior
from ...events import Event
from ...utils import vec2

if TYPE_CHECKING:
    from ..object import PygameObject
    from ..custom import LayoutObject


class BehaviorManager:
    """Ordered collection of behaviors attached to a single object."""

    def __init__(self, owner: PygameObject) -> None:
        """
        Initialize a behavior manager for an owner.

        :param owner: Object that owns these behaviors.
        """
        self._behaviors: dict[str, ObjectBehavior] = {}
        self._owner: PygameObject = owner

    # region PROPERTIES

    @property
    def owner(self) -> PygameObject:
        """Return the object that owns these behaviors."""
        return self._owner

    # endregion

    def add(self, behavior: ObjectBehavior, behavior_id: Optional[str] = None) -> ObjectBehavior:
        """
        Attach a behavior, replacing any existing behavior with the same ID.

        :param behavior: Behavior instance to attach.
        :param behavior_id: Optional identifier; defaults to the behavior's hash.
        :return: The attached behavior.
        """
        if behavior_id is None:
            behavior_id = str(hash(behavior))

        existing = self.get(behavior_id)
        if existing is not None:
            self.remove(existing)

        self._behaviors[behavior_id] = behavior

        behavior.owner = self.owner
        behavior.on_attach()

        return behavior

    def get(self, behavior_id: str) -> Optional[ObjectBehavior]:
        """
        Return a behavior by ID, if present.

        :param behavior_id: Identifier of the behavior to retrieve.
        :return: The matching behavior, or ``None`` when no behavior has that ID.
        """
        return self._behaviors.get(behavior_id)

    def get_id(self, behavior: ObjectBehavior) -> Optional[str]:
        """
        Return the ID for a behavior instance, if attached.

        :param behavior: Behavior instance to look up.
        :return: The behavior's identifier, or ``None`` when it is not attached.
        """
        return next((key for key, value in self._behaviors.items() if value is behavior), None)

    def remove(self, behavior: ObjectBehavior | str) -> Optional[ObjectBehavior]:
        """
        Detach and return a behavior, if present.

        :param behavior: Behavior instance or identifier to detach.
        :return: The detached behavior, or ``None`` when it was not attached.
        """
        if isinstance(behavior, str):
            behavior_id = behavior
            resolved = self._behaviors.get(behavior_id)
        else:
            resolved = behavior
            behavior_id = self.get_id(resolved)

        if behavior_id is not None:
            self._behaviors.pop(behavior_id, None)

        if resolved is not None:
            resolved.on_detach()
            resolved.owner = None

        return resolved

    def __iter__(self) -> Iterator[ObjectBehavior]:
        """
        Iterate over attached behaviors in insertion order.

        :return: Iterator over the attached behaviors.
        """
        return iter(self._behaviors.values())
    
    def on_hover(self) -> None:
        """Dispatch a hover event to all behaviors."""
        for b in self:
            b.on_hover()
        
    def on_hover_end(self) -> None:
        """Dispatch a hover-end event to all behaviors."""
        for b in self:
            b.on_hover_end()
        
    def on_hover_start(self) -> None:
        """Dispatch a hover-start event to all behaviors."""
        for b in self:
            b.on_hover_start()
        
    def on_click(self, button: int, pos: vec2) -> None:
        """
        Dispatch a click event to all behaviors.

        :param button: Mouse button index.
        :param pos: Position in the owner's local space.
        """
        for b in self:
            b.on_click(button, pos)
        
    def on_hold(self, button: int, pos: vec2) -> None:
        """
        Dispatch a hold event to all behaviors.

        :param button: Mouse button index.
        :param pos: Position in the owner's local space.
        """
        for b in self:
            b.on_hold(button, pos)
        
    def on_release(self, button: int, pos: vec2) -> None:
        """
        Dispatch a release event to all behaviors.

        :param button: Mouse button index.
        :param pos: Position in the owner's local space.
        """
        for b in self:
            b.on_release(button, pos)
            
    def on_update(self, dt: float) -> None:
        """
        Dispatch an update event to all behaviors.

        :param dt: Elapsed time in seconds since the previous update.
        """
        for b in self:
            b.on_update(dt)
            
    def on_event(self, event: Event) -> None:
        """
        Dispatch an event to all behaviors.

        :param event: Event to dispatch.
        """
        for b in self:
            b.on_event(event)
    
    def on_scroll(self, scroll: int, pos: vec2) -> None:
        """
        Dispatch a scroll event to all behaviors.

        :param scroll: Scroll amount.
        :param pos: Position in the owner's local space.
        """
        for b in self:
            b.on_scroll(scroll, pos)
            
    def on_collision(self, obj: PygameObject) -> None:
        """
        Dispatch a collision-begin event to all behaviors.

        :param obj: Other object involved in the collision.
        """
        for b in self:
            b.on_collision(obj)
    
    def on_collision_end(self, obj: PygameObject) -> None:
        """
        Dispatch a collision-end event to all behaviors.

        :param obj: Other object involved in the collision.
        """
        for b in self:
            b.on_collision_end(obj)


class LayoutBehaviorManager(BehaviorManager):
    """Behavior manager that also dispatches layout membership hooks."""

    def __init__(self, owner: LayoutObject) -> None:
        """
        Initialize a layout behavior manager for an owner.

        :param owner: Layout object that owns these behaviors.
        """
        super().__init__(owner)

    def on_object_addition(self, obj: PygameObject) -> None:
        """
        Notify layout behaviors that an object was added.

        :param obj: Object added to the layout.
        """
        for behavior in self:
            if isinstance(behavior, LayoutObjectBehavior):
                behavior.on_object_addition(obj)

    def on_object_removal(self, obj: PygameObject) -> None:
        """
        Notify layout behaviors that an object was removed.

        :param obj: Object removed from the layout.
        """
        for behavior in self:
            if isinstance(behavior, LayoutObjectBehavior):
                behavior.on_object_removal(obj)

