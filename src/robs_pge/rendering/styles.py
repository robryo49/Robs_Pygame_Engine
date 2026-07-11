from dataclasses import dataclass, field, replace

from ..utils import Color, Font, Vec2, Colors

@dataclass
class Style:
    def with_(self, **kwargs):
        return replace(self, **kwargs)
    
    def copy(self):
        return replace(self)
    

# region PRIMITIVES


@dataclass
class ShapeStyle(Style):
    bg_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    bd: int = 0
    bd_color: Color = field(default_factory=lambda: Color(0, 0, 0))


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
class LineStyle(Style):
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    width: int = 1


# endregion


@dataclass
class ButtonStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 50
    font: Font = field(default_factory=Font)


@dataclass
class SpriteButtonStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10


@dataclass
class IconButtonStyle(Style):
    button_style: SpriteButtonStyle = field(default_factory=SpriteButtonStyle)
    icon_color: Color = field(default_factory=lambda: Color(255, 255, 255))

@dataclass
class ToggleButtonStyle:
    bg_style: RectStyle = field(default_factory=RectStyle)
    toggle_style: RectStyle = field(default_factory=RectStyle)
    toggle_bg_color: Color = field(default_factory=lambda: Color(0, 0, 0))


@dataclass
class ProgressBarStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    color: Color = field(default_factory=lambda: Color(255, 255, 255))


@dataclass
class LineChartStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    line_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    line_width: int = 1


@dataclass
class SliderStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    bar_style: RectStyle = field(default_factory=RectStyle)
    bar_width: int = 10
    handle_style: RectStyle | CircleStyle = field(default_factory=CircleStyle)
    handle_size: int | Vec2 = 10
    font: Font = field(default_factory=Font)
    text_position: str = "right"
    hide_bg: bool = False


@dataclass
class DebugPanelStyle(Style):
    header_style: RectStyle
    title_panel_style: RectStyle
    panel_style: RectStyle
    title_font: Font

