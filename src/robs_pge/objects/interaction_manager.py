from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from typing import Optional

from .object_collection import ObjectCollection
from .object import PygameObject
from ..input import InputManager
from ..utils import ObjectFlags, Vec2

import pygame as pg

if TYPE_CHECKING:
    from ..core import Camera
    from ..objects import LayerManager


class InteractionManager:
    def __init__(self, input_manager: InputManager):
        self._input = input_manager
        
        self._hovered: list[PygameObject] = []
        self._top_hovered: Optional[PygameObject] = None
        
        self._mouse_pos = Vec2()
        
        self._active: dict[int, Optional[PygameObject]] = {1: None, 2: None, 3: None}
    
    # region PROPERTIES
    
    @property
    def input(self):
        return self._input
    
    @property
    def hovered(self):
        return self._top_hovered
    
    # endregion
    
    def _collect_objects(self, object_collection: ObjectCollection) -> list[PygameObject]:
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
        if not objects:
            return None
        if object_filter is None:
            return objects[0]
        for obj in objects:
            if object_filter(obj):
                return obj
        return None
    
    def _collect_hovered_from_layers(self, layer_manager: "LayerManager") -> list[PygameObject]:
        all_hovered: list[PygameObject] = []
        
        for layer in layer_manager.interactable_layers_reversed():
            camera = layer.camera
            mouse_pos = self._input.mouse.world_pos(camera)
            
            objects = self._collect_objects(layer.objects)
            objects.reverse()
            layer_hovered = [obj for obj in objects if obj.has_flag(ObjectFlags.INTERACTABLE) and obj.test_world_hit(mouse_pos)]
            all_hovered.extend(sorted(layer_hovered, key=lambda c: c.sub_layer, reverse=True))
        
        return all_hovered
    
    def _handle_hover(self, hovered: list[PygameObject]):
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
    
    def _handle_button(self, button: int):
        mouse_pos = self._mouse_pos
        
        if self._input.pressed_button(button):
            active = self._active[button] = self._top_hovered
            if active and active.has_flag(ObjectFlags.CLICKABLE):
                active.on_click(button, mouse_pos)
        
        active = self._active[button]
        if self._input.held_button(button) and active and active.has_flag(ObjectFlags.CLICKABLE):
            active.on_hold(button, mouse_pos)
        
        if self._input.released_button(button) and active and active.has_flag(ObjectFlags.CLICKABLE):
            active.on_release(button, mouse_pos)
            self._active[button] = None
    
    def _handle_scroll(self, hovered: list[PygameObject]):
        if not self._input.mouse_scroll:
            return
        
        first_scrollable = self._get_first(hovered, lambda obj: obj.has_flag(ObjectFlags.SCROLLABLE))
        
        if first_scrollable is not None:
            first_scrollable.on_scroll(self._input.mouse_scroll, self._mouse_pos)
    
    def update(self, layer_manager: "LayerManager"):
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