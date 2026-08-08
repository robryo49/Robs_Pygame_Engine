from dataclasses import dataclass, field, replace
from typing import Optional

from ..utils import Color, Font, vec2, Colors, Anchor, StyleOrName


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
        bg_color
        bd
        bd_color
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
        bg_color
        bd
        bd_color
        bd_radius
    """
    bd_radius: int | tuple[int, int, int, int] = 0


@dataclass
class CircleStyle(ShapeStyle):
    """
    Attributes:
        bg_color
        bd
        bd_color
    """
    pass


@dataclass
class PolygonStyle(ShapeStyle):
    """
    Attributes:
        bg_color
        bd
        bd_color
    """
    pass


@dataclass
class LineStyle(Style):
    """
    Attributes:
        color
        width
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
        bg_style
        margin
        font
        hovered_scale
        clicked_scale
        hovered_color
        clicked_color
        hovered_text_color
        clicked_text_color
        transition_duration
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 50
    font: StyleOrName[Font] = field(default_factory=Font)
    hovered_scale: float = 1.1
    clicked_scale: float = 0.9
    hovered_color: Optional[Color] = None
    clicked_color: Optional[Color] = None
    hovered_text_color: Optional[Color] = None
    clicked_text_color: Optional[Color] = None
    transition_duration: float = 0.1
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class SpriteButtonStyle(Style):
    """
    Attributes:
        bg_style
        margin
        hovered_scale
        clicked_scale
        hovered_color
        clicked_color
        transition_duration
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10
    hovered_scale: float = 1.1
    clicked_scale: float = 0.9
    hovered_color: Optional[Color] = None
    clicked_color: Optional[Color] = None
    transition_duration: float = 0.1
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class IconButtonStyle(Style):
    """
    Attributes:
        button_style
        icon_color
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
        bg_style
        icon_color
        margin
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
        bg_style
        toggle_style
        toggle_bg_color
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
        bg_style
        color
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
        bg_style
        line_color
        line_width
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
        bg_style
        bar_style
        bar_width
        handle_style
        handle_size
        font
        text_position
        hide_bg
        hide_text
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    bar_style: RectStyle = field(default_factory=RectStyle)
    bar_width: int = 10
    handle_style: RectStyle | CircleStyle = field(default_factory=CircleStyle)
    handle_size: int | vec2 = 10
    font:StyleOrName [Font] = field(default_factory=Font)
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
class ScrollbarStyle(Style):
    """
    Attributes:
        bg_style
        handle_style
        margin
    """
    bg_style: RectStyle = field(default_factory=RectStyle)
    handle_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10
    
    def with_alpha(self, alpha: int):
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            handle_style = self.handle_style.with_alpha(alpha),
        )


@dataclass
class DebugPanelStyle(Style):
    """
    Attributes:
        header_style
        title_panel_style
        panel_style
        title_font
    """
    header_style: RectStyle
    title_panel_style: RectStyle
    panel_style: RectStyle
    title_font:StyleOrName [Font]


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
        scrollbar_style
        scrollbar_width
        scrollbar_edge_margin
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
    title_align: vec2 = field(default_factory=lambda: Anchor.C)
    title_in_header: bool = False
    
    scrollbar_style: Optional[ScrollbarStyle] = field(default_factory=ScrollbarStyle)
    scrollbar_width: int = 14
    scrollbar_edge_margin: int = 4
    
    def with_scrollbar(self, scrollbar_style: Optional[ScrollbarStyle] = None, width: Optional[int] = None, edge_margin: Optional[int] = None):
        return self.with_(
            scrollbar_style=scrollbar_style if scrollbar_style is not None else self.scrollbar_style,
            scrollbar_width=width if width is not None else self.scrollbar_width,
            scrollbar_edge_margin=edge_margin if edge_margin is not None else self.scrollbar_edge_margin,
        )
    
    def with_icons(self, icon_buttons_style: Optional[IconButtonStyle]):
        return self.with_(show_icons = True, icon_buttons_style = icon_buttons_style if icon_buttons_style is not None else self.icon_buttons_style)
    
    def with_title(self, title_panel_style: Optional[RectStyle] = None, title_font: Optional[StyleOrName[Font]] = None, title_in_header: Optional[bool] = None):
        return self.with_(
            show_title = True,
            title_panel_style = title_panel_style if title_panel_style is not None else self.title_panel_style,
            title_font = title_font if title_font is not None else self.title_font,
            title_in_header = title_in_header if title_in_header is not None else self.title_in_header
        )