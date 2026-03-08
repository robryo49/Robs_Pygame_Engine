from dataclasses import dataclass, field, replace

from ..utils import Color, Font


@dataclass
class Style:
    def with_(self, **kwargs):
        raise NotImplementedError()


@dataclass
class ShapeStyle:
    bg_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    bd: int = 0
    bd_color: Color = field(default_factory=lambda: Color(0, 0, 0))
    
    def with_(self, **kwargs):
        return replace(self, **kwargs)

@dataclass
class RectStyle(ShapeStyle):
    bd_radius: int = 0


@dataclass
class CircleStyle(ShapeStyle):
    pass


@dataclass
class PolygonStyle(ShapeStyle):
    pass


@dataclass
class LineStyle:
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_(self, **kwargs):
        return replace(self, **kwargs)
    


@dataclass
class ButtonStyle(RectStyle):
    margin: int = 10
    font: Font = field(default_factory=lambda: Font())


@dataclass
class ProgressBarStyle(RectStyle):
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
