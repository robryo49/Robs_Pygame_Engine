from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pymunk

from ..events import Event, Events
from ..utils import vec2

if TYPE_CHECKING:
    from .physics_body import PhysicsBody
    from ..objects import PygameObject, Layer


class PhysicsWorld:
    def __init__(self, owner_layer: Layer, gravity: vec2 = vec2(0, 980), iterations: int = 10):
        self._owner = owner_layer
        self._event_queue: list[Event] = []
        self._event_manager = self._owner.event_manager

        self._space = pymunk.Space()
        self._space.gravity = (gravity.x, gravity.y)
        self._space.iterations = iterations
        self._space.collision_slop = 0.01
        self._space.collision_bias = pow(1.0 - 0.1, 60.0)

        self._bodies: list[PhysicsBody] = []

        self._constraints: list[pymunk.Constraint] = []

        self._fixed_dt = 1.0 / 120.0
        self._time_accumulator = 0.0

        self._setup_default_collision_handlers()

    # region PROPERTIES

    @property
    def space(self) -> pymunk.Space:
        return self._space

    @property
    def bodies(self) -> list[PhysicsBody]:
        return self._bodies

    @property
    def gravity(self) -> vec2:
        g = self._space.gravity
        return vec2(g.x, g.y)

    @gravity.setter
    def gravity(self, value: vec2):
        self._space.gravity = (value.x, value.y)

    # endregion

    # region BODY MANAGEMENT

    def add_body(self, body: PhysicsBody) -> "PhysicsWorld":
        if body not in self._bodies:
            body.create_body(self._space)
            self._bodies.append(body)
        return self

    def remove_body(self, body: PhysicsBody) -> "PhysicsWorld":
        if body in self._bodies:
            body.remove()
            self._bodies.remove(body)
        return self

    def clear(self) -> "PhysicsWorld":
        for constraint in list(self._constraints):
            constraint.remove()
        self._constraints.clear()
        for body in list(self._bodies):
            body.remove()
        self._bodies.clear()
        return self

    # endregion

    # region COLLISION HANDLERS

    def _setup_default_collision_handlers(self):
        self._space.on_collision(
            collision_type_a=0,
            collision_type_b=0,
            begin=lambda arb, space, data: self._on_collision_handler(arb, space, data, is_begin=True),
            separate=lambda arb, space, data: self._on_collision_handler(arb, space, data, is_begin=False),
        )

    def _on_collision_handler(self, arbiter: pymunk.Arbiter, space: pymunk.Space, data, is_begin: bool):
        shape_a, shape_b = arbiter.shapes
        obj_a: Optional[PygameObject] = self.get_shape_owner(shape_a)
        obj_b: Optional[PygameObject] = self.get_shape_owner(shape_b)

        if not obj_a or not obj_b:
            return
        
        obj_a: PygameObject
        obj_b: PygameObject

        is_sensor = shape_a.sensor or shape_b.sensor
        event_type = (Events.TRIGGER_ENTER if is_sensor else Events.COLLISION_BEGIN) if is_begin else (Events.TRIGGER_EXIT if is_sensor else Events.COLLISION_END)

        event = Event(event_type, obj_a=obj_a, obj_b=obj_b, arbiter=arbiter, space=space, data=data)
        self._event_queue.append(event)
    
    def _handle_event_queue(self):
        for e in self._event_queue:
            if e.is_of_type(Events.TRIGGER_ENTER, Events.COLLISION_BEGIN):
                e.obj_a.on_collision(e.obj_b)
                e.obj_b.on_collision(e.obj_a)
            elif e.is_of_type(Events.TRIGGER_EXIT, Events.COLLISION_END):
                e.obj_a.on_collision(e.obj_b)
                e.obj_b.on_collision(e.obj_a)
            self._event_manager.trigger(e)
        self._event_queue.clear()

    # endregion

    # region UPDATE

    def sync_to_physics(self):
        for body in list(self._bodies):
            body.sync_to_physics()

    def sync_from_physics(self):
        for body in list(self._bodies):
            body.sync_from_physics()
        self._space.reindex_static()

    def step(self, dt: float):
        if dt > 0:
            self._time_accumulator += dt
            max_steps = 8
            steps = 0
            while self._time_accumulator >= self._fixed_dt and steps < max_steps:
                self._space.step(self._fixed_dt)
                self._time_accumulator -= self._fixed_dt
                steps += 1
            if steps >= max_steps:
                self._time_accumulator = 0.0

    def update(self, dt: float):
        self.sync_to_physics()
        self.step(dt)
        self.sync_from_physics()
        self._handle_event_queue()

    # endregion

    # region QUERY

    def query_point(self, point: vec2):
        return self._space.point_query((point.x, point.y), 1, pymunk.ShapeFilter())

    def query_segment(self, start: vec2, end: vec2, radius: float = 0):
        return self._space.segment_query((start.x, start.y), (end.x, end.y), radius, pymunk.ShapeFilter())

    # endregion

    def __repr__(self) -> str:
        return f"PhysicsWorld(bodies={len(self._bodies)})"
    
    
    @staticmethod
    def get_shape_owner(shape) -> "PygameObject | None":
        return getattr(shape, "owner_ref", None)
