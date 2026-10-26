"""Draw command dataclasses that describe and render queued draw operations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

import pygame as pg
from pyglm import glm

from .styles import CircleStyle, LineStyle, RectStyle
from ..resources import SurfaceCache, Texture
from ..utils import FRect, Font, Rect, Transform, vec2, surface_pos_from_uv_pos

if TYPE_CHECKING:
    from ..objects import Layer


_camera_cache_layer: object = None
_camera_cache_transform: Transform = None
_camera_cache_center: vec2 = None


@dataclass
class DrawCommand:
    """Base dataclass for draw commands queued by renderers."""

    transform: Transform
    layer: Layer
    sub_layer: int
    anchor: vec2
    caching: bool
    clip_area: Optional[FRect]

    def get_screen_clip_rect(self) -> Optional[pg.Rect]:
        """Convert the command's clip area to a viewport-space rectangle.

        :return: The clipped rectangle in screen coordinates, or ``None`` when no clip area is set.
        """
        if self.clip_area is None:
            return None

        p1 = self.layer.world_to_viewport_pos(vec2(self.clip_area.left, self.clip_area.top))
        p2 = self.layer.world_to_viewport_pos(vec2(self.clip_area.right, self.clip_area.bottom))

        x0, x1 = sorted((p1.x, p2.x))
        y0, y1 = sorted((p1.y, p2.y))

        return pg.Rect(round(x0), round(y0), round(x1 - x0), round(y1 - y0))

    def get_composed_transform(self):
        """Combine this command's transform with its layer camera.

        :return: A tuple of viewport position, rotation in degrees, and relative scale.
        """
        global _camera_cache_layer, _camera_cache_transform, _camera_cache_center
        if self.layer is not _camera_cache_layer:
            _camera_cache_layer = self.layer
            _camera_cache_transform = self.layer.camera.transform
            _camera_cache_center = self.layer.camera.viewport_center

        ct = _camera_cache_transform
        vc = _camera_cache_center
        rotation = round((self.transform.rotation - ct.rotation) % 360, 2)
        scale = round(self.transform.scale / ct.scale, 4)
        if ct.rotation == 0 and ct.scale == 1:
            viewport_pos = self.transform.pos - ct.pos + vc
        else:
            viewport_pos = ct.apply_inverse_on_point(self.transform.pos) + vc
        return viewport_pos, rotation, scale
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, vec2]], surface_cache, font_cache) -> bool | None:
        """Draw the command into the blit queue.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts.
        :raises NotImplementedError: Always, because subclasses must implement drawing.
        """
        raise NotImplementedError("Draw command doesnt have a defined draw method")
    
    @staticmethod
    def add_blit(blit_call_queue: list[tuple[pg.Surface, vec2]], surface: pg.Surface, screen_pos: vec2, offset: Optional[vec2] = None, clip_rect: Optional[pg.Rect] = None):
        """Append a surface blit to the queue, cropping it to the clip rectangle.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface: Surface to blit.
        :param screen_pos: Screen position of the surface's anchor point.
        :param offset: Offset subtracted from the screen position before blitting.
        :param clip_rect: Optional screen-space rectangle used to crop the blit.
        """
        top_left = screen_pos - (offset or vec2())
        
        if clip_rect is not None:
            surf_rect = pg.Rect(round(top_left.x), round(top_left.y), surface.get_width(), surface.get_height())
            visible = surf_rect.clip(clip_rect)
            
            if visible.width <= 0 or visible.height <= 0:
                return
            
            if visible.topleft != surf_rect.topleft or visible.size != surf_rect.size:
                local_rect = pg.Rect(visible.x - surf_rect.x, visible.y - surf_rect.y, visible.width, visible.height)
                surface = surface.subsurface(local_rect)
                top_left = vec2(visible.x, visible.y)
        
        blit_call_queue.append((surface, top_left))
    
    @staticmethod
    def get_cached(surface_cache: SurfaceCache, key: tuple):
        """Look up a cached surface by key.

        :param surface_cache: Cache to query.
        :param key: Cache key identifying the surface.
        :return: The cached surface, or ``None`` when the key is absent.
        """
        return surface_cache.get(key)
    
    def create_surface(self, key, *args):
        """Create the surface represented by this command.

        :param key: Cache key describing the surface.
        :param args: Additional values needed by concrete draw commands.
        :raises NotImplementedError: Always, because subclasses must implement surface creation.
        """
        raise NotImplementedError("Draw command doesn't have a defined create_surface method")
    
    def get_surface(self, surface_cache: SurfaceCache, key: tuple, *args):
        """Return a surface from the cache or create and cache it when missing.

        :param surface_cache: Cache used to store generated surfaces.
        :param key: Cache key identifying the surface.
        :param args: Additional values forwarded to ``create_surface``.
        :return: A tuple of the surface and whether it was found in the cache.
        """
        if not self.caching:
            return self.create_surface(key, *args), None
        
        surface = self.get_cached(surface_cache, key)
        if surface is None:
            surface = self.create_surface(key, *args)
            surface_cache.add(key, surface)
            return surface, False
        return surface, True


@dataclass
class DrawTexture(DrawCommand):
    """Draw command that blits a texture with rotation and scaling."""

    texture: Texture
    
    def create_surface(self, key, *args):
        """Build a scaled and rotated surface for the texture.

        :param key: Cache key containing texture id, LOD level, rotation, and scale.
        :param args: Additional values passed by the draw method.
        :return: The transformed texture surface.
        """
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
            blit_call_queue: list[tuple[pg.Surface, vec2]],
            surface_cache,
            font_cache,
    ):
        """Submit the texture blit if it is visible at the current scale.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts, unused by textures.
        :return: Whether the surface was served from the cache, or ``None`` when skipped.
        """
        screen_pos, rotation, scale = self.get_composed_transform()
        
        if scale <= 0:
            return None
        
        lod_surface, lod_level = self.texture.get_lod_surface(scale)
        
        target_w = max(1, round(self.texture.width * scale))
        target_h = max(1, round(self.texture.height * scale))
        base_dims = vec2(target_w, target_h)
        
        key = (id(self.texture.surface), lod_level, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, lod_surface, rotation, target_w, target_h)
    
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, base_dims, rotation), self.get_screen_clip_rect())
        
        return cached


@dataclass
class DrawRect(DrawCommand):
    """Draw command that renders a filled rectangle with an optional border."""

    dims: vec2
    style: RectStyle
    
    def create_surface(self, key, *args):
        """Build the rectangle surface described by the cache key.

        :param key: Cache key containing builder id, dimensions, colors, border, radius, and rotation.
        :param args: Additional values passed by the draw method.
        :return: The rendered rectangle surface.
        """
        builder_id, dims, bg_color, bd, bd_color, bd_radius, rotation = key
        return self.style.builder.build_surface(vec2(dims), bg_color, bd, bd_color, bd_radius, rotation)
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, vec2]], surface_cache, font_cache):
        """Submit the rectangle blit if its scaled dimensions are positive.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts, unused by rectangles.
        :return: Whether the surface was served from the cache, or ``None`` when skipped.
        """
        screen_pos, rotation, scale = self.get_composed_transform()
        
        bg_color =  tuple(self.style.bg_color)
        bd =        round(self.style.bd * scale)
        bd_color =  tuple(self.style.bd_color)
        bd_radius = tuple(round(corner_radius * scale) for corner_radius in self.style.bd_radius) if isinstance(self.style.bd_radius, tuple) else round(self.style.bd_radius * scale)
        
        dims =      self.dims * scale
        key =       (id(self.style.builder), tuple(dims), bg_color, bd, bd_color, bd_radius, rotation)
        
        if dims[0] <= 0 or dims[1] <= 0:
            return None
        
        surface, cached = self.get_surface(surface_cache, key)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims, rotation), self.get_screen_clip_rect())
        
        return cached


@dataclass
class DrawCircle(DrawCommand):
    """Draw command that renders a filled circle with an optional border."""

    radius: int
    style: CircleStyle
    
    def create_surface(self, key, *args):
        """Build the circle surface described by the cache key.

        :param key: Cache key containing radius, colors, border width, and scale.
        :param args: Additional values passed by the draw method.
        :return: The rendered circle surface.
        """
        radius, bg_color, bd, bd_color, scale = key
        
        surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
        pg.draw.circle(surface, bg_color, (radius, radius), radius, 0)
        if bd:
            pg.draw.circle(surface, bd_color, (radius, radius), radius, bd)
            
        return surface
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, vec2]], surface_cache, font_cache):
        """Submit the circle blit if its scaled radius is positive.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts, unused by circles.
        :return: Whether the surface was served from the cache, or ``None`` when skipped.
        """
        screen_pos, rotation, scale = self.get_composed_transform()
        
        radius =    round(self.radius * scale)
        bg_color =  tuple(self.style.bg_color)
        bd =    round(self.style.bd * scale)
        bd_color =  tuple(self.style.bd_color)
        
        dims =      vec2(radius*2, radius*2)
        key =       (radius, bg_color, bd, bd_color, scale)
        
        if radius <= 0:
            return None
        
        surface, cached = self.get_surface(surface_cache, key)
        
        self.add_blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims), self.get_screen_clip_rect())
        
        return cached


@dataclass
class DrawText(DrawCommand):
    """Draw command that renders multi-line text using a cached pygame font."""

    text: str
    font: Font
    
    def create_surface(self, key, *args):
        """Build a multi-line text surface with spacing, scaling, and rotation applied.

        :param key: Cache key containing text, font key, color, spacing, rotation, and scale.
        :param args: Additional values passed by the draw method; the first is a pygame font.
        :return: The rendered text surface.
        """
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
    
    def draw(self, blit_call_queue, surface_cache, font_cache):
        """Submit the text blit if the text is non-empty.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts.
        :return: Whether the surface was served from the cache, or ``None`` when skipped.
        """
        if not self.text:
            return None
        
        screen_pos, rotation, scale = self.get_composed_transform()
        
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
        
        base_dims = vec2(unrotated_w * scale, unrotated_h * scale)
        
        # 2. Include scale in the cache key so we don't recalculate it every frame
        key = (self.text, font_key, color, base_spacing, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, pg_font)
        
        # 3. Pass the unrotated base_dims to your uv function (just like DrawTexture does)
        offset = surface_pos_from_uv_pos(self.anchor, base_dims, rotation)
        
        self.add_blit(blit_call_queue, surface, screen_pos, offset, self.get_screen_clip_rect())
        
        return cached
    
    
@dataclass
class DrawLine(DrawCommand):
    """Draw command that renders a connected polyline."""

    points: list[vec2]
    style: LineStyle
    
    def create_surface(self, key, *args):
        """Build a surface for the polyline from precomputed screen points.

        :param key: Cache key containing local points, color, width, rotation, and scale.
        :param args: Additional values passed by the draw method; the first is the screen points.
        :return: The rendered polyline surface.
        """
        points, color, width, rotation, scale = key
        screen_points: list[vec2] = args[0]
        
        h_width = width * 0.5
        pad     = round(width + 1)
        
        xs = [p.x for p in screen_points]
        ys = [p.y for p in screen_points]
        min_x, min_y = min(xs), min(ys)
        max_x, max_y = max(xs), max(ys)
        
        surf_w = max(1, round(max_x - min_x) + pad * 2)
        surf_h = max(1, round(max_y - min_y) + pad * 2)
        surface = pg.Surface((surf_w, surf_h), pg.SRCALPHA)
        
        local_points = [vec2(xs[i] - min_x + pad, ys[i] - min_y + pad) for i in range(len(xs))]
        
        if width > 4:
            pg.draw.circle(surface, color, local_points[0], h_width)
            for i in range(len(local_points) - 1):
                a, b = local_points[i: i+2]
                side = glm.normalize(vec2(a.y - b.y, b.x - a.x)) * h_width
                pg.draw.polygon(surface, color, [a + side, a - side, b - side, b + side])
                pg.draw.circle(surface, color, b, h_width)
        else:
            for i in range(len(local_points) - 1):
                pg.draw.line(surface, color, local_points[i], local_points[i + 1], width)
        
        return surface
    
    def draw(self, blit_call_queue, surface_cache, font_cache):
        """Submit the polyline blit if it has points.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts, unused by lines.
        :return: Whether the surface was served from the cache, or ``None`` when skipped.
        """
        if not self.points:
            return None

        position, rotation, scale = self.get_composed_transform()

        color = tuple(self.style.color)
        width = max(1, round(self.style.width * scale))
        
        screen_points = [self.layer.world_to_screen_pos(self.transform.apply_on_point(p)) for p in self.points]
        
        xs = [p.x for p in screen_points]
        ys = [p.y for p in screen_points]
        min_x, min_y = min(xs), min(ys)
        pad = round(width + 1)
        
        key     = (tuple((p.x, p.y) for p in self.points), color, width, rotation, scale)
        surface, cached = self.get_surface(surface_cache, key, screen_points)
        
        self.add_blit(blit_call_queue, surface, vec2(min_x - pad, min_y - pad), None, self.get_screen_clip_rect())
        
        return cached


@dataclass
class DrawSubSurface(DrawCommand):
    """Draw command that renders a cropped, scaled region of a texture."""

    texture: Texture
    sub_rect: Rect
    target_dims: vec2
    
    def create_surface(self, key, *args):
        """Build a cropped and scaled region of the texture.

        :param key: Cache key containing texture id, LOD level, source rect, and view size.
        :param args: Additional values passed by the draw method; the first is the LOD surface.
        :return: The rendered sub-surface, including transparent out-of-bounds areas.
        """
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
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, vec2]], surface_cache, font_cache):
        """Submit the cropped texture blit, applying rotation when present.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts, unused by sub-surfaces.
        :return: Whether the surface was served from the cache.
        """
        screen_pos, rotation, scale = self.get_composed_transform()
        
        view_w = max(1, round(self.target_dims.x * scale))
        view_h = max(1, round(self.target_dims.y * scale))
        base_dims = vec2(view_w, view_h)
        
        lod_surface, lod_level = self.texture.get_lod_surface(scale)
        
        key = (id(self.texture.surface), "subsurf_upright", lod_level, self.sub_rect.x, self.sub_rect.y, self.sub_rect.w, self.sub_rect.h, view_w, view_h)
        
        surface, cached = self.get_surface(surface_cache, key, lod_surface)
        
        if rotation:
            final_surf = pg.transform.rotate(surface, rotation)
        else:
            final_surf = surface
        
        self.add_blit(blit_call_queue, final_surf, screen_pos, surface_pos_from_uv_pos(self.anchor, base_dims, rotation), self.get_screen_clip_rect())
        
        return cached


@dataclass
class DrawChunkedSprite(DrawCommand):
    """Draw command that renders a texture in independently cached chunks."""

    texture: Texture
    chunk_size: int = 256
    
    def create_surface(self, key, *args):
        """Build one scaled or rotated chunk of the texture.

        :param key: Cache key containing texture id, chunk rect, rotation, scale, and LOD level.
        :param args: Additional values passed by the draw method; the first is the LOD surface.
        :return: The transformed chunk surface.
        """
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
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, vec2]], surface_cache, font_cache):
        """Submit visible texture chunks, culling those outside the viewport.

        :param blit_call_queue: Queue of surfaces and positions to blit this frame.
        :param surface_cache: Cache used to reuse generated surfaces.
        :param font_cache: Cache of rendered pygame fonts, unused by chunked sprites.
        :return: Whether all submitted chunk surfaces were served from the cache, or ``None`` when skipped.
        """
        screen_pos, rotation, scale = self.get_composed_transform()
        
        if scale <= 0:
            return None
        
        lod_surface, lod_level = self.texture.get_lod_surface(scale)
        
        base_w = self.texture.width
        base_h = self.texture.height
        cw = self.chunk_size
        ch = self.chunk_size

        screen_w, screen_h = self.layer.camera.viewport_dims

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
                    
                    blit_call_queue.append((surface, vec2(blit_x, blit_y)))
            
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
                
                blit_call_queue.append((surface, vec2(blit_x, blit_y)))
        
        return cached_all