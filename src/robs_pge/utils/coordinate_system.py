from __future__ import annotations

from .math import cos, sin, pi, radians

from pygame import Vector2 as Vec2


class CoordinateSystem:
    
    def __init__(self, horizontal_axis: Vec2 = Vec2(1, 0), vertical_axis: Vec2 = Vec2(0, 1), origin: Vec2 = Vec2()):
        self._x_axis = horizontal_axis
        self._y_axis = vertical_axis
        
        self._origin = origin
    
    # region PROPERTIES
    
    # region origin
    @property
    def origin(self):
        return self._origin
    
    @origin.setter
    def origin(self, value):
        self._origin = value
    # endregion
    
    # region axis1
    @property
    def x_axis(self):
        return self._x_axis
    
    @x_axis.setter
    def x_axis(self, value):
        self._x_axis = value
    # endregion
    
    # region axis2
    @property
    def y_axis(self):
        return self._y_axis
    
    @y_axis.setter
    def y_axis(self, value):
        self._y_axis = value
    # endregion
    
    # region x_axis_angle
    @property
    def x_axis_angle(self):
        return self._x_axis.angle
    
    @x_axis_angle.setter
    def x_axis_angle(self, angle: float):
        angle_rad = radians(angle)
        self._x_axis = self._x_axis.length() * Vec2(cos(angle_rad), sin(angle_rad))
    # endregion
    
    # region y_axis_angle
    @property
    def y_axis_angle(self):
        return self._y_axis.angle
    
    @y_axis_angle.setter
    def y_axis_angle(self, angle: float):
        angle_rad = radians(angle)
        self._y_axis = self._y_axis.length() * Vec2(cos(angle_rad), sin(angle_rad))
    # endregion
    
    # endregion
    
