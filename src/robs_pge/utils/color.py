
from pygame import Color


class Colors:
    WHITE = Color(255,255,255)
    BLACK = Color(0,0,0)
    
    RED = Color(255,0,0)
    GREEN = Color(0,255,0)
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
    def lighten(color: Color, gamma_add: int):
        if gamma_add < 0:
            return Colors.darken(color, -gamma_add)
        return Color(
            min(color.r + gamma_add, 255),
            min(color.g + gamma_add, 255),
            min(color.b + gamma_add, 255),
            color.a
        )

    @staticmethod
    def darken(color: Color, gamma_add: int):
        if gamma_add < 0:
            return Colors.lighten(color, -gamma_add)
        return Color(
            max(color.r - gamma_add, 0),
            max(color.g - gamma_add, 0),
            max(color.b - gamma_add, 0),
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
    def pastel(color, gamma_add=0.5):
        return Color(
            int(color.r + (255 - color.r) * gamma_add),
            int(color.g + (255 - color.g) * gamma_add),
            int(color.b + (255 - color.b) * gamma_add),
            color.a
        )



class ColorPalette:
    def __init__(self, colors: dict[str, Color], shades: dict[str, int] = None, single_colors: dict[str, Color] = None):
        self.primary_colors = dict(colors)
        self.single_colors = {}
        
        self.shades = {}
        self.shaded_colors = {}
        
        self.all_colors = dict(colors)
        
        if shades is not None:
            self.add_shades(shades)
            
        if single_colors is not None:
            self.add_single_colors(single_colors)
            
        
    def add_single_color(self, name: str, color: Color):
        self.single_colors[name] = color
        self.all_colors[name] = color
        return self
    
    def add_single_colors(self, colors: dict[str, Color]):
        for name, color in colors.items():
            self.add_single_color(name, color)
        return self
        
        
    def add_color(self, name: str, color: Color):
        self.primary_colors[name] = color
        self.all_colors[name] = color
        
        for shade_name, gamma_add in self.shades.items():
            color_name, new_color = f"{shade_name}_{name}", Colors.lighten(color, gamma_add)
            self.shaded_colors[color_name] = new_color
            self.all_colors[color_name] = new_color
        return self
        
    def add_colors(self, colors: dict[str, Color]):
        for name, color in colors:
            self.add_color(name, color)
        return self
        
        
    def add_shade(self, name: str, gamma_add: int):
        new_colors = {f"{name}_{color}": Colors.lighten(value, gamma_add) for color, value in self.primary_colors.items()}
        
        self.shaded_colors.update(new_colors)
        self.all_colors.update(new_colors)
        
        self.shades[name] = gamma_add
        return self
    
    def add_shades(self, shades: dict[str, int]):
        for name, gamma_add in shades.items():
            self.add_shade(name, gamma_add)
        return self
    
    
    def get(self, color_name: str):
        return self.all_colors[color_name]
    
    def __getattr__(self, name):
        return self.get(name)
    