from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from ..resources import Texture
from..rendering import Style
from ..utils import Color, ColorPalette, Font, TypedDictCollection, vec2, StyleOrName

if TYPE_CHECKING:
    from ..core import Camera


class ResourceManager:
    def __init__(self):
        self._folders = TypedDictCollection(str, Path)
        self._resources = TypedDictCollection(type, TypedDictCollection)
        self._defaults: dict[type, Any] = {}
    
    # region CORE
    
    def register[T](self, resource_type: type[T], resource_name: str, resource: T) -> T:
        if not isinstance(resource, resource_type):
            raise TypeError(f"Resource '{resource_name}' is not of type '{resource_type.__name__}' but of type '{type(resource).__name__}'")
        
        if resource_type not in self._resources:
            self._resources[resource_type] = TypedDictCollection(str, resource_type)
        
        logging.info(f"Registering {resource_type.__name__} : {resource_name}")
        self._resources[resource_type].set(resource_name, resource)
        return resource
    
    def get[T](self, resource_type: type[T], name: str) -> T:
        if resource_type not in self._resources:
            raise KeyError(f"No resource of type '{resource_type.__name__}' registered, only have: {list(self._resources.keys())}")
        resource = self._resources[resource_type].get(name)
        if resource is None:
            raise KeyError(f"Resource '{name}' of type '{resource_type.__name__}' not found, only have: {list(self._resources[resource_type].keys())}")
        return resource
    
    def register_default[T](self, resource_type: type[T], resource: T | str) -> T | str:
        if not isinstance(resource, resource_type | str):
            raise TypeError(f"Resource '{resource}' is not of type '{resource_type.__name__}' but of type '{type(resource).__name__}'")
        
        logging.info(f"Registering default {resource_type.__name__}")
        
        self._defaults[resource_type] = resource
        return resource
    
    def register_defaults[T](self, defaults: dict[type[T], Any]) -> dict[type[T], Any]:
        for k, v in defaults.items():
            self.register_default(k, v)
        return defaults
    
    def get_default[T](self, resource_type: type[T]) -> T:
        resource = self._defaults.get(resource_type)
        if resource is None:
            raise KeyError(f"Resource type '{resource_type.__name__}' doesn't have a set default")
        elif isinstance(resource, str):
            return self.get(resource_type, resource)
        return resource
    
    def get_or_default[T](self, resource_type: type[T], resource_or_name: StyleOrName[T] | T | str) -> T:
        if resource_or_name is None:
            return self.get_default(resource_type)
        elif isinstance(resource_or_name, str):
            try:
                return self.get(resource_type, resource_or_name)
            except KeyError:
                return self.get_default(resource_type)
        else:
            return resource_or_name
    
    # endregion
    
    # region STYLES
    
    def register_style[T: Style](self, style_type: type[T], name: str, style: T) -> T:
        return self.register(style_type, name, style)
    
    def register_default_style[T: Style](self, style_type: type[T], style: StyleOrName[T]) -> StyleOrName[T]:
        return self.register_default(style_type, style)
    
    def register_default_styles[T: Style](self, styles: dict[type[T], StyleOrName[T]]):
        return self.register_defaults(styles)
    
    def get_default_style[T: Style](self, style_type: type[T]) -> T:
        try:
            return self.get_default(style_type)
        except KeyError:
            return style_type()
        
    def get_style[T: Style](self, style_type: type[T], name: str) -> T:
        return self.get(style_type, name)
    
    def get_style_or_default[T: Style](self, style_type: type[T], style_or_name: StyleOrName[T]) -> T:
        if style_or_name is None:
            return self.get_default_style(style_type)
        elif isinstance(style_or_name, str):
            try:
                return self.get_or_default(style_type, style_or_name)
            except KeyError:
                return self.get_default_style(style_type)
        else:
            return style_or_name
        
    
    # endregion
    
    # region FOLDERS
    
    def register_folder(self, name: str, path: Path):
        path = path.resolve()
        if not path.exists():
            raise FileNotFoundError(f"Folder '{path}' does not exist")
        if not path.is_dir():
            raise NotADirectoryError(f"'{path}' is not a directory")
        self._folders.set(name, path)
    
    def get_path(self, folder: str) -> Path:
        path = self._folders.get(folder)
        if path is None:
            raise KeyError(f"Folder '{folder}' is not registered, only have: {list(self._folders.keys())}")
        return path
    
    # endregion
    
    # region TEXTURES
    
    def load_texture(self, name: str, path: str, folder: str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None) -> Texture:
        full_path = self.get_path(folder).joinpath(path)
        texture = Texture.from_path(full_path, dims, width, height)
        self.register_texture(name, texture)
        return texture
    
    def load_lod_texture(self, name: str, path: str, folder: str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None,
                         min_scale: Optional[float] = None, lod_factor: Optional[float] = None, camera: Optional[Camera] = None) -> Texture:
        full_path = self.get_path(folder).joinpath(path)
        texture = Texture.from_path(full_path, dims, width, height)
        
        if lod_factor:
            texture.lod_factor = lod_factor
        if min_scale:
            texture.pregenerate_lods(min_scale)
        if camera and camera.min_zoom:
            texture.pregenerate_lods(camera.min_zoom)
        
        self.register_texture(name, texture)
        return texture
    
    def register_texture(self, name: str, texture: Texture):
        self.register(Texture, name, texture)
    
    def get_texture(self, name: str) -> Texture:
        return self.get(Texture, name)
    
    # endregion
    
    # region COLOR PALETTES
    
    def create_color_palette(self, name: str, colors: Optional[dict[str, Color]] = None, shades: Optional[dict[str, float]] = None, single_colors: Optional[dict[str, Color]] = None) -> ColorPalette:
        palette = ColorPalette(colors, shades, single_colors)
        self.register_color_palette(name, palette)
        return palette
    
    def register_color_palette(self, name: str, palette: ColorPalette):
        self.register(ColorPalette, name, palette)
    
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
                    color: Optional[_ColorArg] = None, bold: bool = False, italic: bool = False, line_spacing: int = 0):
        _, resolved_size = self._resolve_size(size)
        _, resolved_color = self._resolve_color(color) if color is not None else (None, None)
        self.register_font(name, Font(font, resolved_size, resolved_color, bold, italic, line_spacing))
    
    def create_font_sizes(self, name: str, font: str = "dejavusansmono", sizes: _SizeArg | list[_SizeArg] = 14,
                          color: Optional[_ColorArg] = None, bold: bool = False, italic: bool = False, line_spacing: int = 0):
        for size in self._normalize_list(sizes):
            size_name, resolved_size = self._resolve_size(size)
            _, resolved_color = self._resolve_color(color) if color is not None else (None, None)
            self.register_font(f"{name}_{size_name}", Font(font, resolved_size, resolved_color, bold, italic, line_spacing))
    
    def create_fonts(self, name: str, font: str = "dejavusansmono",
                     sizes: _SizeArg | list[_SizeArg] = 14,
                     colors: Optional[_ColorArg | list[_ColorArg] | dict[str, Color]] = None,
                     bold: bool = False, italic: bool = False, line_spacing: int = 0):
        sizes = self._normalize_list(sizes)
        colors = self._normalize_list(colors)
        
        for size in sizes:
            size_name, resolved_size = self._resolve_size(size)
            for color in colors:
                color_name, resolved_color = self._resolve_color(color) if color is not None else ("default", None)
                self.register_font(
                    f"{name}_{color_name}_{size_name}",
                    Font(font, resolved_size, resolved_color, bold, italic, line_spacing)
                )
    
    def register_font(self, name: str, font: Font):
        self.register_style(Font, name, font)
    
    def get_font(self, name: str) -> Font:
        return self.get(Font, name)
    
    # endregion