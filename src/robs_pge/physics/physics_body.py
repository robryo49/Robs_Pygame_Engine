from __future__ import annotations

import math
from typing import Optional, TYPE_CHECKING, cast

import pymunk

from ..utils import Anchor, vec2

if TYPE_CHECKING:
    from ..objects import PygameObject


class BodyTypes:
    DYNAMIC = pymunk.Body.DYNAMIC
    STATIC = pymunk.Body.STATIC
    KINEMATIC = pymunk.Body.KINEMATIC
    

class ShapeTypes:
    BOX = "box"
    CIRCLE = "circle"


class PhysicsBody:
    def __init__(
            self,
            obj: PygameObject,
            body_type: int = BodyTypes.DYNAMIC,
            mass: float = 1,
            moment: Optional[float] = None,
            friction: float = 0.5,
            elasticity: float = 0.0,
            sensor: bool = False,
            collision_layer: int = 1,
            collision_mask: int = 0xFFFFFFFF,
    ):
        self._owner = obj
        self._sensor = sensor
        self._collision_layer = collision_layer
        self._collision_mask = collision_mask

        self._body_type = body_type
        self._mass = mass
        self._moment = moment
        self._friction = friction
        self._elasticity = elasticity

        self._body: Optional[pymunk.Body] = None
        self._shapes: list[pymunk.Shape] = []
        self._world: Optional[pymunk.Space] = None

        self._shape_configs: list[tuple[str, dict]] = []
        self._constraints: list[pymunk.Constraint] = []

        self._anchor_offset = self._compute_anchor_offset()

    # region PROPERTIES

    @property
    def owner(self) -> PygameObject:
        return self._owner

    @property
    def body(self) -> Optional[pymunk.Body]:
        return self._body

    @property
    def shapes(self) -> list[pymunk.Shape]:
        return self._shapes

    @property
    def sensor(self) -> bool:
        return self._sensor

    @property
    def body_type(self) -> int:
        return self._body_type

    @property
    def is_dynamic(self) -> bool:
        return self._body is not None and self._body.body_type == pymunk.Body.DYNAMIC

    @property
    def constraints(self) -> list[pymunk.Constraint]:
        return self._constraints

    # endregion

    # region SHAPE DEFERRED CREATION

    def add_box_shape(self, size: Optional[tuple[float, float]] = None) -> "PhysicsBody":
        self._shape_configs.append((ShapeTypes.BOX, {"size": size}))
        return self

    def add_circle_shape(self, radius: Optional[float] = None) -> "PhysicsBody":
        self._shape_configs.append((ShapeTypes.CIRCLE, {"radius": radius}))
        return self

    def _create_deferred_shapes(self):
        for shape_type, kwargs in self._shape_configs:
            if shape_type == ShapeTypes.BOX:
                self._create_box_shape(kwargs.get("size"))
            elif shape_type == ShapeTypes.CIRCLE:
                self._create_circle_shape(kwargs.get("radius"))
        self._shape_configs.clear()

    # endregion

    # region SETUP

    def create_body(self, world: pymunk.Space):
        self._world = world
        self._anchor_offset = self._compute_anchor_offset()

        if self._body_type == BodyTypes.DYNAMIC:
            if self._moment is None:
                self._moment = pymunk.moment_for_box(self._mass, self._get_obj_size())
            self._body = pymunk.Body(self._mass, self._moment, body_type=BodyTypes.DYNAMIC)
        else:
            self._body = pymunk.Body(body_type=self._body_type)

        self._body.position = self._to_pymunk_pos(self._get_center_pos())
        self._body.angle = self._to_pymunk_angle(self._owner.world_transform.rotation)
        world.add(self._body)  # type: ignore

        self._create_deferred_shapes()

    @staticmethod
    def _get_default_size() -> tuple[float, float]:
        return 16.0, 16.0

    def _get_obj_size(self) -> tuple[float, float]:
        dims = self._owner.dims
        if dims.x > 0 and dims.y > 0:
            return dims.x, dims.y
        return self._get_default_size()

    def _apply_shape_properties(self, shape: pymunk.Shape):
        shape.friction = self._friction
        shape.elasticity = self._elasticity
        shape.sensor = self._sensor
        shape.filter = pymunk.ShapeFilter(categories=self._collision_layer, mask=self._collision_mask)
        shape.collision_type = 0
        shape.owner_ref = self._owner
        self._shapes.append(shape)
        self._world.add(shape)

    def _create_box_shape(self, size: Optional[tuple[float, float]] = None):
        if size is None:
            size = self._get_obj_size()

        shape = pymunk.Poly.create_box(self._body, size)
        self._apply_shape_properties(shape)

    def _create_circle_shape(self, radius: Optional[float] = None):
        if radius is None:
            radius = max(self._owner.dims.x, self._owner.dims.y) / 2

        shape = pymunk.Circle(self._body, radius)
        self._apply_shape_properties(shape)

    def remove(self):
        for constraint in list(self._constraints):
            constraint.remove()
        self._constraints.clear()

        for shape in self._shapes:
            if shape in self._world.shapes:
                self._world.remove(shape)
        self._shapes.clear()

        if self._body and self._body in self._world.bodies:
            self._world.remove(self._body)
        self._body = None
        self._world = None

    # endregion

    # region SYNC

    def sync_to_physics(self):
        if self._body is None:
            return

        self._body.position = self._to_pymunk_pos(self._get_center_pos())
        self._body.angle = self._to_pymunk_angle(self._owner.world_transform.rotation)

    def sync_from_physics(self):
        if self._body is None or not self.is_dynamic:
            return

        self._owner.set_world_position(self._from_pymunk_pos(self._body.position) - self._get_anchor_offset_world())
        self._owner.set_world_rotation(self._from_pymunk_angle(self._body.angle))

    # endregion

    # region FORCES

    def apply_force(self, force: vec2, point: Optional[vec2] = None) -> "PhysicsBody":
        if self._body and self.is_dynamic:
            p_point = self._to_pymunk_pos(point) if point else (0, 0)
            self._body.apply_force_at_local_point((force.x, force.y), p_point)
        return self

    def apply_impulse(self, impulse: vec2, point: Optional[vec2] = None) -> "PhysicsBody":
        if self._body and self.is_dynamic:
            p_point = self._to_pymunk_pos(point) if point else (0, 0)
            self._body.apply_impulse_at_local_point((impulse.x, impulse.y), p_point)
        return self

    def set_velocity(self, velocity: vec2) -> "PhysicsBody":
        if self._body and self.is_dynamic:
            self._body.velocity = (velocity.x, velocity.y)
        return self

    def set_angular_velocity(self, angular_velocity: float) -> "PhysicsBody":
        if self._body and self.is_dynamic:
            self._body.angular_velocity = angular_velocity
        return self

    # endregion

    # region COORDINATE CONVERSION

    @staticmethod
    def _to_pymunk_pos(pos: vec2) -> tuple[float, float]:
        return pos.x, pos.y

    @staticmethod
    def _from_pymunk_pos(pos) -> vec2:
        return vec2(pos.x, pos.y)

    @staticmethod
    def _to_pymunk_angle(angle_deg: float) -> float:
        return math.radians(-angle_deg)

    @staticmethod
    def _from_pymunk_angle(angle_rad: float) -> float:
        return math.degrees(-angle_rad)

    # endregion

    # region ANCHOR OFFSET

    def _compute_anchor_offset(self) -> vec2:
        center = self._owner.get_anchor_offset(Anchor.C)
        anchor = self._owner.get_anchor_offset(self._owner.anchor)
        return center - anchor

    def _get_anchor_offset_world(self) -> vec2:
        offset = self._anchor_offset
        angle = self._owner.world_transform.rotation
        rad = math.radians(-angle)
        c, s = math.cos(rad), math.sin(rad)
        return vec2(offset.x * c - offset.y * s, offset.x * s + offset.y * c)

    def _get_center_pos(self) -> vec2:
        return self._owner.world_transform.pos + self._get_anchor_offset_world()

    # endregion

    # endregion
    
    # region CONSTRAINTS
    
    def _get_target_body(self, other: Optional[PygameObject]) -> pymunk.Body:
        if self._world is None:
            raise RuntimeError(
                "Body must be added to a world before adding constraints. "
                "Ensure the object is added to a layer with physics enabled."
            )

        if other is None:
            return self._world.static_body

        if other.physics_body is None:
            raise ValueError("Other object has no physics body")

        return cast(pymunk.Body, cast(PhysicsBody, other.physics_body).body)
    
    def add_pin_joint(self, pos_a: vec2, pos_b: vec2, distance: Optional[float] = 0.0, other: Optional[PygameObject] = None) -> pymunk.PinJoint:
        body_b = self._get_target_body(other)
        anchor_a = (pos_a.x, pos_a.y)
        anchor_b = (pos_b.x, pos_b.y)
        
        constraint = pymunk.PinJoint(cast(pymunk.Body, self._body), body_b, anchor_a, anchor_b)
        if distance:
            constraint.distance = distance
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_slide_joint(self, pos_a: vec2, pos_b: vec2, min_v: Optional[float] = None, max_v: Optional[float] = None, other: Optional[PygameObject] = None) -> pymunk.SlideJoint:
        body_b = self._get_target_body(other)
        anchor_a = (pos_a.x, pos_a.y)
        anchor_b = (pos_b.x, pos_b.y)
        
        min_dist = min_v if min_v is not None else 0.0
        max_dist = max_v if max_v is not None else self._body.position.get_distance(body_b.position)
        
        constraint = pymunk.SlideJoint(cast(pymunk.Body, self._body), body_b, anchor_a, anchor_b, min_dist, max_dist)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_pivot_joint(self, pos_a: vec2, pos_b: vec2, other: Optional[PygameObject] = None) -> pymunk.PivotJoint:
        body_b = self._get_target_body(other)
        anchor_a = (pos_a.x, pos_a.y)
        anchor_b = (pos_b.x, pos_b.y)
        
        constraint = pymunk.PivotJoint(cast(pymunk.Body, self._body), body_b, anchor_a, anchor_b)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_groove_joint(self, groove_a: vec2, groove_b: vec2, pos_b: vec2, other: Optional[PygameObject] = None, ) -> pymunk.GrooveJoint:
        body_b = self._get_target_body(other)
        anchor_b = (pos_b.x, pos_b.y)
        groove_a = groove_a.to_tuple()
        groove_b = groove_b.to_tuple()
        
        constraint = pymunk.GrooveJoint(cast(pymunk.Body, self._body), body_b, groove_a, groove_b, anchor_b)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_damped_spring(self, pos_a: vec2, pos_b: vec2, rest_length: Optional[float] = None, stiffness: float = 0.0, damping: float = 0.0, other: Optional[PygameObject] = None) -> pymunk.DampedSpring:
        body_b = self._get_target_body(other)
        anchor_a = (pos_a.x, pos_a.y)
        anchor_b = (pos_b.x, pos_b.y)
        
        rest_length = rest_length if rest_length is not None else self._body.position.get_distance(body_b.position)
        
        constraint = pymunk.DampedSpring(cast(pymunk.Body, self._body), body_b, anchor_a, anchor_b, rest_length, stiffness, damping)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_damped_rotary_spring(self, rest_angle: float = 0.0, stiffness: float = 0.0, damping: float = 0.0, other: Optional[PygameObject] = None) -> pymunk.DampedRotarySpring:
        body_b = self._get_target_body(other)
        
        constraint = pymunk.DampedRotarySpring(cast(pymunk.Body, self._body), body_b, rest_angle, stiffness, damping)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_rotary_limit_joint(self, min_limit: float = 0.0, max_limit: float = 0.0, other: Optional[PygameObject] = None) -> pymunk.RotaryLimitJoint:
        body_b = self._get_target_body(other)
        
        constraint = pymunk.RotaryLimitJoint(cast(pymunk.Body, self._body), body_b, min_limit, max_limit)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_ratchet_joint(self, phase: float = 0.0, ratchet: float = 0.0, other: Optional[PygameObject] = None) -> pymunk.RatchetJoint:
        body_b = self._get_target_body(other)
        
        constraint = pymunk.RatchetJoint(cast(pymunk.Body, self._body), body_b, phase, ratchet)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_gear_joint(self, phase: float = 0.0, ratio: float = 0.0, other: Optional[PygameObject] = None) -> pymunk.GearJoint:
        body_b = self._get_target_body(other)
        
        constraint = pymunk.GearJoint(cast(pymunk.Body, self._body), body_b, phase, ratio)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def add_simple_motor(self, rate: float = 0.0, other: Optional[PygameObject] = None) -> pymunk.SimpleMotor:
        body_b = self._get_target_body(other)
    
        constraint = pymunk.SimpleMotor(cast(pymunk.Body, self._body), body_b, rate)
        
        self._constraints.append(constraint)
        self._world.add(constraint) # type: ignore
        return constraint
    
    def remove_constraint(self, constraint: pymunk.Constraint):
        if constraint in self._constraints:
            if self._world is not None and constraint in self._world.constraints:
                self._world.remove(constraint)
            self._constraints.remove(constraint)
    
    # endregion
