from typing import Any, Literal, Optional

import pygame as pg

from ..utils import Color, Colors, replace_color, vec2


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
            self, template: pg.Surface, grid_width: Literal[1, 2, 3] = 2, grid_height: Literal[1, 2, 3] = 2,
            horizontal_region_sizes: Optional[int | tuple[int, int] | tuple[int, int, int]] = None,
            vertical_region_sizes: Optional[int | tuple[int, int] | tuple[int, int, int]] = None,
            horizontal_fill_mode: Literal["stretch", "repeat"] = "stretch",
            vertical_fill_mode: Literal["stretch", "repeat"] = "stretch",
            template_bg_color: Optional[Color] = None,
            template_bd_color: Optional[Color] = None,
    ):
        super().__init__()
        
        self._template = template
        
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
            
            x_sizes = self._get_destination_sizes(
                width,
                [region.width for region in self._regions[0]],
                self._grid_width
            )
            y_sizes = self._get_destination_sizes(
                height,
                [row[0].height for row in self._regions],
                self._grid_height
            )
            
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
                    self._blit_region(surface, source, dest_rect)
                    
                    dest_x += x_sizes[x]
                
                dest_y += y_sizes[y]
        
        if rotation:
            surface = pg.transform.rotozoom(surface, rotation, 1).convert_alpha()
        
        return surface
    
    @staticmethod
    def _get_destination_sizes(total_size: int, source_sizes: list[int], grid_size: int) -> list[int]:
        if grid_size == 1:
            return [total_size]
        
        if grid_size == 2:
            fixed = source_sizes[0] - 1
            
            if fixed >= total_size:
                return [total_size, 0]
            
            return [fixed, total_size - fixed]
        
        fixed_start = source_sizes[0]
        fixed_end = source_sizes[2]
        
        if fixed_start + fixed_end >= total_size:
            available = total_size
            fixed_total = fixed_start + fixed_end
            
            start = int(available * fixed_start / fixed_total)
            end = available - start
            
            return [start, 0, end]
        
        return [fixed_start, total_size - fixed_start - fixed_end, fixed_end]
    
    
    def _blit_region(self, destination: pg.Surface, source: pg.Surface, dest_rect: pg.Rect) -> None:
        source_width, source_height = source.get_size()
        
        if self._horizontal_fill_mode == "stretch" and self._vertical_fill_mode == "stretch":
            destination.blit(pg.transform.scale(source, dest_rect.size), dest_rect)
            return
        
        if self._horizontal_fill_mode == "stretch":
            source = pg.transform.scale(source, (dest_rect.width, source_height))
            source_width = dest_rect.width
        
        if self._vertical_fill_mode == "stretch":
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
            if sizes is None:
                return [total_size - 1, 1]
            
            if isinstance(sizes, int):
                if sizes < 1 or sizes >= total_size:
                    raise ValueError("Border size must be between 1 and template size - 1.")
                
                return [sizes - 1, 1]
            
            if len(sizes) != 2:
                raise ValueError("A 2-region grid requires two region sizes.")
            
            if sum(sizes) != total_size:
                raise ValueError(f"Region sizes {sizes} don't fill the template dimension ({total_size}).")
            
            return list(sizes)
        
        if sizes is None:
            border = (total_size - 1) // 2
            return [border, 1, total_size - border - 1]
        
        if isinstance(sizes, int):
            middle = total_size - sizes * 2
            
            if middle < 1:
                raise ValueError("Border size leaves no room for the expandable center.")
            
            return [sizes, middle, sizes]
        
        if len(sizes) != 3:
            raise ValueError("A 3-region grid requires three region sizes.")
        
        if sum(sizes) != total_size:
            raise ValueError(f"Region sizes {sizes} don't fill the template dimension ({total_size}).")
        
        return list(sizes)