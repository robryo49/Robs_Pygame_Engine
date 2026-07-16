from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional

from .object_collection import ObjectCollection
from .object import PygameObject
from ..input import InputManager
from ..utils import ObjectFlags, Vec2

import pygame as pg

if TYPE_CHECKING:
    from ..core import Camera


class InteractionManager:
    def __init__(self, input_manager: InputManager):
        self._input = input_manager
        
        self._hovered_ui: list[PygameObject] = []
        self._hovered_world: list[PygameObject] = []
        self._hovered: Optional[PygameObject] = None
        
        self._mouse_pos = Vec2()
        
        self._active: dict[int, Optional[PygameObject]] = {1:None, 2:None, 3:None}
    
    # region PROPERTIES
    
    @property
    def input(self):
        return self._input
    
    @property
    def hovered_ui(self):
        return list(self._hovered_ui)
    
    @property
    def hovered_world(self):
        return list(self._hovered_world)
    
    @property
    def hovered(self):
        return self._hovered
    
    # endregion
    
    def _collect_objects(self, object_collection: ObjectCollection):
        objects = []
        
        collection_objects: list[PygameObject | ObjectCollection] = object_collection.elements
        for obj in collection_objects:
            if isinstance(obj, ObjectCollection):
                objects.extend(self._collect_objects(obj))
            elif isinstance(obj, PygameObject):
                if obj.visible: objects.append(obj)
                objects.extend(self._collect_objects(obj.children))
            
        return objects
        
    
    def _handle_hover(self):
        previous_hovered = self._hovered
        self._hovered = self._hovered_ui[0] if self.hovered_ui and self._hovered_ui[0].has_flag(ObjectFlags.HOVERABLE) \
            else self._hovered_world[0] if self._hovered_world and self._hovered_world[0].has_flag(ObjectFlags.HOVERABLE) else None
        
        hovered = self.hovered
        if previous_hovered is self.hovered:
            if hovered is not None:
                hovered.while_hovered()
        else:
            if previous_hovered:
                previous_hovered.on_hover_end()
            if hovered is not None:
                hovered.on_hover_start()
    
    def _handle_button(self, button: int):
        if self.input.pressed_button(button):
            active = self._active[button] = self.hovered
            if active and active.has_flag(ObjectFlags.CLICKABLE):
                active.on_click(button, self._mouse_pos)
        
        active = self._active[button]
        if self.input.held_button(button) and active and active.has_flag(ObjectFlags.CLICKABLE):
            active.on_hold(button, self._mouse_pos)
            
        if self.input.released_button(button) and active and active.has_flag(ObjectFlags.CLICKABLE):
            active.on_release(button, self._mouse_pos)
            self._active[button] = None
            
    def _handle_scroll(self):
        if self.input.mouse_scroll:
            hovered = self._hovered
            if hovered is not None:
                hovered.on_scroll(self.input.mouse_scroll, self._mouse_pos)
    
    def get_hovered_objects(self, objects: ObjectCollection, camera: Optional[Camera] = None):
        self._mouse_pos = self.input.mouse.world_pos(camera) if camera else self.input.mouse.pos
        objects = self._collect_objects(objects)
        objects.reverse()
        return [obj for obj in sorted(objects, key=lambda c: c.layer, reverse=True) if obj.test_world_hit(self._mouse_pos) and obj.has_flag(ObjectFlags.INTERACTABLE)]
    
    def update(self, objects: ObjectCollection, ui_objects: ObjectCollection, camera: Camera):
        
        self._hovered_ui = self.get_hovered_objects(ui_objects)
        self._hovered_world = self.get_hovered_objects(objects, camera)
    
        self._handle_hover()
        
        self._handle_button(1)
        self._handle_button(2)
        self._handle_button(3)
        
        self._handle_scroll()
        
        hovered = self.hovered
        if hovered and hovered.has_flag(ObjectFlags.CLICKABLE):
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
        else:
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)