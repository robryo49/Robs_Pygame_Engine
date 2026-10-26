"""Provides a fullscreen display surface with logical viewport scaling."""

import pygame as pg
from pyglm.glm import vec2

from ..utils import Color, Colors, ScreenAnchor


class Display:
    """Manage the fullscreen surface, logical viewport, and clear color."""

    def __init__(self, dims: vec2, vsync: bool = True, clear_color: Color = Colors.DARK_NAVY) -> None:
        """Create a fullscreen display and configure its logical viewport.

        :param dims: Logical viewport dimensions in world units.
        :param vsync: Whether to enable vertical synchronization.
        :param clear_color: Color used when clearing the display.
        """
        
        self._screen_dims: vec2 = vec2(pg.display.get_desktop_sizes()[0])
        self._viewport_dims: vec2 = vec2(dims)
        
        self._s2v_ratios: vec2 = self.viewport_dims / self.screen_dims
        self._v2s_ratios: vec2 = self.screen_dims / self.viewport_dims
        
        self._surface: pg.Surface = pg.display.set_mode(self._screen_dims, (pg.SRCALPHA | pg.FULLSCREEN), vsync=vsync)
        ScreenAnchor.set_screen_dims(self._viewport_dims)
        
        self._clear_color: Color = clear_color
        
    # region PROPERTIES
    
    @property
    def surface(self) -> pg.Surface:
        """Return the pygame surface used for rendering."""
        return self._surface
    
    # region dims
    
    @property
    def screen_dims(self) -> vec2:
        """Return the physical screen dimensions."""
        return self._screen_dims
    
    @property
    def screen_width(self) -> float:
        """Return the physical screen width in pixels."""
        return self.screen_dims.x
    
    @property
    def screen_height(self) -> float:
        """Return the physical screen height in pixels."""
        return self.screen_dims.y
    
    
    @property
    def screen_center_x(self) -> float:
        """Return the horizontal center of the physical screen."""
        return self.screen_width * 0.5
    
    @property
    def screen_center_y(self) -> float:
        """Return the vertical center of the physical screen."""
        return self.screen_height * 0.5
    
    @property
    def screen_center(self) -> vec2:
        """Return the physical screen center as a vector."""
        return self.screen_dims * 0.5
    
    
    
    @property
    def viewport_dims(self) -> vec2:
        """Return the logical viewport dimensions."""
        return self._viewport_dims
    
    @property
    def viewport_width(self) -> float:
        """Return the logical viewport width."""
        return self.viewport_dims.x
    
    @property
    def viewport_height(self) -> float:
        """Return the logical viewport height."""
        return self.viewport_dims.y
    
    @property
    def viewport_center_x(self) -> float:
        """Return the horizontal center of the logical viewport."""
        return self.viewport_width * 0.5
    
    @property
    def viewport_center_y(self) -> float:
        """Return the vertical center of the logical viewport."""
        return self.viewport_height * 0.5
    
    @property
    def viewport_center(self) -> vec2:
        """Return the logical viewport center as a vector."""
        return self.viewport_dims * 0.5
    
    # endregion
    
    @property
    def clear_color(self) -> Color:
        """Return the color used when clearing the display."""
        return self._clear_color

    @clear_color.setter
    def clear_color(self, value: Color):
        """
        Set the color used when clearing the display.

        :param value: The new value.
        """
        self._clear_color = value

    
    # endregion
    
    # region Coordinate Conversion Methods
    
    def screen_to_viewport_pos(self, screen_pos: vec2) -> vec2:
        """Convert a screen-space position to viewport space.

        :param screen_pos: Screen-space position.
        :return: Position in viewport coordinates.
        """
        return screen_pos * self._s2v_ratios
    def screen_to_viewport_vec(self, screen_vec: vec2) -> vec2:
        """Convert a screen-space vector to viewport space.

        :param screen_vec: Screen-space vector.
        :return: Vector in viewport coordinates.
        """
        return screen_vec * self._s2v_ratios
    
    def viewport_to_screen_pos(self, viewport_pos: vec2) -> vec2:
        """Convert a viewport-space position to screen space.

        :param viewport_pos: Position in viewport coordinates.
        :return: Screen-space position.
        """
        return viewport_pos * self._v2s_ratios
    def viewport_to_screen_vec(self, viewport_vec: vec2) -> vec2:
        """Convert a viewport-space vector to screen space.

        :param viewport_vec: Vector in viewport coordinates.
        :return: Screen-space vector.
        """
        return viewport_vec * self._v2s_ratios
    
    # endregion
    
    def clear(self) -> "Display":
        """Fill the display surface with the current clear color.

        :return: This display for chaining.
        """
        self.surface.fill(self.clear_color)
        return self
    
    def update(self, dt: float) -> "Display":
        """Present the rendered surface on the screen.

        :param dt: Elapsed time in seconds.
        :return: This display for chaining.
        """
        pg.display.flip()
        return self
    