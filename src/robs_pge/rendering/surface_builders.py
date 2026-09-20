from __future__ import annotations

from typing import Any, Literal, Optional, TYPE_CHECKING

import pygame as pg

from ..utils import Color, Colors, replace_color, vec2

if TYPE_CHECKING:
    from ..resources import Texture


class SurfaceBuilder:
    def build_surface(self, *args) -> pg.Surface: ...


class RectBuilder(SurfaceBuilder):
    def build_surface(self, dims: vec2 = vec2(), bg_color: Color = Colors.WHITE, bd: int = 0, bd_color: Color = Colors.BLACK,
                      bd_radius: int | tuple[int, int, int, int] = 0, rotation: float = 0.0, *args: Any) -> pg.Surface:
        
        surface = pg.Surface(dims, pg.SRCALPHA)
        
        if isinstance(bd_radius, tuple):
            pg.draw.rect(surface, bg_color, surface.get_rect(), 0, 0, *bd_radius)
        else:
            pg.draw.rect(surface, bg_color, surface.get_rect(), 0, bd_radius)
        
        if bd:
            if isinstance(bd_radius, tuple):
                pg.draw.rect(surface, bd_color, surface.get_rect(), bd, 0, *bd_radius)
            else:
                pg.draw.rect(surface, bd_color, surface.get_rect(), bd, bd_radius)
        if rotation:
            surface = pg.transform.rotozoom(surface, rotation, 1).convert_alpha()
        
        return surface


class SlicedRectBuilder(RectBuilder):
    
    def __init__(
            self, template: Texture, grid_width: Literal[1, 2, 3] = 2, grid_height: Literal[1, 2, 3] = 2,
            horizontal_region_sizes: Optional[int | tuple[int, int] | tuple[int, int, int]] = None,
            vertical_region_sizes: Optional[int | tuple[int, int] | tuple[int, int, int]] = None,
            horizontal_fill_mode: Literal["stretch", "repeat"] = "stretch",
            vertical_fill_mode: Literal["stretch", "repeat"] = "stretch",
            template_bg_color: Optional[Color] = None,
            template_bd_color: Optional[Color] = None,
    ):
        super().__init__()
        
        self._template = template.surface
        
        self._grid_width = grid_width
        self._grid_height = grid_height
        
        self._horizontal_region_sizes = horizontal_region_sizes
        self._vertical_region_sizes = vertical_region_sizes
        
        self._horizontal_fill_mode = horizontal_fill_mode
        self._vertical_fill_mode = vertical_fill_mode
        
        self._template_bg_color = Color(template_bg_color) if template_bg_color is not None else None
        self._template_bd_color = Color(template_bd_color) if template_bd_color is not None else None
    
        self._template_cache: dict[tuple[tuple[int, ...], tuple[int, ...]], pg.Surface] = {}
        self._regions = self._build_regions()

    def build_surface(self, dims: vec2 = vec2(), bg_color: Color = Colors.WHITE, bd: int = 0,
                      bd_color: Color = Colors.BLACK, bd_radius: int | tuple[int, int, int, int] = 0,
                      rotation: float = 0.0, *args: Any) -> pg.Surface:
        key = (tuple(bg_color), tuple(bd_color))

        try:
            template = self._template_cache[key]
        except KeyError:
            template = self._template.copy()

            if self._template_bg_color is not None:
                replace_color(template, self._template_bg_color, bg_color)

            if self._template_bd_color is not None:
                replace_color(template, self._template_bd_color, bd_color)

            self._template_cache[key] = template

        width, height = int(dims.x), int(dims.y)

        if self._grid_width == 1 and self._grid_height == 1:
            surface = pg.transform.scale(template, (width, height))
        else:
            surface = pg.Surface((width, height), pg.SRCALPHA)

            x_source_sizes = [region.width for region in self._regions[0]]
            y_source_sizes = [row[0].height for row in self._regions]

            x_sizes = self._get_destination_sizes(width, x_source_sizes)
            y_sizes = self._get_destination_sizes(height, y_source_sizes)

            dest_y = 0

            for y, row in enumerate(self._regions):
                dest_x = 0

                for x, source_rect in enumerate(row):
                    dest_rect = pg.Rect(
                        dest_x,
                        dest_y,
                        x_sizes[x],
                        y_sizes[y]
                    )

                    source = template.subsurface(source_rect)
                    self._blit_region(
                        surface,
                        source,
                        dest_rect,
                        stretch_horizontal=self._is_middle_region(x, len(x_source_sizes)),
                        stretch_vertical=self._is_middle_region(y, len(y_source_sizes)),
                    )

                    dest_x += x_sizes[x]

                dest_y += y_sizes[y]

        if rotation:
            surface = pg.transform.rotozoom(surface, rotation, 1).convert_alpha()

        return surface

    @staticmethod
    def _is_middle_region(index: int, region_count: int) -> bool:
        return region_count == 1 or index == 1

    @staticmethod
    def _get_destination_sizes(total_size: int, source_sizes: list[int]) -> list[int]:
        if len(source_sizes) == 1:
            return [total_size]

        fixed_start = source_sizes[0]
        fixed_end = source_sizes[-1]
        middle_size = max(0, total_size - fixed_start - fixed_end)

        return [fixed_start, middle_size, fixed_end]


    def _blit_region(
            self,
            destination: pg.Surface,
            source: pg.Surface,
            dest_rect: pg.Rect,
            stretch_horizontal: bool,
            stretch_vertical: bool,
    ) -> None:
        if dest_rect.width <= 0 or dest_rect.height <= 0:
            return

        source_width, source_height = source.get_size()

        horizontal_fill_mode = self._horizontal_fill_mode if stretch_horizontal else "repeat"
        vertical_fill_mode = self._vertical_fill_mode if stretch_vertical else "repeat"

        if horizontal_fill_mode == "stretch" and vertical_fill_mode == "stretch":
            destination.blit(pg.transform.scale(source, dest_rect.size), dest_rect)
            return

        if horizontal_fill_mode == "stretch":
            source = pg.transform.scale(source, (dest_rect.width, source_height))
            source_width = dest_rect.width

        if vertical_fill_mode == "stretch":
            source = pg.transform.scale(source, (source_width, dest_rect.height))
            source_height = dest_rect.height

        y = dest_rect.top

        while y < dest_rect.bottom:
            x = dest_rect.left

            while x < dest_rect.right:
                width = min(source_width, dest_rect.right - x)
                height = min(source_height, dest_rect.bottom - y)

                destination.blit(source, (x, y), (0, 0, width, height))
                x += source_width

            y += source_height


    def _build_regions(self) -> list[list[pg.Rect]]:
        width, height = self._template.get_size()

        x_sizes = self._get_source_sizes(width, self._grid_width, self._horizontal_region_sizes)
        y_sizes = self._get_source_sizes(height, self._grid_height, self._vertical_region_sizes)

        regions = []
        y = 0

        for region_height in y_sizes:
            row = []
            x = 0

            for region_width in x_sizes:
                row.append(pg.Rect(x, y, region_width, region_height))
                x += region_width

            regions.append(row)
            y += region_height

        return regions

    @staticmethod
    def _get_source_sizes(total_size: int, grid_size: int, sizes: int | tuple[int, ...] | None) -> list[int]:
        if grid_size == 1:
            return [total_size]

        if grid_size == 2:
            if total_size < 3:
                raise ValueError("A 2-region grid requires at least 3 pixels so a 1px middle region can be inserted.")

            if sizes is None:
                start = total_size // 2
                end = total_size - start - 1

                return [start, 1, end]

            if isinstance(sizes, int):
                end = total_size - sizes - 1

                if sizes < 1 or end < 1:
                    raise ValueError("Border size must leave room for a 1px expandable middle region.")

                return [sizes, 1, end]

            if len(sizes) != 2:
                raise ValueError("A 2-region grid requires two corner region sizes.")

            if sum(sizes) != total_size - 1:
                raise ValueError(
                    f"2-region corner sizes {sizes} must leave exactly 1 pixel for the expandable middle region "
                    f"of the template dimension ({total_size})."
                )

            return [sizes[0], 1, sizes[1]]

        if sizes is None:
            border = (total_size - 1) // 2
            return [border, 1, total_size - border - 1]

        if isinstance(sizes, int):
            middle = total_size - sizes * 2

            if middle < 1:
                raise ValueError("Border size leaves no room for the expandable center.")

            return [sizes, middle, sizes]

        if len(sizes) == 2:
            return [sizes[0], total_size - sizes[0] - sizes[1], sizes[1]]

        if sum(sizes) != total_size:
            raise ValueError(f"Region sizes {sizes} don't fill the template dimension ({total_size}).")

        return list(sizes)