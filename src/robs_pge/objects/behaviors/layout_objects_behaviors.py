from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from ..behavior import LayoutObjectBehavior
from ...rendering import RectStyle
from ...utils import vec2, Callback, Color, Anchor

if TYPE_CHECKING:
    from ...objects import PygameObject, LayoutObject
    from ..object_factory import ObjectFactory


class ActionOnObjectAdditionBehavior(LayoutObjectBehavior):
    def __init__(
            self,
            on_object_addition: Callback[[LayoutObject, PygameObject], Any] = None,
            on_object_removal: Callback[[LayoutObject, PygameObject], Any] = None,
    ):
        super().__init__()

        self._on_object_addition: Callback[[LayoutObject, PygameObject], Any] = on_object_addition
        self._on_object_removal: Callback[[LayoutObject, PygameObject], Any] = on_object_removal

    def on_object_addition(self, obj: PygameObject) -> None:
        self._exec(self._on_object_addition, self.owner, obj)

    def on_object_removal(self, obj: PygameObject) -> None:
        self._exec(self._on_object_removal, self.owner, obj)


class ReorderableLayoutBehavior(ActionOnObjectAdditionBehavior):
    def __init__(self, placeholder_style: RectStyle):
        super().__init__()

        self._placeholder_style = placeholder_style
        self._factory: Optional[ObjectFactory] = None

    def on_attach(self) -> None:
        super().on_attach()
        self._factory = self.owner.services.get_object_factory()

        for obj in self._owner._object_placements:
            self.on_object_addition(obj)

    def _start_dragging_object(self, obj: PygameObject):
        placeholder = self._factory.shape.rect(vec2(), obj.dims, RectStyle(Color(0, 0, 0, 100), 10, Color(0, 0, 0, 0), bd_radius=20))
        self.owner.replace_object(obj, placeholder, ignore_callbacks=True)
        self.owner.add_child(obj, Anchor.TL)
        obj.set_property("layout_placeholder", placeholder)
        obj.focus()

    def _while_dragging_object(self, obj: PygameObject):
        placeholder = obj.get_property("layout_placeholder")
        owner = self.owner

        x, y = obj.pos
        dx, dy = x - placeholder.pos.x, y - placeholder.pos.y

        col, row = owner.get_object_placement(placeholder)

        next_col, next_row = col + 1 if dx >= 0 else col - 1, row + 1 if dy >= 0 else row - 1

        if owner.mode == owner.GRID_MODE:
            if 0 <= next_col <= owner.max_col:
                next_col_width = owner.get_col_width(next_col)
                if abs(dx) > next_col_width * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(next_col, row))
            if 0 <= next_row <= owner.max_row:
                next_row_height = owner.get_row_height(next_row)
                if abs(dy) > next_row_height * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(col, next_row))

        if owner.mode == owner.COL_MODE:

            if 0 <= next_col <= owner.max_col:
                next_col_width = owner.get_col_width(next_col)
                if abs(dx) > next_col_width * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(next_col, row))

            if 0 <= next_row <= owner.max_row:
                next_row_height = owner.get_row_height(next_row, col)
                if abs(dy) > next_row_height * 0.66:
                    owner.switch_object_positions(placeholder, owner.get_object_in_cell(col, next_row))

    def _end_dragging_object(self, obj: PygameObject):
        placeholder = obj.remove_property("layout_placeholder")
        self.owner.replace_object(placeholder, obj, ignore_callbacks=True)
        obj.unfocus()

    def on_object_addition(self, obj: PygameObject) -> None:
        super().on_object_addition(obj)

        obj.make_draggable(
            on_drag_start=self._start_dragging_object,
            while_dragging=self._while_dragging_object,
            on_drag_end=self._end_dragging_object,
        )

    def on_object_removal(self, obj: PygameObject) -> None:
        super().on_object_removal(obj)
        obj.remove_behavior("draggable_behavior")

