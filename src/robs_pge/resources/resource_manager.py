import logging
from pathlib import Path
from typing import Any

from resources import Texture
from utils import Vec2, DictCollection, Font, ColorPalette, Color


class ResourceManager:
    def __init__(self):
        self._folders: DictCollection = DictCollection()
        self._resources: dict[type, DictCollection] = {}
    
    # region CORE
    
    def set(self, resource_type: type, resource_name: str, resource: Any):
        if not isinstance(resource, resource_type):
            raise TypeError(f"Resource '{resource_name}' is not of type '{resource_type.__name__}' but of type '{type(resource).__name__}'")
        
        if resource_type not in self._resources:
            self._resources[resource_type] = DictCollection()
        
        logging.info(f"Registering {resource_type.__name__} : {resource_name}")
        self._resources[resource_type].set(resource_name, resource)
    
    def get(self, resource_type: type, name: str) -> Any:
        if resource_type not in self._resources:
            raise KeyError(f"No resource of type '{resource_type.__name__}' registered")
        resource = self._resources[resource_type].get(name)
        if resource is None:
            raise KeyError(f"Resource '{name}' of type '{resource_type.__name__}' not found")
        return resource
    
    # endregion
    
    # region FOLDERS
    
    def add_folder(self, name: str, path: Path):
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(f"Folder '{path}' does not exist")
        if not path.is_dir():
            raise NotADirectoryError(f"'{path}' is not a directory")
        self._folders.set(name, path)
    
    def get_path(self, folder: str) -> Path:
        path = self._folders.get(folder)
        if path is None:
            raise KeyError(f"Asset folder '{folder}' is not registered")
        return path
    
    # endregion
    
    # region TEXTURES
    
    def load_texture(self, name: str, path: str, folder: str, dims: Vec2 = None, width: int = None, height: int = None) -> Texture:
        full_path = self.get_path(folder).joinpath(path)
        texture = Texture.from_path(full_path, dims, width, height)
        self.set_texture(name, texture)
        return texture
    
    def set_texture(self, name: str, texture: Texture):
        self.set(Texture, name, texture)
    
    def get_texture(self, name: str) -> Texture:
        return self.get(Texture, name)
    
    # endregion
    
    # region COLOR PALETTES
    
    def create_color_palette(self, name: str, colors: dict[str, Color] = None, shades: dict[str, float] = None, single_colors: dict[str, Color] = None) -> ColorPalette:
        palette = ColorPalette(colors, shades, single_colors)
        self.set_color_palette(name, palette)
        return palette
    
    def set_color_palette(self, name: str, palette: ColorPalette):
        self.set(ColorPalette, name, palette)
    
    def get_color_palette(self, name: str) -> ColorPalette:
        return self.get(ColorPalette, name)
    
    # endregion
    
    # region FONTS
    
    type _ColorArg = str | Color | tuple[str, Color]
    type _SizeArg = int | tuple[str, int]
    
    def _resolve_color(self, color: _ColorArg) -> tuple[str, Color]:
        if isinstance(color, tuple):
            return color
        if isinstance(color, str):
            if "." in color:
                palette_name, color_name = color.rsplit(".", 1)
            else:
                palette_name, color_name = "default", color
            return color_name, self.get_color_palette(palette_name).get(color_name)
        return str(color), color
    
    @staticmethod
    def _resolve_size(size: _SizeArg) -> tuple[str, int]:
        return size if isinstance(size, tuple) else (str(size), size)
    
    @staticmethod
    def _normalize_list(value):
        if isinstance(value, dict):
            return list(value.items())
        if not isinstance(value, list):
            return [value]
        return value
    
    def create_font(self, name: str, font: str = "dejavusansmono", size: _SizeArg = 14,
                    color: _ColorArg = None, bold: bool = False, italic: bool = False, line_spacing: int = 0):
        _, resolved_size = self._resolve_size(size)
        _, resolved_color = self._resolve_color(color) if color is not None else (None, None)
        self.set_font(name, Font(font, resolved_size, resolved_color, bold, italic, line_spacing))
    
    def create_font_sizes(self, name: str, font: str = "dejavusansmono", sizes: _SizeArg | list[_SizeArg] = 14,
                          color: _ColorArg = None, bold: bool = False, italic: bool = False, line_spacing: int = 0):
        for size in self._normalize_list(sizes):
            size_name, resolved_size = self._resolve_size(size)
            _, resolved_color = self._resolve_color(color) if color is not None else (None, None)
            self.set_font(f"{name}_{size_name}", Font(font, resolved_size, resolved_color, bold, italic, line_spacing))
    
    def create_fonts(self, name: str, font: str = "dejavusansmono",
                     sizes: _SizeArg | list[_SizeArg] = 14,
                     colors: _ColorArg | list[_ColorArg] | dict[str, Color] = None,
                     bold: bool = False, italic: bool = False, line_spacing: int = 0):
        sizes = self._normalize_list(sizes)
        colors = self._normalize_list(colors)
        
        for size in sizes:
            size_name, resolved_size = self._resolve_size(size)
            for color in colors:
                color_name, resolved_color = self._resolve_color(color) if color is not None else ("default", None)
                self.set_font(
                    f"{name}_{color_name}_{size_name}",
                    Font(font, resolved_size, resolved_color, bold, italic, line_spacing)
                )
    
    def set_font(self, name: str, font: Font):
        self.set(Font, name, font)
    
    def get_font(self, name: str) -> Font:
        return self.get(Font, name)
    
    # endregion