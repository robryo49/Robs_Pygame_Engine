from __future__ import annotations
from dataclasses import dataclass

import pygame as pg
import math

from .styles import CircleStyle, LineStyle, RectStyle
from ..resources import Texture, SurfaceCache
from ..utils import Font, Transform, Vec2, surface_pos_from_uv_pos, Rect, FRect

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Camera


@dataclass
class DrawCommand:
    transform: Transform
    sub_layer: int
    anchor: Vec2
    caching: bool
    clip_area: Optional[FRect]
    
    def get_screen_clip_rect(self, camera: Camera) -> Optional[pg.Rect]:
        if self.clip_area is None:
            return None
        
        p1 = camera.world_to_screen_pos(Vec2(self.clip_area.left, self.clip_area.top))
        p2 = camera.world_to_screen_pos(Vec2(self.clip_area.right, self.clip_area.bottom))
        
        x0, x1 = sorted((p1.x, p2.x))
        y0, y1 = sorted((p1.y, p2.y))
        
        return pg.Rect(round(x0), round(y0), round(x1 - x0), round(y1 - y0))
    
    def get_composed_transform(self, camera: Camera):
        camera_transform: Transform =   camera.transform
        rotation =  round((self.transform.rotation - camera_transform.rotation)%360, 2)
        scale =     round(self.transform.scale / camera_transform.scale, 4)
        screen_pos = camera.world_to_screen_pos(self.transform.pos) if camera else self.transform.pos
        
        return screen_pos, rotation, scale
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache) -> bool | None:
        raise NotImplementedError("Draw command doesnt have a defined draw method")
    
    @staticmethod
    def add_blit(blit_call_queue: list[tuple[pg.Surface, Vec2]], surface: pg.Surface, screen_pos: Vec2, offset: Optional[Vec2] = None, clip_rect: Optional[pg.Rect] = None):
        top_left = screen_pos - (offset or Vec2())
        
        if clip_rect is not None:
            surf_rect = pg.Rect(round(top_left.x), round(top_left.y), surface.get_width(), surface.get_height())
            visible = surf_rect.clip(clip_rect)
            
            if visible.width <= 0 or visible.height <= 0:
                return
            
            if visible.topleft != surf_rect.topleft or visible.size != surf_rect.size:
                local_rect = pg.Rect(visible.x - surf_rect.x, visible.y - surf_rect.y, visible.width, visible.height)
                surface = surface.subsurface(local_rect)
                top_left = Vec2(visible.x, visible.y)
        
        blit_call_queue.append((surface, top_left))
    
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
        texture_id, _, rotation, scale = key
        
        if not rotation and scale == 1:
            return self.texture.surface
        
        base_surface, _ = self.texture.get_lod_surface(scale)
        
        if scale != 1:
            new_w = max(1, round(self.texture.width * scale))
            new_h = max(1, round(self.texture.height * scale))
            surface = pg.transform.scale(base_surface, (new_w, new_h))
        else:
            surface = base_surface
        
        if rotation:
            surface = pg.transform.rotate(surface, rotation)
        
        return surface.convert_alpha()
    
    def draw(
            self,
            blit_call_queue: list[tuple[pg.Surface, Vec2]],
            camera,
            surface_cache,
            font_cache,
    ):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        if scale <= 0:
            return None
        
        lod_surface, lod_level = self.texture.get_lod_surface(scale)
        
        target_w = max(1, round(self.texture.width * scale))
        target_h = max(1, round(self.texture.height * scale))
        base_dims = Vec2(target_w, target_h)
        
        key = (id(self.texture.surface), lod_level, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, lod_surface, rotation, target_w, target_h)
    
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, base_dims, rotation), self.get_screen_clip_rect(camera))
        
        return cached


@dataclass
class DrawRect(DrawCommand):
    dims: Vec2
    style: RectStyle
    
    def make_surface(self, key, *args):
        
        dims, bg_color, bd, bd_color, bd_radius, rotation, scale = key
        
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
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        bg_color =  tuple(self.style.bg_color)
        bd =        round(self.style.bd * scale)
        bd_color =  tuple(self.style.bd_color)
        bd_radius = tuple(round(corner_radius * scale) for corner_radius in self.style.bd_radius) if isinstance(self.style.bd_radius, tuple) else round(self.style.bd_radius * scale)
        
        dims =      round(self.dims * scale)
        key =       (tuple(dims), bg_color, bd, bd_color, bd_radius, rotation, scale)
        
        if dims[0] <= 0 or dims[1] <= 0:
            return None
        
        surface, cached = self.get_surface(surface_cache, key)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims, rotation), self.get_screen_clip_rect(camera))
        
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
            pg.draw.circle(surface, bd_color, (radius, radius), radius, bd)
            
        return surface
    
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
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims), self.get_screen_clip_rect(camera))
        
        return cached


@dataclass
class DrawText(DrawCommand):
    text: str
    font: Font
    
    def make_surface(self, key, *args):
        # Added scale to the cache key unpack
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
        
        # Apply scaling BEFORE rotation for better visual quality
        if scale != 1.0:
            new_w = max(1, round(width * scale))
            new_h = max(1, round(height * scale))
            surface = pg.transform.smoothscale(surface, (new_w, new_h))
        
        if rotation:
            surface = pg.transform.rotozoom(surface, rotation, 1.0).convert_alpha()
        
        return surface
    
    def draw(self, blit_call_queue, camera, surface_cache, font_cache):
        if not self.text:
            return None
        
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        base_font_size = round(self.font.size)
        color          = tuple(self.font.color)
        base_spacing   = round(self.font.line_spacing)
        font_key       = (self.font.key, base_font_size)
        
        if font_key not in font_cache:
            font_cache[font_key] = pg.font.SysFont(self.font.name, base_font_size, self.font.bold, self.font.italic)
        pg_font = font_cache[font_key]
        
        # 1. Calculate unrotated base dimensions for accurate anchoring
        unrotated_w = 0
        unrotated_h = 0
        for line in self.text.split("\n"):
            w, h = pg_font.size(line)
            unrotated_w = max(unrotated_w, w)
            unrotated_h += h + base_spacing
        unrotated_h -= base_spacing
        
        base_dims = Vec2(unrotated_w * scale, unrotated_h * scale)
        
        # 2. Include scale in the cache key so we don't recalculate it every frame
        key = (self.text, font_key, color, base_spacing, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, pg_font)
        
        # 3. Pass the unrotated base_dims to your uv function (just like DrawTexture does)
        offset = surface_pos_from_uv_pos(self.anchor, base_dims, rotation)
        
        self.add_blit(blit_call_queue, surface, screen_pos, offset, self.get_screen_clip_rect(camera))
        
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
        
        self.add_blit(blit_call_queue, surface, Vec2(min_x - pad, min_y - pad), None, self.get_screen_clip_rect(camera))
        
        return cached


@dataclass
class DrawSubSurface(DrawCommand):
    texture: Texture
    sub_rect: Rect
    target_dims: Vec2
    
    def make_surface(self, key, *args):
        _, _, lod_level, sx, sy, sw, sh, view_w, view_h = key
        lod_surface: pg.Surface = args[0]
        
        surface = pg.Surface((view_w, view_h), pg.SRCALPHA)
        
        w_ratio = lod_surface.get_width() / self.texture.width
        h_ratio = lod_surface.get_height() / self.texture.height
        
        lod_sub_rect = Rect(
            round(sx * w_ratio), round(sy * h_ratio),
            max(1, round(sw * w_ratio)), max(1, round(sh * h_ratio))
        )
        lod_texture_rect = lod_surface.get_rect()
        
        if lod_sub_rect.colliderect(lod_texture_rect):
            safe_sub_rect = lod_sub_rect.clip(lod_texture_rect)
            
            x_ratio = view_w / lod_sub_rect.w
            y_ratio = view_h / lod_sub_rect.h
            
            dest_x = int((safe_sub_rect.x - lod_sub_rect.x) * x_ratio)
            dest_y = int((safe_sub_rect.y - lod_sub_rect.y) * y_ratio)
            dest_w = int(safe_sub_rect.w * x_ratio)
            dest_h = int(safe_sub_rect.h * y_ratio)
            
            if dest_w > 0 and dest_h > 0:
                sub_surf = lod_surface.subsurface(safe_sub_rect)
                pg.transform.scale(sub_surf, (dest_w, dest_h), surface.subsurface(Rect(dest_x, dest_y, dest_w, dest_h)))
        
        return surface
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        view_w = max(1, round(self.target_dims.x * scale))
        view_h = max(1, round(self.target_dims.y * scale))
        base_dims = Vec2(view_w, view_h)
        
        lod_surface, lod_level = self.texture.get_lod_surface(scale)
        
        key = (id(self.texture.surface), "subsurf_upright", lod_level, self.sub_rect.x, self.sub_rect.y, self.sub_rect.w, self.sub_rect.h, view_w, view_h)
        
        surface, cached = self.get_surface(surface_cache, key, lod_surface)
        
        if rotation:
            final_surf = pg.transform.rotate(surface, rotation)
        else:
            final_surf = surface
        
        self.add_blit(blit_call_queue, final_surf, screen_pos, surface_pos_from_uv_pos(self.anchor, base_dims, rotation), self.get_screen_clip_rect(camera))
        
        return cached


@dataclass
class DrawChunkedSprite(DrawCommand):
    texture: Texture
    chunk_size: int = 256
    
    def make_surface(self, key, *args):
        texture_id, cx, cy, cw, ch, rotation, scale, lod_level = key
        lod_surface: pg.Surface = args[0]
        
        if lod_level == 0:
            sub_surf = self.texture.surface.subsurface(Rect(cx, cy, cw, ch))
        else:
            w_ratio = lod_surface.get_width() / self.texture.width
            h_ratio = lod_surface.get_height() / self.texture.height
            
            lod_x = int(cx * w_ratio)
            lod_y = int(cy * h_ratio)
            
            lod_w = max(1, int((cx + cw) * w_ratio) - lod_x)
            lod_h = max(1, int((cy + ch) * h_ratio) - lod_y)
            
            lod_w = min(lod_w, lod_surface.get_width() - lod_x)
            lod_h = min(lod_h, lod_surface.get_height() - lod_y)
            
            sub_surf = lod_surface.subsurface(Rect(lod_x, lod_y, lod_w, lod_h))
        
        if scale != 1:
            new_w = max(1, math.ceil(cw * scale))
            new_h = max(1, math.ceil(ch * scale))
            sub_surf = pg.transform.scale(sub_surf, (new_w, new_h))
        
        if rotation:
            sub_surf = pg.transform.rotate(sub_surf, rotation)
        
        return sub_surf.convert_alpha()
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        if scale <= 0:
            return None
        
        lod_surface, lod_level = self.texture.get_lod_surface(scale)
        
        base_w = self.texture.width
        base_h = self.texture.height
        cw = self.chunk_size
        ch = self.chunk_size

        screen_w, screen_h = camera.display_dims

        anchor_offset_x = self.anchor.x * base_w
        anchor_offset_y = self.anchor.y * base_h
        
        cached_all = True
        
        if not rotation:
            local_screen_left   = anchor_offset_x - (screen_pos.x / scale)
            local_screen_right  = anchor_offset_x + ((screen_w - screen_pos.x) / scale)
            local_screen_top    = anchor_offset_y - (screen_pos.y / scale)
            local_screen_bottom = anchor_offset_y + ((screen_h - screen_pos.y) / scale)
            
            start_chunk_x = max(0, int(local_screen_left // cw))
            end_chunk_x   = min(math.ceil(base_w / cw), int(math.ceil(local_screen_right / cw)))
            
            start_chunk_y = max(0, int(local_screen_top // ch))
            end_chunk_y   = min(math.ceil(base_h / ch), int(math.ceil(local_screen_bottom / ch)))
            
            for chk_y in range(start_chunk_y, end_chunk_y):
                y = chk_y * ch
                chunk_h = min(ch, base_h - y)
                
                for chk_x in range(start_chunk_x, end_chunk_x):
                    x = chk_x * cw
                    chunk_w = min(cw, base_w - x)
                    
                    cx_local = (x + chunk_w / 2.0) - anchor_offset_x
                    cy_local = (y + chunk_h / 2.0) - anchor_offset_y
                    
                    chunk_center_x = screen_pos.x + cx_local * scale
                    chunk_center_y = screen_pos.y + cy_local * scale
                    
                    key = (id(self.texture.surface), x, y, chunk_w, chunk_h, 0.0, scale, lod_level)
                    surface, cached = self.get_surface(surface_cache, key, lod_surface)
                    if not cached:
                        cached_all = False
                    
                    final_dims = surface.get_size()
                    blit_x = round(chunk_center_x - final_dims[0] / 2.0)
                    blit_y = round(chunk_center_y - final_dims[1] / 2.0)
                    
                    blit_call_queue.append((surface, Vec2(blit_x, blit_y)))
            
            return cached_all
        
        for y in range(0, base_h, ch):
            chunk_h = min(ch, base_h - y)
            for x in range(0, base_w, cw):
                chunk_w = min(cw, base_w - x)
                
                cx_local = (x + chunk_w / 2.0) - anchor_offset_x
                cy_local = (y + chunk_h / 2.0) - anchor_offset_y
                
                vec = pg.math.Vector2(cx_local * scale, cy_local * scale).rotate(-rotation)
                
                chunk_center_x = screen_pos.x + vec.x
                chunk_center_y = screen_pos.y + vec.y
                
                chunk_radius = math.hypot(chunk_w, chunk_h) * 0.5 * scale
                if (chunk_center_x + chunk_radius < 0 or
                        chunk_center_x - chunk_radius > screen_w or
                        chunk_center_y + chunk_radius < 0 or
                        chunk_center_y - chunk_radius > screen_h):
                    continue
                
                key = (id(self.texture.surface), x, y, chunk_w, chunk_h, rotation, scale, lod_level)
                surface, cached = self.get_surface(surface_cache, key, lod_surface)
                if not cached:
                    cached_all = False
                
                final_dims = surface.get_size()
                blit_x = round(chunk_center_x - final_dims[0] / 2.0)
                blit_y = round(chunk_center_y - final_dims[1] / 2.0)
                
                blit_call_queue.append((surface, Vec2(blit_x, blit_y)))
        
        return cached_all