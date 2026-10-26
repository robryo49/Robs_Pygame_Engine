"""Dataclass style definitions used by renderers and UI widgets."""

from dataclasses import dataclass, field
from typing import Optional

from .surface_builders import RectBuilder
from ..utils import Anchor, Color, Colors, Font, Style, StyleOrName, vec2


# region PRIMITIVES


@dataclass
class ShapeStyle(Style):
    """Base style for filled shapes with an optional border."""

    bg_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    bd: int = 0
    bd_color: Color = field(default_factory=lambda: Color(0, 0, 0))
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the fill and border colors.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_color = Colors.with_alpha(self.bg_color, alpha),
            bd_color = Colors.with_alpha(self.bd_color, alpha)
        )


@dataclass
class RectStyle(ShapeStyle):
    """Style for rectangles, including corner radius and surface builder."""

    bd_radius: int | tuple[int, int, int, int] = 0
    builder: RectBuilder = field(default_factory=RectBuilder)

    def inset_bd_radius(self, border: Optional[int] = None) -> int | tuple[int, int, int, int]:
        """Return the corner radius inset by ``border`` (defaults to ``bd``), clamped at zero.

        :param border: Border width to subtract, or the style's border width when omitted.
        :return: The inset radius or per-corner radii.
        """
        inset = self.bd if border is None else border
        if isinstance(self.bd_radius, tuple):
            return tuple(max(0, radius - inset) for radius in self.bd_radius)  # type: ignore[return-value]
        return max(0, self.bd_radius - inset)


@dataclass
class CircleStyle(ShapeStyle):
    """Style for circles with a fill color and optional border."""
    pass


@dataclass
class PolygonStyle(ShapeStyle):
    """Style for polygons with a fill color and optional border."""
    pass


@dataclass
class LineStyle(Style):
    """Style for polylines with a color and stroke width."""

    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    width: int = 1
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the line color.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with the adjusted color.
        """
        return self.with_(
            color = Colors.with_alpha(self.color, alpha),
        )

# endregion


@dataclass
class ButtonStyle(Style):
    """Style for text buttons, including margins, font, and interaction feedback."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 20
    font: StyleOrName[Font] = field(default_factory=Font)
    hovered_scale: float = 1.1
    clicked_scale: float = 0.9
    hovered_color: Optional[Color] = None
    clicked_color: Optional[Color] = None
    hovered_text_color: Optional[Color] = None
    clicked_text_color: Optional[Color] = None
    transition_duration: float = 0.1
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background style.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with the adjusted background.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class SpriteButtonStyle(Style):
    """Style for sprite buttons, including margins and interaction feedback."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10
    hovered_scale: float = 1.1
    clicked_scale: float = 0.9
    hovered_color: Optional[Color] = None
    clicked_color: Optional[Color] = None
    transition_duration: float = 0.1
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background style.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with the adjusted background.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
        )


@dataclass
class IconButtonStyle(Style):
    """Style for icon buttons, combining a sprite button style and icon color."""

    button_style: SpriteButtonStyle = field(default_factory=SpriteButtonStyle)
    icon_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the button style and icon color.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            button_style = self.button_style.with_alpha(alpha),
            icon_color = Colors.with_alpha(self.icon_color, alpha),
        )

@dataclass
class RadioButtonStyle(Style):
    """Style for radio buttons with a circular background and icon color."""

    bg_style: CircleStyle = field(default_factory=CircleStyle)
    icon_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    margin: int = 0
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and icon colors.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            icon_color = Colors.with_alpha(self.icon_color, alpha),
        )


@dataclass
class ToggleButtonStyle(Style):
    """Style for toggle buttons, including the toggle knob and its color."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    toggle_style: RectStyle = field(default_factory=RectStyle)
    toggle_bg_color: Color = field(default_factory=lambda: Color(0, 0, 0))
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and toggle colors.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            toggle_bg_color = Colors.with_alpha(self.toggle_bg_color, alpha),
        )

@dataclass
class ProgressBarStyle(Style):
    """Style for progress bars with a background style and fill color."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    color: Color = field(default_factory=lambda: Color(255, 255, 255))
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and fill colors.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            color = Colors.with_alpha(self.color, alpha),
        )


@dataclass
class LineChartStyle(Style):
    """Style for line charts with a background and line color and width."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    line_color: Color = field(default_factory=lambda: Color(255, 255, 255))
    line_width: int = 1
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and line colors.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            line_color = Colors.with_alpha(self.line_color, alpha),
        )


@dataclass
class SliderStyle(Style):
    """Style for sliders, including bar, handle, font, and text options."""

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
        """Return a copy with alpha applied to the background, bar, and handle styles.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            bar_style = self.bar_style.with_alpha(alpha),
            handle_style = self.handle_style.with_alpha(alpha),
        )


@dataclass
class ScrollbarStyle(Style):
    """Style for scrollbars with background and handle styles and a margin."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    handle_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 10
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and handle styles.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            handle_style = self.handle_style.with_alpha(alpha),
        )


@dataclass
class ValueSelectorStyle(Style):
    """Style for value selectors with background, buttons, font, and value width."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    button_style: ButtonStyle = field(default_factory=ButtonStyle)
    font: StyleOrName[Font] = field(default_factory=Font)
    margin: int = 8
    value_width: Optional[int] = None
    hide_bg: bool = False
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and button styles.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            button_style = self.button_style.with_alpha(alpha),
        )


@dataclass
class ValueCyclerStyle(Style):
    """Style for value cyclers with background, icon buttons, font, and icon size."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    icon_button_style: IconButtonStyle = field(default_factory=IconButtonStyle)
    font: StyleOrName[Font] = field(default_factory=Font)
    margin: int = 8
    value_width: Optional[int] = None
    icon_size: int = 16
    hide_bg: bool = False
    
    def with_alpha(self, alpha: int):
        """Return a copy with alpha applied to the background and icon button styles.

        :param alpha: Alpha value to apply, typically in the range ``[0, 255]``.
        :return: A new style instance with adjusted colors.
        """
        return self.with_(
            bg_style = self.bg_style.with_alpha(alpha),
            icon_button_style = self.icon_button_style.with_alpha(alpha),
        )


@dataclass
class DebugPanelStyle(Style):
    """Style for the debug panel's header, title panel, and body panel."""

    header_style: RectStyle
    title_panel_style: RectStyle
    panel_style: RectStyle
    title_font:StyleOrName [Font]


@dataclass
class WindowStyle(Style):
    """Style for windows, including header, title, and scrollbar options."""

    bg_style: RectStyle = field(default_factory=RectStyle)
    margin: int = 0
    
    show_header: bool = False
    header_style: Optional[RectStyle] = field(default_factory=RectStyle)
    header_height: int = 20
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
        """Return a copy with scrollbar settings overridden by the provided values.

        :param scrollbar_style: Scrollbar style to use, or the current style when omitted.
        :param width: Scrollbar width in pixels, or the current width when omitted.
        :param edge_margin: Scrollbar edge margin in pixels, or the current margin when omitted.
        :return: A new style instance with the resolved scrollbar settings.
        """
        return self.with_(
            scrollbar_style=scrollbar_style if scrollbar_style is not None else self.scrollbar_style,
            scrollbar_width=width if width is not None else self.scrollbar_width,
            scrollbar_edge_margin=edge_margin if edge_margin is not None else self.scrollbar_edge_margin,
        )
    
    def with_icons(self, icon_buttons_style: Optional[IconButtonStyle] = None):
        """Return a copy that shows header buttons using the given icon style.

        :param icon_buttons_style: Icon button style to use, or the current style when omitted.
        :return: A new style instance with header buttons enabled.
        """
        return self.with_(
            show_header_buttons=True,
            icon_buttons_style=icon_buttons_style if icon_buttons_style is not None else self.icon_buttons_style,
        )
    
    def with_title(self, title_panel_style: Optional[RectStyle] = None, title_font: Optional[StyleOrName[Font]] = None, title_in_header: Optional[bool] = None):
        """Return a copy that shows a title using the provided panel and font settings.

        :param title_panel_style: Title panel style, or the current style when omitted.
        :param title_font: Title font, or the current font when omitted.
        :param title_in_header: Whether to place the title in the header, or the current value when omitted.
        :return: A new style instance with title rendering enabled.
        """
        return self.with_(
            show_title = True,
            title_panel_style = title_panel_style if title_panel_style is not None else self.title_panel_style,
            title_font = title_font if title_font is not None else self.title_font,
            title_in_header = title_in_header if title_in_header is not None else self.title_in_header
        )