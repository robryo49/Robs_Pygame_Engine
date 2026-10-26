"""Base interface for objects that draw and hit-test an owning game object."""

from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

from pyglm import glm

from ..utils import Transform, vec2, FRect

if TYPE_CHECKING:
    from ..objects import Layer


class ObjectRenderer:
    """Base class for renderers owned by an object.

    Renderers describe how an object is drawn and how it is hit-tested. They do not
    own the object's transform, layer, or sub-layer; those are supplied by the object
    when rendering.
    """

    def __init__(self, cache: bool = True) -> None:
        """Initialize the renderer and its bounding-radius cache state.

        :param cache: Whether draw commands may use the shared surface cache.
        """
        self._cache = cache
        self._cached_bounding_radius: float = 0.0
        self._bounding_radius_dirty: bool = True
        self._cached_dims: Optional[vec2] = None

    # region PROPERTIES
    @property
    def cache(self) -> bool:
        """Return whether draw commands produced by this renderer may use the surface cache."""
        return self._cache

    @property
    def dims(self) -> vec2:
        """Return the renderer's local dimensions.

        :return: The renderer's local dimensions.
        :raises NotImplementedError: Subclasses must implement this property.
        """
        raise NotImplementedError

    @property
    def width(self) -> float:
        """Return the renderer's local width.

        :return: The renderer's local width.
        :raises NotImplementedError: Subclasses must implement this property.
        """
        raise NotImplementedError

    @width.setter
    def width(self, value: int) -> None:
        """
        Set the renderer's local width; subclasses must implement this.

        :param value: The new local width.
        :raises NotImplementedError: Subclasses must implement this property.
        """
        raise NotImplementedError

    @property
    def height(self) -> float:
        """Return the renderer's local height.

        :return: The renderer's local height.
        :raises NotImplementedError: Subclasses must implement this property.
        """
        raise NotImplementedError

    @height.setter
    def height(self, value: int) -> None:
        """
        Set the renderer's local height; subclasses must implement this.

        :param value: The new local height.
        :raises NotImplementedError: Subclasses must implement this property.
        """
        raise NotImplementedError

    # endregion

    def get_aabb_size(self, rotation: float) -> vec2:
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the rendered shape.
        :return: The axis-aligned bounding box size in local units.
        """
        return vec2(glm.length(self.dims)) if rotation else self.dims

    def get_bounding_radius(self) -> float:
        """Return the radius of the smallest circle enclosing ``dims``.

        :return: The cached or recomputed bounding-circle radius.
        """
        dims = self.dims
        if self._bounding_radius_dirty or dims != self._cached_dims:
            self._cached_bounding_radius = glm.length(dims) * 0.5
            self._cached_dims = dims
            self._bounding_radius_dirty = False
        return self._cached_bounding_radius

    def _invalidate_bounding_radius(self) -> None:
        self._bounding_radius_dirty = True

    def render(self, submit: Callable[[Any], None], transform: Transform, layer: Layer, sub_layer: int,
               anchor: vec2, clip_area: Optional[FRect] = None) -> None:
        """Submit the draw command(s) for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the rendered content.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        :raises NotImplementedError: Always, because subclasses must implement rendering.
        """
        raise NotImplementedError

    def test_hit(self, local_pos: vec2) -> bool:
        """Return whether a local-space point lies inside the rendered shape.

        :param local_pos: Point to test in the renderer's local coordinate space.
        :return: ``True`` when the point hits the rendered shape.
        :raises NotImplementedError: Always, because subclasses must implement hit testing.
        """
        raise NotImplementedError

    def get_offset(self, anchor: vec2) -> vec2:
        """Return the local-space offset of an anchor in UV coordinates.

        :param anchor: UV anchor point to convert.
        :return: The anchor position in local pixels.
        """
        return self.uv_to_local(anchor)

    def uv_to_local(self, uv: vec2) -> vec2:
        """Convert UV coordinates in the range ``[0, 1]`` to local pixels.

        :param uv: UV coordinates to convert.
        :return: The corresponding local-space position.
        """
        return uv * self.dims

    def local_to_uv(self, local: vec2) -> vec2:
        """Convert local pixels to UV coordinates in the range ``[0, 1]``.

        :param local: Local-space position to convert.
        :return: The corresponding UV coordinates.
        """
        return local / self.dims

    def update(self, dt: float) -> None:
        """Advance any renderer-owned animation state.

        :param dt: Elapsed time in seconds since the previous update.
        """
        pass

