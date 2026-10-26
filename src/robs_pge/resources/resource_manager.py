"""Central registry for named textures, fonts, color palettes, styles, and resource folders."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from .texture import Texture
from ..rendering import Style
from ..sound import Sound, Music, Playlist
from ..utils import Color, ColorPalette, Font, vec2, StyleOrName

if TYPE_CHECKING:
    from ..core import Camera


class ResourceManager:
    """Stores resources by type and name and resolves defaults when lookups are ambiguous."""

    def __init__(self) -> None:
        """Initialize empty resource, default, and folder registries."""
        self._folders: dict[str, Path] = {}
        self._resources: dict[type, dict] = {}
        self._defaults: dict[type, Any] = {}
    
    # region CORE
    
    def register[T](self, resource_type: type[T], resource_name: str, resource: T) -> T:
        """
        Register a named resource of a specific type.

        :param resource_type: type used as the resource category
        :param resource_name: name used to retrieve the resource later
        :param resource: resource instance to store
        :return: the registered resource
        :raises TypeError: if the resource is not an instance of ``resource_type``
        """
        if not isinstance(resource, resource_type):
            raise TypeError(f"Resource '{resource_name}' is not of type '{resource_type.__name__}' but of type '{type(resource).__name__}'")
        
        if resource_type not in self._resources:
            self._resources[resource_type] = {}
        
        logging.info(f"Registering {resource_type.__name__} : {resource_name}")
        self._resources[resource_type][resource_name] = resource
        return resource
    
    def get[T](self, resource_type: type[T], name: str) -> T:
        """
        Look up a named resource by type.

        :param resource_type: type used as the resource category
        :param name: name of the resource to retrieve
        :return: the stored resource
        :raises KeyError: if the type or name is not registered
        """
        if resource_type not in self._resources:
            raise KeyError(f"No resource of type '{resource_type.__name__}' registered, only have: {list(self._resources.keys())}")
        resource = self._resources[resource_type].get(name)
        if resource is None:
            raise KeyError(f"Resource '{name}' of type '{resource_type.__name__}' not found, only have: {list(self._resources[resource_type].keys())}")
        return resource
    
    def register_default[T](self, resource_type: type[T], resource: T | str) -> T | str:
        """
        Register the default resource or resource name for a type.

        :param resource_type: type whose default is being set
        :param resource: resource instance or registered resource name to use as the default
        :return: the registered default
        :raises TypeError: if the default is neither an instance of ``resource_type`` nor a string
        """

        logging.info(f"Registering default {resource_type.__name__}")
        
        self._defaults[resource_type] = resource
        return resource
    
    def register_defaults[T](self, defaults: dict[type[T], Any]) -> dict[type[T], Any]:
        """
        Register multiple defaults and return the supplied mapping.

        :param defaults: mapping of resource types to their default resources or names
        :return: the supplied mapping
        """
        for k, v in defaults.items():
            self.register_default(k, v)
        return defaults
    
    def get_default[T](self, resource_type: type[T]) -> T:
        """
        Return the default resource for a type.

        :param resource_type: type whose default is requested
        :return: the default resource instance
        :raises KeyError: if the type has no registered default
        """
        resource = self._defaults.get(resource_type)
        if resource is None:
            raise KeyError(f"Resource type '{resource_type.__name__}' doesn't have a set default")
        elif isinstance(resource, str):
            return self.get(resource_type, resource)
        return resource
    
    def get_or_default[T](self, resource_type: type[T], resource_or_name: StyleOrName[T] | T | str) -> T:
        """
        Resolve a resource value, falling back to the registered default.

        :param resource_type: type used for named lookups and the fallback default
        :param resource_or_name: resource instance, registered name, or ``None`` to use the default
        :return: the resolved resource
        """
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
        """
        Register a named style.

        :param style_type: style class acting as the resource category
        :param name: name used to retrieve the style later
        :param style: style instance to store
        :return: the registered style
        """
        return self.register(style_type, name, style)
    
    def register_default_style[T: Style](self, style_type: type[T], style: StyleOrName[T]) -> StyleOrName[T]:
        """
        Register the default style or style name for a style class.

        :param style_type: style class whose default is being set
        :param style: style instance or registered name to use as the default
        :return: the registered default
        """
        return self.register_default(style_type, style)
    
    def register_default_styles[T: Style](self, styles: dict[type[T], StyleOrName[T]]) -> dict[type[T], StyleOrName[T]]:
        """
        Register multiple style defaults.

        :param styles: mapping of style classes to their default styles or names
        :return: the supplied mapping
        """
        return self.register_defaults(styles)
    
    def get_default_style[T: Style](self, style_type: type[T]) -> T:
        """
        Return the default style, creating a bare instance if necessary.

        :param style_type: style class whose default is requested
        :return: the default or newly constructed style instance
        """
        try:
            return self.get_default(style_type)
        except KeyError:
            return style_type()
        
    def get_style[T: Style](self, style_type: type[T], name: str) -> T:
        """
        Look up a named style by class.

        :param style_type: style class acting as the resource category
        :param name: name of the style to retrieve
        :return: the stored style
        :raises KeyError: if the style class or name is not registered
        """
        return self.get(style_type, name)
    
    def get_style_or_default[T: Style](self, style_type: type[T], style_or_name: StyleOrName[T]) -> T:
        """
        Resolve a style instance or name, falling back to a default style.

        :param style_type: style class used for named lookups and the fallback default
        :param style_or_name: style instance, registered name, or ``None`` to use the default
        :return: the resolved style
        """
        if style_or_name is None:
            return self.get_default_style(style_type)
        if isinstance(style_or_name, str):
            try:
                return self.get_style(style_type, style_or_name)
            except KeyError:
                return self.get_default_style(style_type)
        return style_or_name
        
    
    # endregion
    
    # region FOLDERS
    
    def register_folder(self, name: str, path: Path | str) -> Path:
        """
        Register a resource folder by name.

        :param name: name used to retrieve the folder later
        :param path: filesystem path of the folder
        :return: the resolved folder path
        :raises FileNotFoundError: if the path does not exist
        :raises NotADirectoryError: if the path is not a directory
        """
        path = Path(path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Folder '{path}' does not exist")
        if not path.is_dir():
            raise NotADirectoryError(f"'{path}' is not a directory")
        self._folders[name] = path
        return path
    
    def get_path(self, folder: str) -> Path:
        """
        Return the resolved path of a registered folder.

        :param folder: name of the registered folder
        :return: the folder path
        :raises KeyError: if the folder name is not registered
        """
        path = self._folders.get(folder)
        if path is None:
            raise KeyError(f"Folder '{folder}' is not registered, only have: {list(self._folders.keys())}")
        return path
    
    # endregion
    
    # region TEXTURES
    
    def load_texture(self, name: str, path: str, folder: str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None) -> Texture:
        """
        Load a texture from a registered folder and register it under a name.

        :param name: name used to register the loaded texture
        :param path: path of the image relative to the folder
        :param folder: name of the registered folder containing the image
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :return: the loaded texture
        """
        full_path = self.get_path(folder).joinpath(path)
        texture = Texture.from_path(full_path, dims, width, height)
        self.register_texture(name, texture)
        return texture
    
    def load_lod_texture(self, name: str, path: str, folder: str, dims: Optional[vec2] = None, width: Optional[int] = None, height: Optional[int] = None,
                         min_scale: Optional[float] = None, lod_factor: Optional[float] = None, camera: Optional[Camera] = None) -> Texture:
        """
        Load a texture and optionally pregenerate its lower-detail levels.

        :param name: name used to register the loaded texture
        :param path: path of the image relative to the folder
        :param folder: name of the registered folder containing the image
        :param dims: optional target dimensions
        :param width: optional target width, preserving aspect ratio when height is omitted
        :param height: optional target height, preserving aspect ratio when width is omitted
        :param min_scale: minimum scale to pregenerate LODs for
        :param lod_factor: scale factor between successive LOD levels
        :param camera: camera whose minimum zoom determines the LOD range to pregenerate
        :return: the loaded texture
        """
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
    
    def register_texture(self, name: str, texture: Texture) -> Texture:
        """
        Register a texture by name.

        :param name: name used to retrieve the texture later
        :param texture: texture instance to store
        :return: the registered texture
        """
        return self.register(Texture, name, texture)
    
    def get_texture(self, name: str) -> Texture:
        """
        Look up a texture by name.

        :param name: name of the texture to retrieve
        :return: the stored texture
        :raises KeyError: if the texture type or name is not registered
        """
        return self.get(Texture, name)
    
    # endregion
    
    # region COLOR PALETTES
    
    def create_color_palette(self, name: str, colors: Optional[dict[str, Color]] = None, shades: Optional[dict[str, float]] = None, single_colors: Optional[dict[str, Color]] = None) -> ColorPalette:
        """
        Create a color palette and register it under a name.

        :param name: name used to register the palette
        :param colors: base colors keyed by name
        :param shades: shade factors keyed by name
        :param single_colors: standalone colors keyed by name
        :return: the created color palette
        """
        palette = ColorPalette(colors, shades, single_colors)
        self.register_color_palette(name, palette)
        return palette
    
    def register_color_palette(self, name: str, palette: ColorPalette) -> ColorPalette:
        """
        Register a color palette by name.

        :param name: name used to retrieve the palette later
        :param palette: color palette to store
        :return: the registered palette
        """
        return self.register(ColorPalette, name, palette)
    
    def get_color_palette(self, name: str) -> ColorPalette:
        """
        Look up a color palette by name.

        :param name: name of the palette to retrieve
        :return: the stored color palette
        :raises KeyError: if the palette type or name is not registered
        """
        return self.get(ColorPalette, name)
    
    # endregion
    
    # region FONTS
    
    type _ColorArg = str | Color | tuple[str, Color]
    type _SizeArg = int | tuple[str, int]
    
    def _resolve_color(self, color: _ColorArg) -> tuple[str, Color]:
        """
        Resolve a color argument into a name and color instance.

        :param color: color instance, palette-qualified name, or pre-resolved pair
        :return: the resolved color name and color
        """
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
    def _normalize_list(value: Any) -> list[Any]:
        """
        Normalize a scalar, list, or mapping into a list.

        :param value: value to normalize
        :return: a list, with mappings converted to item tuples
        """
        if isinstance(value, dict):
            return list(value.items())
        if not isinstance(value, list):
            return [value]
        return value
    
    def create_font(self, name: str, font: str = "dejavusansmono", size: _SizeArg = 14,
                    color: Optional[_ColorArg] = None, bold: bool = False, italic: bool = False, line_spacing: int = 0) -> Font:
        """
        Create and register a font.

        :param name: name used to register the font
        :param font: font family name
        :param size: font size, optionally paired with a name
        :param color: font color, optionally paired with a name or palette reference
        :param bold: whether to use a bold face
        :param italic: whether to use an italic face
        :param line_spacing: extra spacing between lines
        :return: the created font
        """
        _, resolved_size = self._resolve_size(size)
        _, resolved_color = self._resolve_color(color) if color is not None else (None, None)
        return self.register_font(name, Font(font, resolved_size, resolved_color, bold, italic, line_spacing))
    
    def create_font_sizes(self, name: str, font: str = "dejavusansmono", sizes: _SizeArg | list[_SizeArg] = 14,
                          color: Optional[_ColorArg] = None, bold: bool = False, italic: bool = False, line_spacing: int = 0) -> list[Font]:
        """
        Create and register one font per supplied size.

        :param name: base name used to register each font
        :param font: font family name
        :param sizes: one or more font sizes, optionally paired with names
        :param color: font color, optionally paired with a name or palette reference
        :param bold: whether to use a bold face
        :param italic: whether to use an italic face
        :param line_spacing: extra spacing between lines
        :return: the created fonts
        """
        fonts: list[Font] = []
        for size in self._normalize_list(sizes):
            size_name, resolved_size = self._resolve_size(size)
            _, resolved_color = self._resolve_color(color) if color is not None else (None, None)
            fonts.append(self.register_font(f"{name}_{size_name}", Font(font, resolved_size, resolved_color, bold, italic, line_spacing)))
        return fonts
    
    def create_fonts(self, name: str, font: str = "dejavusansmono",
                     sizes: _SizeArg | list[_SizeArg] = 14,
                     colors: Optional[_ColorArg | list[_ColorArg] | dict[str, Color]] = None,
                     bold: bool = False, italic: bool = False, line_spacing: int = 0) -> list[Font]:
        """
        Create and register the cross-product of sizes and colors.

        :param name: base name used to register each font
        :param font: font family name
        :param sizes: one or more font sizes, optionally paired with names
        :param colors: one or more font colors or palette references
        :param bold: whether to use a bold face
        :param italic: whether to use an italic face
        :param line_spacing: extra spacing between lines
        :return: the created fonts
        """
        sizes = self._normalize_list(sizes)
        colors = self._normalize_list(colors)
        fonts: list[Font] = []
        for size in sizes:
            size_name, resolved_size = self._resolve_size(size)
            for color in colors:
                color_name, resolved_color = self._resolve_color(color) if color is not None else ("default", None)
                fonts.append(self.register_font(
                    f"{name}_{color_name}_{size_name}",
                    Font(font, resolved_size, resolved_color, bold, italic, line_spacing)
                ))
        return fonts
    
    def register_font(self, name: str, font: Font) -> Font:
        """
        Register a font by name.

        :param name: name used to retrieve the font later
        :param font: font instance to store
        :return: the registered font
        """
        return self.register_style(Font, name, font)
    
    def get_font(self, name: str) -> Font:
        """
        Look up a font by name.

        :param name: name of the font to retrieve
        :return: the stored font
        :raises KeyError: if the font type or name is not registered
        """
        return self.get(Font, name)
    
    # endregion

    # region SOUNDS

    def load_sound(self, name: str, path: str, folder: str):
        full_path = self.get_path(folder).joinpath(path)
        sound = Sound(full_path)
        self.register_sound(name, sound)
        return sound

    def register_sound(self, name: str, sound: Sound) -> Sound:
        self.register(Sound, name, sound)
        return sound

    def get_sound(self, name: str) -> Sound:
        return self.get(Sound, name)


    def load_music(self, name: str, path: str, folder: str, playlist: Optional[Playlist | str] = None):
        full_path = self.get_path(folder).joinpath(path)
        music = Music(name, str(full_path))
        self.register_music(name, music, playlist)
        return music

    def register_music(self, name: str, music: Music, playlist: Optional[Playlist | str] = None) -> Music:
        self.register(Music, name, music)

        if isinstance(playlist, str):
            try:
                playlist: Playlist = self.get_playlist(playlist)
            except KeyError:
                playlist: Playlist = self.register_playlist(str(playlist), Playlist(str(playlist), []))
        if isinstance(playlist, Playlist):
            playlist.add_music(music)

        return music

    def get_music(self, name: str) -> Music:
        return self.get(Music, name)


    def load_playlist(self, name: str, path: str, folder: str):
        full_path = self.get_path(folder).joinpath(path)
        valid_extensions = {".mp3", ".ogg", ".wav"}
        music_files = [p for p in full_path.iterdir() if p.is_file() and p.suffix.lower() in valid_extensions]
        playlist = Playlist(name, [])
        for music_path in music_files:
            music_name = music_path.stem
            music = Music(music_name, str(music_path))
            self.register_music(music_name, music, playlist)
        self.register_playlist(name, playlist)
        return playlist

    def create_playlist(self, name, musics: list[Music | str]):
        playlist = Playlist(name, list(music if isinstance(music, Music) else self.get_music(music) for music in musics))
        self.register_playlist(name, playlist)
        return playlist

    def register_playlist(self, name: str, playlist: Playlist) -> Playlist:
        self.register(Playlist, name, playlist)
        return playlist

    def get_playlist(self, name: str) -> Playlist:
        return self.get(Playlist, name)

    # endregion