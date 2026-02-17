from dataclasses import dataclass, field

from ..utils import Color, Font


@dataclass
class ShapeStyle:
    bg_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    border: int = 0
    bd_color: Color = field(default_factory=lambda: Color(0, 0, 0))


@dataclass
class RectStyle(ShapeStyle):
    bd_radius: int = 0


@dataclass
class CircleStyle(ShapeStyle):
    pass


@dataclass
class ButtonStyle(RectStyle):
    margin: int = 10
    font: Font = field(default_factory=lambda: Font())

