from pathlib import Path
from typing import Any

from ..resources import Texture
from ..utils import Vec2, DictCollection
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
        
        self.set(Texture, name, texture)
        return texture
    
    def get_texture(self, name):
        return self.get(Texture, name)
    
    def create_color_palette(self, name, colors: dict[str, Color], shades: list[tuple[str, float]] = None):
        palette = ColorPalette(**colors)
        if shades:
            for name, factor in shades:
                palette.add_shade(name, factor)
        
        self.set(ColorPalette, name, ColorPalette())
        
    def get_color_palette(self, name):
        return self.get(ColorPalette, name)
