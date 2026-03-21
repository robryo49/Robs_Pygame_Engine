from pygame import Color


class Colors:
    WHITE           = Color(255, 255, 255)
    LIGHT_GRAY      = Color(211, 211, 211)
    SILVER          = Color(192, 192, 192)
    GRAY            = Color(128, 128, 128)
    DARK_GRAY       = Color(64, 64, 64)
    CHARCOAL        = Color(54, 69, 79)
    BLACK           = Color(0, 0, 0)
    
    LIGHT_RED       = Color(255, 80, 80)
    RED             = Color(255, 0, 0)
    CRIMSON         = Color(220, 20, 60)
    DARK_RED        = Color(139, 0, 0)
    MAROON          = Color(128, 0, 0)
    
    PEACH           = Color(255, 218, 185)
    ORANGE          = Color(255, 165, 0)
    DARK_ORANGE     = Color(255, 140, 0)
    BURNT_ORANGE    = Color(204, 85, 0)
    BROWN           = Color(139, 69, 19)
    
    LIGHT_YELLOW    = Color(255, 255, 153)
    YELLOW          = Color(255, 255, 0)
    GOLD            = Color(255, 215, 0)
    DARK_YELLOW     = Color(204, 204, 0)
    OLIVE           = Color(128, 128, 0)
    AMBER           = Color(255, 200, 60)
    
    MINT            = Color(152, 255, 152)
    LIGHT_GREEN     = Color(144, 238, 144)
    GREEN           = Color(0, 128, 0)
    DARK_GREEN      = Color(0, 100, 0)
    FOREST_GREEN    = Color(34, 139, 34)
    
    LIGHT_TEAL      = Color(128, 222, 213)
    TEAL            = Color(0, 128, 128)
    DARK_TEAL       = Color(0, 100, 100)
    CYAN            = Color(0, 255, 255)
    TURQUOISE       = Color(64, 224, 208)
    CARIBBEAN_GREEN = Color(0, 220, 170)
    
    LIGHT_BLUE      = Color(173, 216, 230)
    SKY_BLUE        = Color(135, 206, 235)
    BLUE            = Color(0, 0, 255)
    ROYAL_BLUE      = Color(65, 105, 225)
    DARK_BLUE       = Color(0, 0, 139)
    NAVY            = Color(0, 0, 128)
    DARK_NAVY       = Color(20, 28, 45)
    MIDNIGHT        = Color(16, 22, 35)
    SLATE_BLUE      = Color(87, 101, 126)
    BRIGHT_BLUE     = Color(80, 160, 255)
    
    LAVENDER        = Color(230, 230, 250)
    LIGHT_PURPLE    = Color(200, 162, 200)
    PURPLE          = Color(128, 0, 128)
    VIOLET          = Color(138, 43, 226)
    INDIGO          = Color(75, 0, 130)
    
    LIGHT_PINK      = Color(255, 182, 193)
    PINK            = Color(255, 105, 180)
    HOT_PINK        = Color(255, 20, 147)
    DEEP_PINK       = Color(199, 21, 133)
    ROSE            = Color(255, 0, 127)
    
    BEIGE           = Color(245, 245, 220)
    TAN             = Color(210, 180, 140)
    SIENNA          = Color(160, 82, 45)
    CHOCOLATE       = Color(210, 105, 30)
    DARK_BROWN      = Color(101, 67, 33)
    
    TRANSPARENT     = Color(0, 0, 0, 0)
    
    ALL: dict[str, Color] = {
        name.lower(): value
        for name, value in vars().items()
        if isinstance(value, Color)
    }
    
    @staticmethod
    def grey(value: int, alpha: int = 255) -> Color:
        return Color(value, value, value, alpha)
    
    @staticmethod
    def lighten(color: Color, amount: int) -> Color:
        if amount < 0:
            return Colors.darken(color, -amount)
        return Color(
            min(color.r + amount, 255),
            min(color.g + amount, 255),
            min(color.b + amount, 255),
            color.a
        )
    
    @staticmethod
    def darken(color: Color, amount: int) -> Color:
        if amount < 0:
            return Colors.lighten(color, -amount)
        return Color(
            max(color.r - amount, 0),
            max(color.g - amount, 0),
            max(color.b - amount, 0),
            color.a
        )
    
    @staticmethod
    def multiply(color: Color, factor: float) -> Color:
        return Color(
            min(int(color.r * factor), 255),
            min(int(color.g * factor), 255),
            min(int(color.b * factor), 255),
            color.a
        )
    
    @staticmethod
    def with_alpha(color: Color, alpha: int) -> Color:
        return Color(color.r, color.g, color.b, alpha)
    
    @staticmethod
    def transparent(color: Color, alpha: int) -> Color:
        return Colors.with_alpha(color, alpha)
    
    @staticmethod
    def grayscale(color: Color) -> Color:
        return color.grayscale()
    
    @staticmethod
    def blend(color1: Color, color2: Color, factor: float) -> Color:
        return Color(
            round(color1.r * factor + color2.r * (1 - factor)),
            round(color1.g * factor + color2.g * (1 - factor)),
            round(color1.b * factor + color2.b * (1 - factor)),
            round(color1.a * factor + color2.a * (1 - factor))
        )
    
    @staticmethod
    def pastel(color: Color, factor: float = 0.5) -> Color:
        return Color(
            int(color.r + (255 - color.r) * factor),
            int(color.g + (255 - color.g) * factor),
            int(color.b + (255 - color.b) * factor),
            color.a
        )


class ColorPalette:
    def __init__(
            self,
            colors: dict[str, Color] = None,
            shades: dict[str, int] = None,
            single_colors: dict[str, Color] = None
    ):
        self.primary_colors: dict[str, Color] = {}
        self.single_colors: dict[str, Color] = {}
        self.shades: dict[str, int] = {}
        self.shaded_colors: dict[str, Color] = {}
        self.all_colors: dict[str, Color] = {}
        
        if colors is not None:
            self.add_colors(colors)
        if shades is not None:
            self.add_shades(shades)
        if single_colors is not None:
            self.add_single_colors(single_colors)
    
    # region SINGLE COLORS
    
    def add_single_color(self, name: str, color: Color) -> "ColorPalette":
        self.single_colors[name] = color
        self.all_colors[name] = color
        return self
    
    def add_single_colors(self, colors: dict[str, Color]) -> "ColorPalette":
        for name, color in colors.items():
            self.add_single_color(name, color)
        return self
    
    # endregion
    
    # region PRIMARY COLORS
    
    def add_color(self, name: str, color: Color) -> "ColorPalette":
        self.primary_colors[name] = color
        self.all_colors[name] = color
        
        for shade_name, amount in self.shades.items():
            shaded_name = f"{shade_name}_{name}"
            shaded_color = Colors.lighten(color, amount)
            self.shaded_colors[shaded_name] = shaded_color
            self.all_colors[shaded_name] = shaded_color
        
        return self
    
    def add_colors(self, colors: dict[str, Color]) -> "ColorPalette":
        for name, color in colors.items():
            self.add_color(name, color)
        return self
    
    # endregion
    
    # region SHADES
    
    def add_shade(self, name: str, amount: int) -> "ColorPalette":
        for color_name, color in self.primary_colors.items():
            shaded_name = f"{name}_{color_name}"
            shaded_color = Colors.lighten(color, amount)
            self.shaded_colors[shaded_name] = shaded_color
            self.all_colors[shaded_name] = shaded_color
        
        self.shades[name] = amount
        return self
    
    def add_shades(self, shades: dict[str, int]) -> "ColorPalette":
        for name, amount in shades.items():
            self.add_shade(name, amount)
        return self
    
    # endregion
    
    def get(self, color_name: str) -> Color:
        if color_name not in self.all_colors:
            raise KeyError(f"Color '{color_name}' not found in palette")
        return self.all_colors[color_name]
    
    def __getattr__(self, name: str) -> Color:
        try:
            return self.get(name)
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no color '{name}'")