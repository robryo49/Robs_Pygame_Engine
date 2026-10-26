"""Behaviors that toggle visibility with camera zoom and provide drag handling."""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .behavior import ObjectBehavior
from ..object_flags import ObjectFlags
from ...utils import vec2, Callback

if TYPE_CHECKING:
    from ...core import Camera
    from ...objects import PygameObject



class HideOnCameraZoomBehavior(ObjectBehavior):
    """Hide the owner while the camera zoom is outside an optional range."""
    def __init__(self, camera: Camera, min_zoom: Optional[float] = None, max_zoom: Optional[float] = None) -> None:
        """
        Store the camera and optional zoom bounds.

        :param camera: Camera whose zoom controls visibility.
        :param min_zoom: Zoom below which the owner is hidden.
        :param max_zoom: Zoom above which the owner is hidden.
        """
        super().__init__()

        self._min_zoom = min_zoom
        self._max_zoom = max_zoom

        self._camera = camera

    def on_update(self, dt: float) -> None:
        """
        Apply or clear the hidden flag based on the current camera zoom.

        :param dt: Seconds elapsed since the previous update.
        """
        if (owner := self.owner) is None: return

        hide = False
        if self._max_zoom is not None and self._max_zoom < self._camera.zoom:
            hide = True
        if self._min_zoom is not None and self._min_zoom > self._camera.zoom:
            hide = True

        if hide:
            owner.add_flag(ObjectFlags.HIDDEN)
        else:
            owner.remove_flag(ObjectFlags.HIDDEN)


class DraggableBehavior(ObjectBehavior):
    """Move an owner or target object by dragging it with a mouse button."""
    def __init__(
            self, button: int = 1, target: Optional[PygameObject] = None,
            on_drag_start: Callback[[PygameObject], Any] = None,
            while_dragging: Callback[[PygameObject], Any] = None,
            on_drag_end: Callback[[PygameObject], Any] = None,
    ) -> None:
        """
        Store the drag button, target, and lifecycle callbacks.

        :param button: Mouse button used for dragging.
        :param target: Object to move, defaulting to the owner when omitted.
        :param on_drag_start: Callback invoked when dragging starts.
        :param while_dragging: Callback invoked on every drag update.
        :param on_drag_end: Callback invoked when dragging ends.
        """
        super().__init__()
        self._button: int = button
        self._target: Optional[PygameObject] = target
        self._dragging: bool = False
        self._has_moved: bool = False
        self._offset: vec2 = vec2(0, 0)

        self._on_drag_start: Callback[[PygameObject], Any] = on_drag_start
        self._while_dragging: Callback[[PygameObject], Any] = while_dragging
        self._on_drag_end: Callback[[PygameObject], Any] = on_drag_end

    @property
    def target(self) -> Optional[PygameObject]:
        """Return the object moved by dragging, defaulting to the owner."""
        return self._target if self._target is not None else self.owner

    @property
    def has_moved(self):
        """Return whether the target moved during the last drag update."""
        return self._has_moved

    def on_attach(self) -> None:
        """Mark the owner as draggable."""
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.DRAGGABLE)

    def on_click(self, button: int, pos: vec2) -> None:
        """
        Start dragging when the configured button is pressed.

        :param button: Mouse button that was pressed.
        :param pos: Pointer position in world coordinates.
        """
        if (target := self.target) is None: return

        if button == self._button:
            self._dragging = True
            self._offset = target.pos - target.world_to_parent_children_local(pos)
            self._exec(self._on_drag_start, self.owner)

    def on_hold(self, button: int, pos: vec2) -> None:
        """
        Move the target while the configured button is held.

        :param button: Mouse button currently held.
        :param pos: Pointer position in world coordinates.
        """
        if (target := self.target) is None: return

        if self._dragging and button == self._button:
            prev = target.pos
            new = target.world_to_parent_children_local(pos) + self._offset
            target.pos = new
            self._has_moved = prev != new
            self._exec(self._while_dragging, self.owner)

    def on_release(self, button: int, pos: vec2) -> None:
        """
        Stop dragging when the configured button is released.

        :param button: Mouse button that was released.
        :param pos: Pointer position in world coordinates.
        """
        if button == self._button:
            self._dragging = False
            self._exec(self._on_drag_end, self.owner)
            self._has_moved = False

