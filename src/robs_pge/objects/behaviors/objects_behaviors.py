from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from ..behavior import ObjectBehavior
from ...utils import ObjectFlags, vec2, Callback

if TYPE_CHECKING:
    from ...core import Camera
    from ...objects import PygameObject



class HideOnCameraZoomBehavior(ObjectBehavior):
    def __init__(self, camera: Camera, min_zoom: Optional[float] = None, max_zoom: Optional[float] = None):
        super().__init__()

        self._min_zoom = min_zoom
        self._max_zoom = max_zoom

        self._camera = camera

    def on_update(self, dt: float) -> None:
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
    def __init__(
            self, button: int = 1, target: Optional[PygameObject] = None,
            on_drag_start: Callback[[PygameObject], Any] = None,
            while_dragging: Callback[[PygameObject], Any] = None,
            on_drag_end: Callback[[PygameObject], Any] = None,
    ):
        super().__init__()
        self._button: int = button
        self._target: Optional[PygameObject] = target
        self._dragging: bool = False
        self._offset: vec2 = vec2(0, 0)

        self._on_drag_start: Callback[[PygameObject], Any] = on_drag_start
        self._while_dragging: Callback[[PygameObject], Any] = while_dragging
        self._on_drag_end: Callback[[PygameObject], Any] = on_drag_end

    @property
    def target(self) -> Optional[PygameObject]:
        return self._target if self._target is not None else self.owner

    def on_attach(self) -> None:
        if (owner := self.owner) is None: return
        owner.add_flag(ObjectFlags.DRAGGABLE)

    def on_click(self, button: int, pos: vec2) -> None:
        if (target := self.target) is None: return

        if button == self._button:
            self._dragging = True
            self._offset = target.pos - target.world_to_parent_children_local(pos)
            self._exec(self._on_drag_start, self.owner)

    def on_hold(self, button: int, pos: vec2) -> None:
        if (target := self.target) is None: return

        if self._dragging and button == self._button:
            target.pos = target.world_to_parent_children_local(pos) + self._offset
            self._exec(self._while_dragging, self.owner)

    def on_release(self, button: int, pos: vec2) -> None:
        if button == self._button:
            self._dragging = False
            self._exec(self._on_drag_end, self.owner)

