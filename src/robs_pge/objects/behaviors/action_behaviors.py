"""Behaviors that react to events, input, collisions, and attribute changes on pygame objects."""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from .behavior import ObjectBehavior
from ..object_flags import ObjectFlags
from ...events import Event
from ...utils import vec2, Callback

if TYPE_CHECKING:
    from ...objects import PygameObject


class ActionOnEventBehavior(ObjectBehavior):
    """Invoke a callback when one of the configured events is dispatched to the owner."""
    def __init__(self, event: str | Event | tuple[str | Event, ...], action: Callback[[PygameObject], Any]) -> None:
        """
        Store the event selector and the callback to run.

        :param event: Event or tuple of events that triggers the action.
        :param action: Callback invoked with the owner when the event matches.
        """
        super().__init__()

        self._event = event

        self._action = action

    def on_event(self, event: str | Event) -> None:

        """
        Run the action when the event matches the configured selector.

        :param event: Event being dispatched.
        """
        if isinstance(self._event, tuple):
            found = False
            for e in self._event:
                if Event.are_equal(e, event):
                    found = True
                    break
            if not found: return
        elif not Event.are_equal(self._event, event):
            return

        self._exec(self._action, self.owner)

class ActionOnUpdateBehavior(ObjectBehavior):
    """Invoke a callback on every update tick of the owner."""
    def __init__(self, action: Callback[[PygameObject], Any]) -> None:
        """
        Store the callback to run on each update.

        :param action: Callback invoked with the owner on every update.
        """
        super().__init__()

        self._action = action

    def on_update(self, dt: float) -> None:
        """
        Run the action for the current update tick.

        :param dt: Seconds elapsed since the previous update.
        """
        self._exec(self._action, self.owner)

class ActionOnClickBehavior(ObjectBehavior):
    """Invoke click, hold, and release callbacks for a mouse button."""
    def __init__(self, button: int, on_click: Callback[[PygameObject], Any] = None, on_hold: Callback[[PygameObject], Any] = None, on_release: Callback[[PygameObject], Any] = None) -> None:
        """
        Store the button and the click lifecycle callbacks.

        :param button: Mouse button that triggers the callbacks.
        :param on_click: Callback invoked when the button is pressed.
        :param on_hold: Callback invoked while the button is held.
        :param on_release: Callback invoked when the button is released.
        """
        super().__init__()

        self._button = button

        self._on_click = on_click
        self._on_hold = on_hold
        self._on_release = on_release

    def on_attach(self) -> None:
        """Mark the owner as clickable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.CLICKABLE)

    def on_click(self, button: int, pos: vec2) -> None:
        """
        Run the click callback when the configured button is pressed.

        :param button: Mouse button that was pressed.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._on_click, self.owner)

    def on_hold(self, button: int, pos: vec2) -> None:
        """
        Run the hold callback while the configured button is held.

        :param button: Mouse button currently held.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._on_hold, self.owner)

    def on_release(self, button: int, pos: vec2) -> None:
        """
        Run the release callback when the configured button is released.

        :param button: Mouse button that was released.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._on_release, self.owner)

class ActionOnHoverBehavior(ObjectBehavior):
    """Invoke hover callbacks as the pointer enters, stays over, and leaves the owner."""
    def __init__(self, hover_start: Callback[[PygameObject], Any] = None, while_hovered: Callback[[PygameObject], Any] = None, hover_end: Callback[[PygameObject], Any] = None) -> None:
        """
        Store the hover lifecycle callbacks.

        :param hover_start: Callback invoked when hovering begins.
        :param while_hovered: Callback invoked while the owner is hovered.
        :param hover_end: Callback invoked when hovering ends.
        """
        super().__init__()

        self._on_hover_start = hover_start
        self._on_hover = while_hovered
        self._on_hover_end = hover_end

    def on_attach(self) -> None:
        """Mark the owner as hoverable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.HOVERABLE)

    def on_hover(self) -> None:
        """Run the callback used while the owner is hovered."""
        self._exec(self._on_hover, self.owner)

    def on_hover_start(self) -> None:
        """Run the callback used when hovering begins."""
        self._exec(self._on_hover_start, self.owner)

    def on_hover_end(self) -> None:
        """Run the callback used when hovering ends."""
        self._exec(self._on_hover_end, self.owner)

class ActionOnScrollBehavior(ObjectBehavior):
    """Invoke a callback when the owner receives scroll input."""
    def __init__(self, action: Callback[[PygameObject, int, vec2], Any] = None) -> None:
        """
        Store the scroll callback.

        :param action: Callback invoked with the owner, scroll amount, and pointer position.
        """
        super().__init__()

        self._action = action

    def on_attach(self) -> None:
        """Mark the owner as scrollable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.SCROLLABLE)

    def on_scroll(self, scroll: int, pos: vec2) -> None:
        """
        Run the scroll callback for the current scroll input.

        :param scroll: Signed scroll amount.
        :param pos: Pointer position in world coordinates.
        """
        self._exec(self._action, self.owner, scroll, pos)

class ActionOnCollisionBehavior(ObjectBehavior):
    """Invoke callbacks when the owner begins, continues, and ends collisions."""
    def __init__(self, on_collision: Callback[[PygameObject, PygameObject], Any] = None, while_colliding: Callback[[PygameObject, PygameObject], Any] = None, on_collision_end: Callback[[PygameObject, PygameObject], Any] = None,
                 condition_on_other: Optional[Callable[[PygameObject], bool]] = None) -> None:
        """
        Store the collision lifecycle callbacks and other-object filter.

        :param on_collision: Callback invoked when a collision starts.
        :param while_colliding: Callback invoked on every update while colliding.
        :param on_collision_end: Callback invoked when a collision ends.
        :param condition_on_other: Optional predicate that filters which other objects trigger callbacks.
        """
        super().__init__()

        self._on_collision_action = on_collision
        self._while_colliding_action = while_colliding
        self._on_collision_end_action = on_collision_end

        self._condition_on_other = condition_on_other

        self._colliding_objects: list[PygameObject] = []

    def _validate(self, obj: PygameObject) -> bool:
        return self._condition_on_other is None or self._condition_on_other(obj)

    def on_collision(self, obj: PygameObject) -> None:
        """
        Record a new collision and run the collision-start callback.

        :param obj: Other object involved in the collision.
        """
        if self._validate(obj):
            self._exec(self._on_collision_action, self.owner, obj)
            self._colliding_objects.append(obj)

    def on_update(self, dt: float) -> None:
        """
        Run the while-colliding callback for every active collision.

        :param dt: Seconds elapsed since the previous update.
        """
        if self._colliding_objects:
            for obj in self._colliding_objects:
                self._exec(self._while_colliding_action, self.owner, obj)

    def on_collision_end(self, obj: PygameObject) -> None:
        """
        Forget an ending collision and run the collision-end callback.

        :param obj: Other object whose collision ended.
        """
        if self._validate(obj):
            self._exec(self._on_collision_end_action, self.owner, obj)
            self._colliding_objects.remove(obj)

class ActionOnAttributeChangeBehavior(ObjectBehavior):
    """Invoke a callback when a watched owner attribute changes between updates."""
    def __init__(self, attribute: str, action: Callable[[PygameObject], Any]) -> None:
        """
        Store the watched attribute and the change callback.

        :param attribute: Name of the owner attribute to watch.
        :param action: Callback invoked with the owner when the attribute changes.
        """
        super().__init__()

        self._attribute = attribute
        self._action = action

        self._previous_attribute_value = None

    def on_attach(self) -> None:
        """Record the initial value of the watched attribute."""
        self._previous_attribute_value = getattr(self.owner, self._attribute)

    def on_update(self, dt: float) -> None:
        """
        Compare the watched attribute and run the callback when it changed.

        :param dt: Seconds elapsed since the previous update.
        """
        current_attribute_value = getattr(self.owner, self._attribute)
        if current_attribute_value != self._previous_attribute_value:
            self._exec(self._action, self.owner)
            self._previous_attribute_value = current_attribute_value

