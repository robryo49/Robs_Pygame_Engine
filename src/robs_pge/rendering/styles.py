from dataclasses import dataclass, field, replace

from ..utils import Color, Font, Vec2, Colors

@dataclass
class Style:
    def with_(self, **kwargs):
        return replace(self, **kwargs)  # type: ignore[arg-type]
    
    def copy(self):
        return replace(self)
    

# region PRIMITIVES


@dataclass
class ShapeStyle(Style):
    bg_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    bd: int = 0
    bd_color: Color = field(default_factory=lambda: Color(0, 0, 0))
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_color = Colors.with_alpha(self.bg_color, alpha),
            bd_color = Colors.with_alpha(self.bd_color, alpha)
        )
        
        


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
    
    def with_alpha(self, alpha: int):
        return self.with_(
            color = Colors.with_alpha(self.color, alpha),
        )

# endregion


@dataclass
class ButtonStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 50
    font: Font = field(default_factory=Font)
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class SpriteButtonStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class IconButtonStyle(Style):
    button_style: SpriteButtonStyle = field(default_factory=SpriteButtonStyle)
    icon_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_alpha(self, alpha: int):
        return self.with_(
            button_style = self.button_style.with_alpha(alpha),
            icon_color = Colors.with_alpha(self.icon_color, alpha),
        )

@dataclass
class RadioButtonStyle(Style):
    bg_style: CircleStyle = field(default_factory=CircleStyle)
    icon_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    margin: int = 0
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            icon_color = Colors.with_alpha(self.icon_color, alpha),
        )


@dataclass
class ToggleButtonStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    toggle_style: RectStyle = field(default_factory=RectStyle)
    toggle_bg_color: Color = field(default_factory=lambda: Color(0, 0, 0))
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            toggle_bg_color = Colors.with_alpha(self.toggle_bg_color, alpha),
        )

@dataclass
class ProgressBarStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            color = Colors.with_alpha(self.color, alpha),
        )


@dataclass
class LineChartStyle(Style):
    bg_style: RectStyle = field(default_factory=RectStyle)
    line_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    line_width: int = 1
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            line_color = Colors.with_alpha(self.line_color, alpha),
        )


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
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            bar_style = self.bar_style.with_alpha(alpha),
            handle_style = self.handle_style.with_alpha(alpha),
        )


@dataclass
class DebugPanelStyle(Style):
    header_style: RectStyle
    title_panel_style: RectStyle
    panel_style: RectStyle
    title_font: Font

