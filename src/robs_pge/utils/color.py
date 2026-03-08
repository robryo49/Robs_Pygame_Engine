
from pygame import Color


class Colors:
    WHITE = Color(255,255,255)
    BLACK = Color(0,0,0)
    
    RED = Color(255,0,0)
    DARK_RED = Color(139,0,0)
    LIGHT_RED = Color(255,102,102)
    
    GREEN = Color(0,255,0)
    DARK_GREEN = Color(0,100,0)
    LIGHT_GREEN = Color(144,238,144)
    
    BLUE = Color(0,0,255)
    NAVY = Color(0,0,128)
    SKY_BLUE = Color(135,206,235)
    
    ORANGE = Color(255,165,0)
    PURPLE = Color(128,0,128)
    PINK = Color(255,192,203)
    BROWN = Color(165,42,42)
    
    GOLD = Color(255,215,0)
    SILVER = Color(192,192,192)
    
    GREY = Color(128,128,128)
    LIGHT_GREY = Color(192,192,192)
    DARK_GREY = Color(64,64,64)
    
    TRANSPARENT = Color(0, 0, 0, 0)
    
    @staticmethod
    def grey(value: int, alpha: int = 255):
        return Color(value, value, value, alpha)
    
    @staticmethod
    def lighten(color: Color, amount: int):
        return Color(
            min(color.r + amount, 255),
            min(color.g + amount, 255),
            min(color.b + amount, 255),
            color.a
        )

    @staticmethod
    def darken(color: Color, amount: int):
        return Color(
            max(color.r - amount, 0),
            max(color.g - amount, 0),
            max(color.b - amount, 0),
            color.a
        )
    
    @staticmethod
    def multiply(color: Color, factor: float):
        return Color(
            min(int(color.r * factor), 255),
            min(int(color.g * factor), 255),
            min(int(color.b * factor), 255),
            color.a
        )
    
    @staticmethod
    def transparent(color: Color, alpha: int):
        return Color(color.r, color.g, color.b, alpha)
    
    @staticmethod
    def grayscale(color: Color):
        return color.grayscale()
    
    
    @staticmethod
    def blend(color1: Color, color2: Color, factor: float):
        return Color(
            round(color1.r * factor + color2.r * (1 - factor)),
            round(color1.g * factor + color2.g * (1 - factor)),
            round(color1.b * factor + color2.b * (1 - factor)),
            round(color1.a * factor + color2.a * (1 - factor))
        )
    
    @staticmethod
    def with_alpha(color: Color, alpha: int):
        return Color(color.r, color.g, color.b, alpha)
    
    @staticmethod
    def pastel(color, amount=0.5):
        return Color(
            int(color.r + (255 - color.r) * amount),
            int(color.g + (255 - color.g) * amount),
            int(color.b + (255 - color.b) * amount),
            color.a
        )



class ColorPalette:
    def __init__(self, **colors: Color):
        self.primary_colors = colors
        
        self.shades = {}
        self.shaded_colors = {}
        
    def add_colors(self, **colors: Color):
        self.primary_colors.update(colors)
        
        for name, factor in self.shades.items():
            new_colors = {f"{name}_{color}": Colors.multiply(value, factor) for color, value in colors.items()}
            self.shaded_colors.update(new_colors)
            
        return self
        
        
    def add_shade(self, name: str, factor: float):
        new_colors = {f"{name}_{color}": Colors.multiply(value, factor) for color, value in self.primary_colors.items()}
        self.shaded_colors.update(new_colors)
        self.shades[name] = factor
        return self
    
    def get(self, color_name: str):
        if color_name in self.primary_colors:
            return self.primary_colors[color_name]
        return self.shaded_colors[color_name]
    
    def __getattr__(self, name):
        return self.get(name)
    