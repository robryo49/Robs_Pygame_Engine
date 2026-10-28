"""Behaviors that observe child additions and removals in layout objects."""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from .behavior import LayoutObjectBehavior
from ...rendering import RectStyle
from ...utils import vec2, Callback, Anchor

if TYPE_CHECKING:
    from ...objects import PygameObject, LayoutObject, ObjectFactory


class ActionOnObjectAdditionBehavior(LayoutObjectBehavior):
    """Invoke callbacks when objects are added to and removed from a layout."""
    def __init__(
            self,
            on_object_addition: Callback[[LayoutObject, PygameObject], Any] = None,
            on_object_removal: Callback[[LayoutObject, PygameObject], Any] = None,
    ) -> None:
        """
        Store the addition and removal callbacks.

        :param on_object_addition: Callback invoked when an object is added.
        :param on_object_removal: Callback invoked when an object is removed.
        """
        super().__init__()

        self._on_object_addition: Callback[[LayoutObject, PygameObject], Any] = on_object_addition
        self._on_object_removal: Callback[[LayoutObject, PygameObject], Any] = on_object_removal

    def on_object_addition(self, obj: PygameObject) -> None:
        """
        Run the object-addition callback.

        :param obj: Object that was added to the layout.
        """
        self._exec(self._on_object_addition, self.owner, obj)

    def on_object_removal(self, obj: PygameObject) -> None:
        """
        Run the object-removal callback.

        :param obj: Object that was removed from the layout.
        """
        self._exec(self._on_object_removal, self.owner, obj)


class ReorderableLayoutBehavior(ActionOnObjectAdditionBehavior):
    """Add drag-and-drop reordering with placeholder rectangles to a layout object."""
    def __init__(self, placeholder_style: RectStyle) -> None:
        """
        Store the style used for the drag placeholder.

        :param placeholder_style: Rectangle style for the placeholder left behind while dragging.
        """
        super().__init__()

        self._placeholder_style = placeholder_style
        self._factory: Optional[ObjectFactory] = None

    def on_attach(self) -> None:
        """Cache the object factory and make existing children reorderable."""
        super().on_attach()
        self._factory = self.owner.services.get_object_factory()

        for obj in self.owner.objects:
            self.on_object_addition(obj)

    def _start_dragging_object(self, obj: PygameObject):
        """
        Swap the dragged object for a placeholder and focus it.

        :param obj: Object being dragged.
        """
        if self._factory is None:
            return

        placeholder = self._factory.shape.rect(vec2(), obj.dims, self._placeholder_style)
        self.owner.replace_object(obj, placeholder, ignore_callbacks=True)
        self.owner.add_child(obj, Anchor.TL)
        obj.set_property("layout_placeholder", placeholder)
        obj.focus()

    def _while_dragging_object(self, obj: PygameObject):
        """
        Swap the placeholder with neighbors as the dragged object passes thresholds.

        :param obj: Object currently being dragged.
        """
        placeholder = obj.get_property("layout_placeholder")
        owner = self.owner

        if placeholder is None or not owner.has_object(placeholder):
            return

        x, y = obj.pos
        dx, dy = x - placeholder.pos.x, y - placeholder.pos.y

        col, row = owner.get_object_placement(placeholder)

        next_col, next_row = col + 1 if dx >= 0 else col - 1, row + 1 if dy >= 0 else row - 1

        if owner.mode in (owner.GRID_MODE, owner.COL_MODE):
            if 0 <= next_col <= owner.max_col:
                next_col_width = owner.get_col_width(next_col)
                if abs(dx) > next_col_width * 0.66:
                    other = owner.find_object_in_cell(next_col, row)
                    if other is not None:
                        owner.switch_object_positions(placeholder, other)
            if 0 <= next_row <= owner.max_row:
                next_row_height = owner.get_row_height(next_row, col) if owner.mode == owner.COL_MODE else owner.get_row_height(next_row)
                if abs(dy) > next_row_height * 0.66:
                    other = owner.find_object_in_cell(col, next_row)
                    if other is not None:
                        owner.switch_object_positions(placeholder, other)

    def _end_dragging_object(self, obj: PygameObject):
        """
        Replace the placeholder with the dragged object and unfocus it.

        :param obj: Object that finished dragging.
        """
        placeholder = obj.get_property("layout_placeholder")
        obj.remove_property("layout_placeholder")
        if placeholder is not None:
            self.owner.replace_object(placeholder, obj, ignore_callbacks=True)
        obj.unfocus()

    def on_object_addition(self, obj: PygameObject) -> None:
        """
        Make the added object draggable within the layout.

        :param obj: Object that was added to the layout.
        """
        super().on_object_addition(obj)

        obj.make_draggable(
            on_drag_start=self._start_dragging_object,
            while_dragging=self._while_dragging_object,
            on_drag_end=self._end_dragging_object,
        )

    def on_object_removal(self, obj: PygameObject) -> None:
        """
        Remove the draggable behavior from the removed object.

        :param obj: Object that was removed from the layout.
        """
        super().on_object_removal(obj)
        obj.remove_behavior("draggable_behavior")

