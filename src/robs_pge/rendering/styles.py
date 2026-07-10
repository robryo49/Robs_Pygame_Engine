from dataclasses import dataclass, field, replace

from ..utils import Color, Font


@dataclass
class Style:
    def with_(self, **kwargs):
        return replace(self, **kwargs)
    
    def copy(self):
        return replace(self)


@dataclass
class ShapeStyle(Style):
    bg_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    bd: int = 0
    bd_color: Color = field(default_factory=lambda: Color(0, 0, 0))
    
    def with_(self, **kwargs):
        return replace(self, **kwargs)
    
    def copy(self):
        return replace(self)

@dataclass
class RectStyle(ShapeStyle):
    bd_radius: int = 0
    
    def copy(self):
        return replace(self)


@dataclass
class CircleStyle(ShapeStyle):
    pass
    
    def copy(self):
        return replace(self)


@dataclass
class PolygonStyle(ShapeStyle):
    pass
    
    def copy(self):
        return replace(self)


@dataclass
class LineStyle(Style):
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    width: int = 1
    
    def copy(self):
        return replace(self)
    


@dataclass
class ButtonStyle(RectStyle):
    margin: int = 50
    font: Font = field(default_factory=lambda: Font())
    
    def copy(self):
        return replace(self)


@dataclass
class ProgressBarStyle(RectStyle):
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def copy(self):
        return replace(self)
    

@dataclass
class GraphStyle(RectStyle):
    line_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    line_width: int = 1
    
    def copy(self):
        return replace(self)
    

@dataclass
class SliderStyle(RectStyle):
    bar_style: RectStyle = field(default_factory=lambda: RectStyle())
    handle_style: RectStyle | CircleStyle = field(default_factory=lambda: CircleStyle())
    font: Font = field(default_factory=lambda: Font())
    text_position: str = "right"



@dataclass
class DebugPanelStyle:
    header_style: RectStyle
    title_panel_style: RectStyle
    panel_style: RectStyle
    title_font: Font
