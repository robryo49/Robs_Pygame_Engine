"""Physics simulation world that steps pymunk and dispatches collisions."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import pymunk

from ..events import Event, Events
from ..utils import vec2

if TYPE_CHECKING:
    from .physics_body import PhysicsBody
    from ..objects import PygameObject, Layer


class PhysicsWorld:
    """Owns a pymunk space, its bodies, and collision event dispatch."""

    def __init__(self, owner_layer: Layer, gravity: vec2 = vec2(0, 980), iterations: int = 10) -> None:
        """
        Initialize a physics world for a layer.

        :param owner_layer: Layer that owns this physics world.
        :param gravity: Gravity vector.
        :param iterations: Number of solver iterations per step.
        """
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

    @property
    def space(self) -> pymunk.Space:
        """Return the underlying pymunk space."""
        return self._space

    @property
    def bodies(self) -> list[PhysicsBody]:
        """Return the physics bodies registered with this world."""
        return self._bodies

    @property
    def gravity(self) -> vec2:
        """Return the gravity vector applied by the physics space."""
        gravity = self._space.gravity
        return vec2(gravity.x, gravity.y)

    @gravity.setter
    def gravity(self, value: vec2) -> None:
        """
        Set the gravity vector applied by the physics space.

        :param value: The new value.
        """
        self._space.gravity = (value.x, value.y)

    def add_body(self, body: PhysicsBody) -> PhysicsWorld:
        """
        Add and initialize a physics body.

        :param body: Physics body to add.
        :return: This physics world.
        """
        if body not in self._bodies:
            body.create_body(self._space)
            self._bodies.append(body)
        return self

    def remove_body(self, body: PhysicsBody) -> PhysicsWorld:
        """
        Remove and tear down a physics body.

        :param body: Physics body to remove.
        :return: This physics world.
        """
        if body in self._bodies:
            body.remove()
            self._bodies.remove(body)
        return self

    def clear(self) -> PhysicsWorld:
        """
        Remove all constraints and bodies.

        :return: This physics world.
        """
        for constraint in list(self._constraints):
            constraint.remove()
        self._constraints.clear()
        for body in list(self._bodies):
            body.remove()
        self._bodies.clear()
        return self

    def _setup_default_collision_handlers(self) -> None:
        """Register collision handlers for the default collision type."""
        self._space.on_collision(
            collision_type_a=0,
            collision_type_b=0,
            begin=lambda arb, space, data: self._on_collision_handler(arb, space, data, is_begin=True),
            separate=lambda arb, space, data: self._on_collision_handler(arb, space, data, is_begin=False),
        )

    def _on_collision_handler(
        self,
        arbiter: pymunk.Arbiter,
        space: pymunk.Space,
        data: object,
        is_begin: bool,
    ) -> None:
        """
        Queue a collision or trigger event from a pymunk arbiter.

        :param arbiter: Pymunk arbiter describing the collision.
        :param space: Space in which the collision occurred.
        :param data: User data attached to the collision handler.
        :param is_begin: Whether the collision is beginning rather than ending.
        """
        shape_a, shape_b = arbiter.shapes
        obj_a = self.get_shape_owner(shape_a)
        obj_b = self.get_shape_owner(shape_b)

        if obj_a is None or obj_b is None:
            return

        is_sensor = shape_a.sensor or shape_b.sensor
        if is_begin:
            event_type = Events.TRIGGER_ENTER if is_sensor else Events.COLLISION_BEGIN
        else:
            event_type = Events.TRIGGER_EXIT if is_sensor else Events.COLLISION_END

        self._event_queue.append(
            Event(event_type, obj_a=obj_a, obj_b=obj_b, arbiter=arbiter, space=space, data=data)
        )

    def _handle_event_queue(self) -> None:
        """Dispatch queued collision events to objects and the event manager."""
        for event in tuple(self._event_queue):
            if event.is_of_type(Events.TRIGGER_ENTER, Events.COLLISION_BEGIN):
                event.obj_a.on_collision(event.obj_b)
                event.obj_b.on_collision(event.obj_a)
            elif event.is_of_type(Events.TRIGGER_EXIT, Events.COLLISION_END):
                event.obj_a.on_collision_end(event.obj_b)
                event.obj_b.on_collision_end(event.obj_a)
            self._event_manager.trigger(event)
        self._event_queue.clear()

    def sync_to_physics(self) -> None:
        """Copy object transforms into their pymunk bodies."""
        for body in list(self._bodies):
            body.sync_to_physics()

    def sync_from_physics(self) -> None:
        """Copy dynamic body transforms back into their objects."""
        for body in list(self._bodies):
            body.sync_from_physics()
        self._space.reindex_static()

    def step(self, dt: float) -> None:
        """
        Advance the physics space using fixed timesteps.

        :param dt: Elapsed time in seconds to simulate.
        """
        if dt <= 0:
            return

        self._time_accumulator += dt
        max_steps = 8
        steps = 0
        while self._time_accumulator >= self._fixed_dt and steps < max_steps:
            self._space.step(self._fixed_dt)
            self._time_accumulator -= self._fixed_dt
            steps += 1
        if steps >= max_steps:
            self._time_accumulator = 0.0

    def update(self, dt: float) -> PhysicsWorld:
        """
        Synchronize, step physics, and dispatch collision events.

        :param dt: Elapsed time in seconds to simulate.
        :return: This physics world.
        """
        self.sync_to_physics()
        self.step(dt)
        self.sync_from_physics()
        self._handle_event_queue()
        return self

    def query_point(self, point: vec2) -> list[pymunk.PointQueryInfo]:
        """
        Query shapes near a world point.

        :param point: World-space point to query.
        :return: Pymunk point query results.
        """
        return self._space.point_query((point.x, point.y), 1, pymunk.ShapeFilter())

    def query_segment(self, start: vec2, end: vec2, radius: float = 0) -> list[pymunk.SegmentQueryInfo]:
        """
        Query shapes intersecting a world-space segment.

        :param start: Segment start in world space.
        :param end: Segment end in world space.
        :param radius: Segment thickness.
        :return: Pymunk segment query results.
        """
        return self._space.segment_query(
            (start.x, start.y),
            (end.x, end.y),
            radius,
            pymunk.ShapeFilter(),
        )

    @staticmethod
    def get_shape_owner(shape: pymunk.Shape) -> Optional[PygameObject]:
        """
        Return the scene object that owns a pymunk shape.

        :param shape: Pymunk shape to inspect.
        :return: The owning scene object, or ``None`` when no owner is recorded.
        """
        return getattr(shape, "owner_ref", None)

    def __repr__(self) -> str:
        """Return a debug string representation."""
        return f"PhysicsWorld(bodies={len(self._bodies)})"
