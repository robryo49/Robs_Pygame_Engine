"""Provides a 2D camera with coordinate conversion and zoom controls."""

from typing import Optional

from pyglm import glm

from .display import Display
from ..utils import Transform, vec2


class Camera:
    """Represent a 2D camera with position, rotation, zoom, and coordinate conversions."""

    def __init__(self, display: Display) -> None:
        """Initialize the camera for a display viewport.

        :param display: Display whose viewport defines the camera projection.
        """
        
        self._display: Display = display
        
        self._display_dims: vec2 = display.viewport_dims
        self._display_center: vec2 = display.viewport_dims * 0.5
        
        self._transform: Transform = Transform()
        
        self._min_zoom: Optional[float] = None
        self._max_zoom: Optional[float] = None

        self._cached_bounding_radius: float = 0.0
        self._bounding_radius_dirty: bool = True

    # region PROPERTIES
    
    @property
    def display(self) -> Display:
        """Return the display that owns this camera."""
        return self._display
    
    @property
    def transform(self) -> Transform:
        """Return the underlying camera transform."""
        return self._transform
    
    # region dimensions
    
    @property
    def screen_dims(self):
        """Return the full screen dimensions."""
        return self.display.screen_dims
    
    @property
    def screen_width(self):
        """Return the screen width in pixels."""
        return self.display.screen_width
    
    @property
    def screen_height(self):
        """Return the screen height in pixels."""
        return self.display.screen_height
    
    @property
    def screen_center_x(self):
        """Return the horizontal center of the screen."""
        return self.display.screen_center_x
    
    @property
    def screen_center_y(self):
        """Return the vertical center of the screen."""
        return self.display.screen_center_y
    
    @property
    def screen_center(self):
        """Return the screen center as a vector."""
        return self.display.screen_center
    
    
    
    @property
    def viewport_dims(self):
        """Return the logical viewport dimensions."""
        return self.display.viewport_dims
    
    @property
    def viewport_width(self):
        """Return the logical viewport width."""
        return self.display.viewport_width
    
    @property
    def viewport_height(self):
        """Return the logical viewport height."""
        return self.display.viewport_height
    
    @property
    def viewport_center_x(self):
        """Return the horizontal center of the viewport."""
        return self.display.viewport_center_x
    
    @property
    def viewport_center_y(self):
        """Return the vertical center of the viewport."""
        return self.display.viewport_center_y
    
    @property
    def viewport_center(self):
        """Return the viewport center as a vector."""
        return self.display.viewport_center
    
    # endregion
    
    # region pos
    @property
    def pos(self) -> vec2:
        """Return the camera position in world units."""
        return self.transform.pos
    
    @pos.setter
    def pos(self, value: vec2) -> None:
        """
        Set the camera position in world units.

        :param value: The new camera position in world units.
        """
        self.transform.pos = value
        
    # region x_pos
    @property
    def x_pos(self):
        """Return the camera's x position in world units."""
        return self.transform.x_pos
    
    @x_pos.setter
    def x_pos(self, value):
        """
        Set the camera's x position in world units.

        :param value: The new camera's x position in world units.
        """
        self.transform.x_pos = value
    # endregion
    
    # region y_pos
    @property
    def y_pos(self):
        """Return the camera's y position in world units."""
        return self.transform.y_pos
    
    @y_pos.setter
    def y_pos(self, value):
        """
        Set the camera's y position in world units.

        :param value: The new camera's y position in world units.
        """
        self.transform.y_pos = value
    # endregion
        
    def move(self, translation: vec2) -> "Camera":
        """Translate the camera by the given offset.

        :param translation: World-space translation to apply.
        :return: This camera for chaining.
        """
        self.pos += translation
        return self
    
    def move_x(self, dx: float) -> "Camera":
        """Translate the camera horizontally.

        :param dx: World-space horizontal distance to add.
        :return: This camera for chaining.
        """
        self.x_pos += dx
        return self
    
    def move_y(self, dy: float) -> "Camera":
        """Translate the camera vertically.

        :param dy: World-space vertical distance to add.
        :return: This camera for chaining.
        """
        self.y_pos += dy
        return self
    # endregion
        
    # region rotation
    @property
    def rotation(self) -> float:
        """Return the camera rotation in degrees."""
        return self.transform.rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        """
        Set the camera rotation in degrees.

        :param value: The new camera rotation in degrees.
        """
        self.transform.rotation = value
        
    def rotate(self, value: float) -> "Camera":
        """Rotate the camera by a relative angle.

        :param value: Rotation delta in degrees.
        :return: This camera for chaining.
        """
        self.rotation += value
        return self
    # endregion
    
    # region zoom
    @property
    def zoom(self) -> float:
        """Return the current zoom factor."""
        return 1/self.transform.scale
    
    @zoom.setter
    def zoom(self, value: float | int) -> None:
        """Set the zoom factor, clamping it to the configured limits.

        :param value: Desired zoom factor, which must be greater than zero.
        :raises ValueError: If value is not greater than zero.
        """
        if value <= 0:
            raise ValueError("Camera zoom must be greater than zero")

        max_zoom = self.max_zoom
        min_zoom = self.min_zoom
        if max_zoom is not None and value > max_zoom:
            value = max_zoom
        if min_zoom is not None and value < min_zoom:
            value = min_zoom
        self.transform.scale = 1 / value
        self._invalidate_bounding_radius()
    
    def zoom_in(self, fact: float, point: Optional[vec2]=None) -> "Camera":
        """Increase the zoom factor, optionally keeping a world point fixed.

        :param fact: Multiplicative zoom-in factor.
        :param point: Optional world-space point to keep in place.
        :return: This camera for chaining.
        """
        prev = self.zoom
        self.zoom *= fact
        fact = prev / self.zoom
        if point is not None: self.pos = point - (point - self.pos) * fact
        return self
    
    def zoom_out(self, fact: float, point: Optional[vec2]=None) -> "Camera":
        """Decrease the zoom factor, optionally keeping a world point fixed.

        :param fact: Divisor applied to the current zoom factor.
        :param point: Optional world-space point to keep in place.
        :return: This camera for chaining.
        """
        prev = self.zoom
        self.zoom /= fact
        fact = prev / self.zoom
        if point is not None: self.pos = point - (point - self.pos) * fact
        return self
    # endregion
    
    # region min_zoom
    @property
    def min_zoom(self):
        """Return the minimum allowed zoom factor, if any."""
        return self._min_zoom
    
    @min_zoom.setter
    def min_zoom(self, value):
        """
        Set the minimum allowed zoom factor.

        :param value: The new minimum allowed zoom factor.
        """
        self._min_zoom = value
    # endregion
    
    # region max_zoom
    @property
    def max_zoom(self):
        """Return the maximum allowed zoom factor, if any."""
        return self._max_zoom
    
    @max_zoom.setter
    def max_zoom(self, value):
        """
        Set the maximum allowed zoom factor.

        :param value: The new maximum allowed zoom factor.
        """
        self._max_zoom = value
    # endregion
    
    @property
    def bounding_radius(self) -> float:
        """Return the cached world-space radius of the viewport's bounding circle."""
        if self._bounding_radius_dirty:
            self._cached_bounding_radius = glm.length(self.viewport_dims * self.transform.scale) * 0.5
            self._bounding_radius_dirty = False
        return self._cached_bounding_radius

    def _invalidate_bounding_radius(self):
        self._bounding_radius_dirty = True
        
    @property
    def bounding_radius_squared(self) -> float:
        """Return the squared world-space radius of the viewport's bounding circle."""
        return self.bounding_radius ** 2

    @property
    def up(self) -> vec2:
        """Return the camera's up direction in world space."""
        return self.transform.apply_on_vec(vec2(0, -1))
    
    @property
    def right(self) -> vec2:
        """Return the camera's right direction in world space."""
        return self.transform.apply_on_vec(vec2(1, 0))
    
    @property
    def down(self) -> vec2:
        """Return the camera's down direction in world space."""
        return self.transform.apply_on_vec(vec2(0, 1))
    
    @property
    def left(self) -> vec2:
        """Return the camera's left direction in world space."""
        return self.transform.apply_on_vec(vec2(-1, 0))
    
    # endregion
    
    # region COORDINATES CONVERSION METHODS
    
    # region From Screen
    def screen_to_viewport_pos(self, pos: vec2) -> vec2:
        """Convert a screen-space position to viewport space.

        :param pos: Screen-space position.
        :return: Position in viewport coordinates.
        """
        return self.display.screen_to_viewport_pos(pos)
    def screen_to_viewport_vec(self, vec: vec2) -> vec2:
        """Convert a screen-space vector to viewport space.

        :param vec: Screen-space vector.
        :return: Vector in viewport coordinates.
        """
        return self.display.screen_to_viewport_vec(vec)
    def screen_to_camera_pos(self, pos: vec2) -> vec2:
        """Convert a screen-space position to camera space.

        :param pos: Screen-space position.
        :return: Position in camera coordinates.
        """
        return self.viewport_to_camera_pos(self.screen_to_viewport_pos(pos))
    def screen_to_camera_vec(self, vec: vec2) -> vec2:
        """Convert a screen-space vector to camera space.

        :param vec: Screen-space vector.
        :return: Vector in camera coordinates.
        """
        return self.viewport_to_camera_vec(self.screen_to_viewport_vec(vec))
    def screen_to_world_pos(self, pos: vec2) -> vec2:
        """Convert a screen-space position to world space.

        :param pos: Screen-space position.
        :return: Position in world coordinates.
        """
        return self.viewport_to_world_pos(self.screen_to_viewport_pos(pos))
    def screen_to_world_vec(self, vec: vec2) -> vec2:
        """Convert a screen-space vector to world space.

        :param vec: Screen-space vector.
        :return: Vector in world coordinates.
        """
        return self.viewport_to_world_vec(self.screen_to_viewport_vec(vec))
    # endregion
    
    # region From Viewport
    def viewport_to_screen_pos(self, pos: vec2) -> vec2:
        """Convert a viewport-space position to screen space.

        :param pos: Position in viewport coordinates.
        :return: Screen-space position.
        """
        return self.display.viewport_to_screen_pos(pos)
    def viewport_to_screen_vec(self, vec: vec2) -> vec2:
        """Convert a viewport-space vector to screen space.

        :param vec: Vector in viewport coordinates.
        :return: Screen-space vector.
        """
        return self.display.viewport_to_screen_vec(vec)
    def viewport_to_camera_pos(self, pos: vec2) -> vec2:
        """Convert a viewport-space position to camera space.

        :param pos: Position in viewport coordinates.
        :return: Position in camera coordinates, offset by the viewport center.
        """
        return pos - self.viewport_center
    def viewport_to_camera_vec(self, vec: vec2) -> vec2:
        """Convert a viewport-space vector to camera space.

        :param vec: Vector in viewport coordinates.
        :return: The same vector in camera coordinates.
        """
        return vec
    def viewport_to_world_pos(self, pos: vec2) -> vec2:
        """Convert a viewport-space position to world space.

        :param pos: Position in viewport coordinates.
        :return: Position in world coordinates.
        """
        return self.camera_to_world_pos(self.viewport_to_camera_pos(pos))
    def viewport_to_world_vec(self, vec: vec2) -> vec2:
        """Convert a viewport-space vector to world space.

        :param vec: Vector in viewport coordinates.
        :return: Vector in world coordinates.
        """
        return self.camera_to_world_vec(self.viewport_to_camera_vec(vec))
    # endregion
    
    # region From Camera
    def camera_to_screen_pos(self, pos: vec2) -> vec2:
        """Convert a camera-space position to screen space.

        :param pos: Position in camera coordinates.
        :return: Screen-space position.
        """
        return self.display.viewport_to_screen_pos(self.camera_to_viewport_pos(pos))
    def camera_to_screen_vec(self, vec: vec2) -> vec2:
        """Convert a camera-space vector to screen space.

        :param vec: Vector in camera coordinates.
        :return: Screen-space vector.
        """
        return self.display.viewport_to_screen_vec(self.camera_to_viewport_vec(vec))
    def camera_to_viewport_pos(self, pos: vec2) -> vec2:
        """Convert a camera-space position to viewport space.

        :param pos: Position in camera coordinates.
        :return: Position in viewport coordinates, offset by the viewport center.
        """
        return pos + self.viewport_center
    def camera_to_viewport_vec(self, vec: vec2) -> vec2:
        """Convert a camera-space vector to viewport space.

        :param vec: Vector in camera coordinates.
        :return: The same vector in viewport coordinates.
        """
        return vec
    def camera_to_world_pos(self, pos: vec2) -> vec2:
        """Apply the camera transform to a camera-space position.

        :param pos: Position in camera coordinates.
        :return: Position in world coordinates.
        """
        return self.transform.apply_on_point(pos)
    def camera_to_world_vec(self, vec: vec2) -> vec2:
        """Apply the camera transform to a camera-space vector.

        :param vec: Vector in camera coordinates.
        :return: Vector in world coordinates.
        """
        return self.transform.apply_on_vec(vec)
    # endregion
    
    # region From World
    def world_to_screen_pos(self, pos: vec2) -> vec2:
        """Convert a world-space position to screen space.

        :param pos: Position in world coordinates.
        :return: Screen-space position.
        """
        return self.display.viewport_to_screen_pos(self.world_to_viewport_pos(pos))
    def world_to_screen_vec(self, vec: vec2) -> vec2:
        """Convert a world-space vector to screen space.

        :param vec: Vector in world coordinates.
        :return: Screen-space vector.
        """
        return self.display.viewport_to_screen_vec(self.world_to_viewport_vec(vec))
    def world_to_viewport_pos(self, pos: vec2) -> vec2:
        """Convert a world-space position to viewport space.

        :param pos: Position in world coordinates.
        :return: Position in viewport coordinates.
        """
        return self.camera_to_viewport_pos(self.world_to_camera_pos(pos))
    def world_to_viewport_vec(self, vec: vec2) -> vec2:
        """Convert a world-space vector to viewport space.

        :param vec: Vector in world coordinates.
        :return: Vector in viewport coordinates.
        """
        return self.camera_to_viewport_vec(self.world_to_camera_vec(vec))
    def world_to_camera_pos(self, pos: vec2) -> vec2:
        """Apply the inverse camera transform to a world-space position.

        :param pos: Position in world coordinates.
        :return: Position in camera coordinates.
        """
        return self.transform.apply_inverse_on_point(pos)
    def world_to_camera_vec(self, vec: vec2) -> vec2:
        """Apply the inverse camera transform to a world-space vector.

        :param vec: Vector in world coordinates.
        :return: Vector in camera coordinates.
        """
        return self.transform.apply_inverse_on_vec(vec)
    # endregion
    
    # endregion
    
    # endregion
    
    
    def update(self, dt: float) -> "Camera":
        """Advance the camera by one frame; this base implementation performs no work.

        :param dt: Elapsed time in seconds.
        :return: This camera for chaining.
        """
        return self
    
    def __repr__(self) -> str:
        """Return a debug string representation."""
        return "Camera"