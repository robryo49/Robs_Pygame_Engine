from dataclasses import dataclass

import pygame as pg

from .styles import CircleStyle, LineStyle, RectStyle
from ..core.camera import Camera
from ..resources.texture import Texture
from ..resources.surface_cache import SurfaceCache
from ..utils import Font, Transform, Vec2, surface_pos_from_uv_pos


@dataclass
class DrawCommand:
    transform: Transform
    layer: int
    anchor: Vec2
    caching: bool
    
    def get_composed_transform(self, camera: Camera):
        camera_transform: Transform =   camera.transform
        rotation =  round((self.transform.rotation - camera_transform.rotation)%360, 2)
        scale =     round(self.transform.scale / camera_transform.scale, 4)
        screen_pos = camera.world_to_screen_pos(self.transform.pos) if camera else self.transform.pos
        
        return screen_pos, rotation, scale
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache) -> bool | None:
        raise NotImplementedError("Draw command doesnt have a defined draw method")
    
    @staticmethod
    def add_blit(blit_call_queue: list[tuple[pg.Surface, Vec2]], surface: pg.Surface, screen_pos: Vec2, offset: Vec2 = None):
        blit_call_queue.append((surface, screen_pos - (offset or Vec2())))
    
    @staticmethod
    def get_cached(surface_cache: SurfaceCache, key: tuple):
        return surface_cache.get(key)
    
    def make_surface(self, key, *args):
        raise NotImplementedError("Draw command doesn't have a defined make_surface method")
    
    def get_surface(self, surface_cache: SurfaceCache, key: tuple, *args):
        if not self.caching:
            return self.make_surface(key, *args), None
        
        surface = self.get_cached(surface_cache, key)
        if surface is None:
            surface = self.make_surface(key, *args)
            surface_cache.add(key, surface)
            return surface, False
        return surface, True
        

@dataclass
class DrawTexture(DrawCommand):
    texture: Texture
    
    def make_surface(self, key, *args):
        texture_id, rotation, scale = key
        
        surface = pg.transform.rotozoom(self.texture.surface, rotation, scale).convert_alpha() if rotation or scale != 1 else self.texture.surface
        return surface
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        dims =      round(self.texture.dims * scale)
        key =       (id(self.texture.surface), rotation, scale)
        
        if dims[0] <= 0 or dims[1] <= 0:
            return None
        
        surface, cached = self.get_surface(surface_cache, key)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims, rotation))
        
        return cached


@dataclass
class DrawRect(DrawCommand):
    dims: Vec2
    style: RectStyle
    
    def make_surface(self, key, *args):
        
        dims, bg_color, bd, bd_color, bd_radius, rotation, scale = key
        
        surface = pg.Surface(dims, pg.SRCALPHA)
        pg.draw.rect(surface, bg_color, surface.get_rect(), 0, bd_radius)
        if bd:
            pg.draw.rect(surface, bd_color, surface.get_rect(), bd, bd_radius)
        if rotation:
            surface = pg.transform.rotozoom(surface, rotation, 1).convert_alpha()
        
        return surface
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        bg_color =  tuple(self.style.bg_color)
        bd =        round(self.style.bd * scale)
        bd_color =  tuple(self.style.bd_color)
        bd_radius = round(self.style.bd_radius * scale)
        
        dims =      round(self.dims * scale)
        key =       (tuple(dims), bg_color, bd, bd_color, bd_radius, rotation, scale)
        
        if dims[0] <= 0 or dims[1] <= 0:
            return None
        
        surface, cached = self.get_surface(surface_cache, key)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims, rotation))
        
        return cached


@dataclass
class DrawCircle(DrawCommand):
    radius: int
    style: CircleStyle
    
    def make_surface(self, key, *args):
        radius, bg_color, bd, bd_color, scale = key
        
        surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        pg.draw.circle(surface, bg_color, (radius, radius), radius, 0)
        if bd:
            pg.draw.circle(surface, bg_color, (radius, radius), radius, bd)
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        radius =    round(self.radius * scale)
        bg_color =  tuple(self.style.bg_color)
        bd =    round(self.style.bd * scale)
        bd_color =  tuple(self.style.bd_color)
        
        dims =      Vec2(radius*2, radius*2)
        key =       (radius, bg_color, bd, bd_color, scale)
        
        if radius <= 0:
            return None
        
        surface, cached = self.get_surface(surface_cache, key)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims))
        
        return cached


@dataclass
class DrawText(DrawCommand):
    text: str
    font: Font
    
    def make_surface(self, key, *args):
        text, font_key, color, spacing, rotation, scale = key
        pg_font: pg.font.Font = args[0]
        
        lines = []
        width = 0
        height = 0
        for line in text.split("\n"):
            surf = pg_font.render(line, True, color)
            width = max(width, surf.get_width())
            height += surf.get_height() + spacing
            lines.append(surf)
        height -= spacing
        
        surface = pg.Surface((width, height), pg.SRCALPHA)
        y = 0
        for surf in lines:
            surface.blit(surf, (0, y))
            y += surf.get_height() + spacing
        
        if rotation:
            surface = pg.transform.rotozoom(surface, rotation, 1).convert_alpha()
        
        return surface
    
    def draw(self, blit_call_queue, camera, surface_cache, font_cache):
        if not self.text:
            return None
        
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        font_size = round(self.font.size * scale)
        color     = tuple(self.font.color)
        spacing   = round(self.font.line_spacing * scale)
        font_key  = (self.font.key, font_size)
        
        if font_key not in font_cache:
            font_cache[font_key] = pg.font.SysFont(self.font.name, font_size, self.font.bold, self.font.italic)
        pg_font = font_cache[font_key]
        
        key     = (self.text, font_key, color, spacing, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, pg_font)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, Vec2(surface.get_width(), surface.get_height()), rotation))
        
        return cached
        

@dataclass
class DrawLine(DrawCommand):
    points: list[Vec2]
    style: LineStyle
    
    def make_surface(self, key, *args):
        points, color, width, rotation, scale = key
        screen_points: list[Vec2] = args[0]
        
        h_width = width * 0.5
        pad     = round(width + 1)
        
        xs = [p.x for p in screen_points]
        ys = [p.y for p in screen_points]
        min_x, min_y = min(xs), min(ys)
        max_x, max_y = max(xs), max(ys)
        
        surf_w = max(1, round(max_x - min_x) + pad * 2)
        surf_h = max(1, round(max_y - min_y) + pad * 2)
        surface = pg.Surface((surf_w, surf_h), pg.SRCALPHA)
        
        local_points = [Vec2(xs[i] - min_x + pad, ys[i] - min_y + pad) for i in range(len(xs))]
        
        if width > 4:
            pg.draw.circle(surface, color, local_points[0], h_width)
            for i in range(len(local_points) - 1):
                a, b = local_points[i: i+2]
                side = Vec2(a.y - b.y, b.x - a.x).normalize() * h_width
                pg.draw.polygon(surface, color, [a + side, a - side, b - side, b + side])
                pg.draw.circle(surface, color, b, h_width)
        else:
            for i in range(len(local_points) - 1):
                pg.draw.line(surface, color, local_points[i], local_points[i + 1], width)
        
        return surface
    
    def draw(self, blit_call_queue, camera, surface_cache, font_cache):
        
        position, rotation, scale = self.get_composed_transform(camera)
        
        color = tuple(self.style.color)
        width = max(1, round(self.style.width * scale))
        
        screen_points = [camera.world_to_screen_pos(self.transform.apply(p)) for p in self.points]
        
        xs = [p.x for p in screen_points]
        ys = [p.y for p in screen_points]
        min_x, min_y = min(xs), min(ys)
        pad = round(width + 1)
        
        key     = (tuple((p.x, p.y) for p in self.points), color, width, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, screen_points)
        
        self.add_blit(blit_call_queue, surface, Vec2(min_x - pad, min_y - pad))
        
        return cached