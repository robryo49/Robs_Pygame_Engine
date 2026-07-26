from dataclasses import dataclass, field, replace
from typing import Optional

from ..utils import Color, Font, Vec2, Colors, Anchor


@dataclass
class Style:
    """
    Base class for all UI styles
    """
    def with_(self, **kwargs):
        return replace(self, **kwargs)  # type: ignore[arg-type]
    
    def copy(self):
        return replace(self)


# region PRIMITIVES


@dataclass
class ShapeStyle(Style):
    """
    Attributes:
        bg_color: background color of the shape
        bd: border width
        bd_color: color of the border
    """
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
    """
    Attributes:
        bg_color: background color of the shape
        bd: border width
        bd_color: color of the border
        bd_radius: radius for rounded corners
    """
    bd_radius: int | tuple[int, int, int, int] = 0


@dataclass
class CircleStyle(ShapeStyle):
    """
    Attributes:
        bg_color: background color of the shape
        bd: border width
        bd_color: color of the border
    """
    pass


@dataclass
class PolygonStyle(ShapeStyle):
    """
    Attributes:
        bg_color: background color of the shape
        bd: border width
        bd_color: color of the border
    """
    pass


@dataclass
class LineStyle(Style):
    """
    Attributes:
        color: color of the line
        width: thickness of the line
    """
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    width: int = 1
    
    def with_alpha(self, alpha: int):
        return self.with_(
            color = Colors.with_alpha(self.color, alpha),
        )

# endregion


@dataclass
class ButtonStyle(Style):
    """
    Attributes:
        bg_style: rect style for the background
        margin: padding around the text
        font: font style for the button text
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 50
    font: Font = field(default_factory=Font)
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class SpriteButtonStyle(Style):
    """
    Attributes:
        bg_style: rect style for the background
        margin: padding around the sprite/icon
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class IconButtonStyle(Style):
    """
    Attributes:
        button_style: base sprite button style
        icon_color: tint color for the icon
    """
    button_style: SpriteButtonStyle = field(default_factory=SpriteButtonStyle)
    icon_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_alpha(self, alpha: int):
        return self.with_(
            button_style = self.button_style.with_alpha(alpha),
            icon_color = Colors.with_alpha(self.icon_color, alpha),
        )

@dataclass
class RadioButtonStyle(Style):
    """
    Attributes:
        bg_style: circle style for the background
        icon_color: color of the active indicator
        margin: spacing around the radio button
    """
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
    """
    Attributes:
        bg_style: rect style for the toggle background track
        toggle_style: rect style for the movable toggle element
        toggle_bg_color: background color of the active toggle
    """
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
    """
    Attributes:
        bg_style: rect style for the progress track background
        color: color of the filled progress indicator
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            color = Colors.with_alpha(self.color, alpha),
        )


@dataclass
class LineChartStyle(Style):
    """
    Attributes:
        bg_style: rect style for the chart background area
        line_color: color of the plotted data line
        line_width: thickness of the plotted data line
    """
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
    """
    Attributes:
        bg_style: rect style for the overall slider area background
        bar_style: rect style for the slider track
        bar_width: thickness of the slider track
        handle_style: style for the draggable handle
        handle_size: dimensions of the handle
        font: font style for displaying the value
        text_position: placement of the value text
        hide_bg: toggles visibility of the overall background
        hide_text: toggles visibility of the value text
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    bar_style: RectStyle = field(default_factory=RectStyle)
    bar_width: int = 10
    handle_style: RectStyle | CircleStyle = field(default_factory=CircleStyle)
    handle_size: int | Vec2 = 10
    font: Font = field(default_factory=Font)
    text_position: str = "right"
    hide_bg: bool = False
    hide_text: bool = False
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            bar_style = self.bar_style.with_alpha(alpha),
            handle_style = self.handle_style.with_alpha(alpha),
        )


@dataclass
class DebugPanelStyle(Style):
    """
    Attributes:
        header_style: rect style for the top header
        title_panel_style: rect style containing the title text
        panel_style: rect style for the main panel content area
        title_font: font style for the header title
    """
    header_style: RectStyle
    title_panel_style: RectStyle
    panel_style: RectStyle
    title_font: Font


@dataclass
class WindowStyle(Style):
    """
    Attributes:
        bg_style
        margin
        show_header
        header_style
        header_height
        header_margin
        show_header_buttons
        icon_buttons_style
        show_title
        title_panel_style
        title_panel_height
        title_panel_margin
        title_font
        title_align
        title_in_header
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 0
    
    show_header: bool = False
    header_style: Optional[RectStyle] = field(default_factory=RectStyle)
    header_height: Optional[int] = None
    header_margin: int = 0
    
    show_header_buttons: bool = False
    icon_buttons_style: IconButtonStyle = field(default_factory=IconButtonStyle)
    
    show_title: bool = False
    title_panel_style: Optional[RectStyle] = field(default_factory=RectStyle)
    title_panel_height: Optional[int] = None
    title_panel_margin: int = 0
    
    title_font: Optional[Font] = field(default_factory=Font)
    title_align: Vec2 = field(default_factory=lambda: Anchor.C)
    title_in_header: bool = False
    
    def with_icons(self, icon_buttons_style: Optional[IconButtonStyle]):
        return self.with_(show_icons = True, icon_buttons_style = icon_buttons_style if icon_buttons_style is not None else self.icon_buttons_style)
    
    def with_title(self, title_panel_style: Optional[RectStyle] = None, title_font: Optional[Font] = None, title_in_header: Optional[bool] = None):
        return self.with_(
            show_title = True,
            title_panel_style = title_panel_style if title_panel_style is not None else self.title_panel_style,
            title_font = title_font if title_font is not None else self.title_font,
            title_in_header = title_in_header if title_in_header is not None else self.title_in_header
        )