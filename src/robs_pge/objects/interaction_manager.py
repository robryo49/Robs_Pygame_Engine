"""Mouse interaction routing for hovered and active scene objects."""

from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

import pygame as pg

from .object import PygameObject
from .object_collection import ObjectCollection
from ..input import InputManager
from ..utils import ObjectFlags, vec2

if TYPE_CHECKING:
    from ..objects import LayerManager


class InteractionManager:
    """Route mouse input to hovered and active scene objects."""
    def __init__(self, input_manager: InputManager) -> None:
        """
        Initialize interaction state from an input manager.

        :param input_manager: Input manager used to read mouse state.
        """
        self._input = input_manager
        
        self._all_hovered: list[PygameObject] = []
        self._top_hovered: Optional[PygameObject] = None
        
        self._mouse_pos = vec2()
        
        self._active: dict[int, Optional[PygameObject]] = {1: None, 2: None, 3: None}
    
    # region PROPERTIES
    
    @property
    def input(self):
        """Return the input manager used for mouse state."""
        return self._input
    
    @property
    def hovered(self):
        """Return the topmost hovered object."""
        return self._top_hovered
    
    # endregion
    
    def _collect_objects(self, object_collection: ObjectCollection) -> list[PygameObject]:
        """
        Recursively collect visible objects from a collection and their children.

        :param object_collection: Collection to traverse.
        :return: Visible objects in traversal order.
        """
        objects = []
        
        for obj in object_collection:
            if isinstance(obj, ObjectCollection):
                objects.extend(self._collect_objects(obj))
            elif isinstance(obj, PygameObject):
                if obj.visible:
                    objects.append(obj)
                objects.extend(self._collect_objects(obj.children))
        
        return objects
    
    @staticmethod
    def _get_first(objects: list[PygameObject], object_filter: Optional[Callable[[PygameObject], bool]] = None) -> Optional[PygameObject]:
        """
        Return the first object matching an optional filter.

        :param objects: Candidate objects in priority order.
        :param object_filter: Optional predicate the object must satisfy.
        :return: The first matching object, or ``None`` when no object matches.
        """
        if not objects:
            return None
        if object_filter is None:
            return objects[0]
        for obj in objects:
            if object_filter(obj):
                return obj
        return None
    
    def _collect_hovered_from_layers(self, layer_manager: "LayerManager") -> list[PygameObject]:
        """
        Collect hovered interactable objects across interactable layers.

        :param layer_manager: Layer manager whose layers are tested.
        :return: Hovered objects ordered from topmost to bottommost.
        """
        all_hovered: list[PygameObject] = []
        
        for layer in layer_manager.interactable_layers_reversed():
            camera = layer.camera
            mouse_pos = self._input.mouse.world_pos(camera)
            
            objects = self._collect_objects(layer.objects)
            objects.reverse()
            layer_hovered = [obj for obj in objects if obj.has_flag(ObjectFlags.INTERACTABLE) and obj.test_world_hit(mouse_pos)]
            all_hovered.extend(sorted(layer_hovered, key=lambda c: c.sub_layer, reverse=True))
        
        return all_hovered
    
    def _handle_hover(self, hovered: list[PygameObject]) -> None:
        """
        Update hover state and dispatch hover callbacks.

        :param hovered: Objects currently under the pointer.
        """
        previous_hovered = self._top_hovered
        
        if any(self._active.values()):
            self._top_hovered = self._active[1] or self._active[2] or self._active[3]
        else:
            self._top_hovered = self._get_first(hovered, lambda obj: obj.has_flag(ObjectFlags.HOVERABLE))
            
        top = self._top_hovered
        if previous_hovered is top:
            if top is not None:
                top.while_hovered()
        else:
            if previous_hovered:
                previous_hovered.on_hover_end()
            if top is not None:
                top.on_hover_start()
    
    def _handle_button(self, button: int) -> None:
        """
        Process press, hold, and release state for one mouse button.

        :param button: Mouse button index.
        """
        screen_pos = self._mouse_pos

        if self._input.pressed_button(button):
            active = self._active[button] = self._top_hovered
            if active and active.has_flag(ObjectFlags.CLICKABLE):
                active.on_click(button, active.screen_to_world(screen_pos))

        active = self._active[button]
        if self._input.held_button(button) and active and active.has_flag(ObjectFlags.CLICKABLE):
            active.on_hold(button, active.screen_to_world(screen_pos))

        if self._input.released_button(button) and active:
            if active.has_flag(ObjectFlags.CLICKABLE):
                active.on_release(button, active.screen_to_world(screen_pos))
            self._active[button] = None

    def _handle_scroll(self, hovered: list[PygameObject]) -> None:
        """
        Dispatch a scroll event to the topmost scrollable hovered object.

        :param hovered: Objects currently under the pointer.
        """
        if not self._input.mouse_scroll:
            return
        
        first_scrollable = self._get_first(hovered, lambda obj: obj.has_flag(ObjectFlags.SCROLLABLE))
        
        if first_scrollable is not None:
            first_scrollable.on_scroll(
                self._input.mouse_scroll,
                first_scrollable.screen_to_world(self._mouse_pos),
            )

    def update(self, layer_manager: "LayerManager") -> "InteractionManager":
        """
        Update hover, button, scroll, and cursor state.

        :param layer_manager: Layer manager whose objects are interactable.
        :return: This interaction manager.
        """
        self._mouse_pos = self._input.mouse.pos
        
        hovered = self._collect_hovered_from_layers(layer_manager)
        
        self._handle_hover(hovered)
        
        self._handle_button(1)
        self._handle_button(2)
        self._handle_button(3)
        
        self._handle_scroll(hovered)
        
        top = self._top_hovered
        if top and top.has_flag(ObjectFlags.CLICKABLE):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)