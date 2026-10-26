"""Base behavior classes and event hooks for scene objects."""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from ...events import Event
from ...utils import vec2

if TYPE_CHECKING:
    from ...objects import PygameObject, LayoutObject


class ObjectBehavior[OwnerType: PygameObject = PygameObject]:
    """Base class for behaviors that can be attached to scene objects."""
    def __init__(self) -> None:
        """Initialize a behavior with no owner."""
        self._owner: Optional[OwnerType] = None
    
    # region PROPERTIES
    
    # region object
    @property
    def owner(self) -> Optional[OwnerType]:
        """Return the owner object this behavior is attached to, if any."""
        return self._owner
    
    @owner.setter
    def owner(self, value) -> Optional[OwnerType]:
        """
        Set the owner object this behavior is attached to, if any.

        :param value: The new value.
        """
        self._owner = value
    # endregion
    
    # endregion
    
    def _exec(self, action: Optional[Callable | tuple[Callable, ...]], *args, **kwargs) -> None:
        """
        Execute a callable action or each callable in a tuple in sequence.

        :param action: Callable to execute, a tuple of callables, or ``None``.
        :param args: Positional arguments passed to the callable.
        :param kwargs: Keyword arguments passed to the callable.
        """
        if action is not None:
            if isinstance(action, tuple):
                for action in action:
                    self._exec(action, *args, **kwargs)
            else:
                action(*args, **kwargs)
    
    @staticmethod
    def _evaluate[T](val_or_getter: Callable[[], T] | T) -> T:
        """
        Return a value, calling it first when it is a callable getter.

        :param val_or_getter: Value or zero-argument callable returning the value.
        :return: The resolved value.
        """
        return val_or_getter() if callable(val_or_getter) else val_or_getter
    
    def on_click(self, button: int, pos: vec2) -> None:
        """
        Handle a mouse button press on the owner.

        :param button: Mouse button index.
        :param pos: Position in the owner's local space.
        """
        pass
    def on_hold(self, button: int, pos: vec2) -> None:
        """
        Handle a held mouse button while the owner is active.

        :param button: Mouse button index.
        :param pos: Position in the owner's local space.
        """
        pass
    def on_release(self, button: int, pos: vec2) -> None:
        """
        Handle a mouse button release on the owner.

        :param button: Mouse button index.
        :param pos: Position in the owner's local space.
        """
        pass
    
    def on_hover_start(self) -> None:
        """Handle the pointer entering the owner."""
        pass
    def on_hover(self) -> None:
        """Handle continuous hovering over the owner."""
        pass
    def on_hover_end(self) -> None:
        """Handle the pointer leaving the owner."""
        pass
    
    def on_event(self, event: Event) -> None:
        """
        Handle an event dispatched to the owner.

        :param event: Event to handle.
        """
        pass
    
    def on_attach(self) -> None:
        """Handle the behavior being attached to an owner."""
        pass
    def on_detach(self) -> None:
        """Handle the behavior being detached from its owner."""
        pass
    
    def on_update(self, dt: float) -> None:
        """
        Handle the owner's per-frame update.

        :param dt: Elapsed time in seconds since the previous update.
        """
        pass
    
    def on_scroll(self, scroll: int, pos: vec2) -> None:
        """
        Handle mouse wheel scrolling over the owner.

        :param scroll: Scroll amount.
        :param pos: Position in the owner's local space.
        """
        pass
    
    def on_collision(self, obj: PygameObject) -> None:
        """
        Handle a collision beginning with another object.

        :param obj: Other object involved in the collision.
        """
        pass
    def on_collision_end(self, obj: PygameObject) -> None:
        """
        Handle a collision ending with another object.

        :param obj: Other object involved in the collision.
        """
        pass


class LayoutObjectBehavior[OwnerType: LayoutObject = LayoutObject](ObjectBehavior[OwnerType]):
    """Base class for behaviors attached to layout objects."""
    def on_object_addition(self, obj: PygameObject) -> None:
        """
        Handle an object being added to the layout.

        :param obj: Object added to the layout.
        """
        pass
    def on_object_removal(self, obj: PygameObject) -> None:
        """
        Handle an object being removed from the layout.

        :param obj: Object removed from the layout.
        """
        pass
