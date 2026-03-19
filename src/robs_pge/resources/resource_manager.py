from pathlib import Path
from typing import Any

from ..resources import Texture
from ..utils import Vec2, DictCollection, Font
from ..utils.color import ColorPalette, Color


class ResourceManager:
    def __init__(self):
        self._folders = DictCollection()
        
        self._resources: dict[type, DictCollection] = {
            Texture: DictCollection()
        }
        
    # region PROPERTIES
    
    # endregion
    
    def set(self, resource_type: type, resource_name: str, resource: Any):
        if not isinstance(resource, resource_type):
            raise TypeError(f"Resource '{resource_name}' is not of type '{resource_type}' but of type '{type(resource)}'")
        
        if resource_type not in self._resources:
            self._resources[resource_type] = DictCollection()
        
        self._resources[resource_type].set(resource_name, resource)
    
    def get(self, ressource_type: type, name: str):
        return self._resources[ressource_type].get(name)
    
    def get_path(self, folder: str):
        try:
            return self._folders[folder]
        except KeyError:
            raise KeyError(f"Asset folder '{folder}' is not registered")
    
    def add_folder(self, name: str, path: Path):
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_dir():
            raise NotADirectoryError(path)
        
        self._folders.set(name, path)


    def load_texture(self, name: str, path: str, folder: str, dims: Vec2 = None, width: int = None, height: int = None):
        path = self.get_path(folder).joinpath(path)
        texture = Texture.from_path(path, dims, width, height)
        
        self.set_texture(name, texture)
        return texture
    
    def set_texture(self, name: str, texture: Texture):
        self.set(Texture, name, texture)
    
    def get_texture(self, name):
        return self.get(Texture, name)

    
    def create_color_palette(self, name, colors: dict[str, Color], shades: dict[str, float] = None, single_colors: dict[str, float] = None):
        palette = ColorPalette(colors, shades, single_colors)
        self.set_color_palette(name, palette)
        
    def set_color_palette(self, name, palette: ColorPalette):
        self.set(ColorPalette, name, palette)
        
    def get_color_palette(self, name):
        return self.get(ColorPalette, name)
    
    
    def create_font(self, name: str, font="dejavusansmono", size=24, color: Color = None, bold=False, italic=False, line_spacing=0):
        font = Font(font, size, color, italic, line_spacing)
        self.set_font(name, font)
    
    def set_font(self, name: str, font: Font):
        self.set(Font, name, font)
        
    def get_font(self, name):
        return self.get(Font, name)
