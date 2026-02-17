from dataclasses import dataclass, field
import pygame as pg

from ..core.camera import Camera
from .styles import CircleStyle, RectStyle
from ..resources import Texture
from ..utils import Anchor, Font, Transform, Vec2, surface_pos_from_uv_pos


@dataclass
class DrawCommand:
    transform: Transform
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        raise NotImplementedError("Draw command doesnt have a defined draw method")
    
    @staticmethod
    def blit(blit_call_queue: list[tuple[pg.Surface, Vec2]], surface: pg.Surface, screen_pos: Vec2, offset: Vec2 = None):
        blit_call_queue.append((surface, screen_pos - (offset or Vec2())))
        
    def get_composed_transform(self, camera):
        camera_transform: Transform =   camera.transform if camera else Transform()
        rotation =  round((self.transform.rotation - camera_transform.rotation)%360, 2)
        scale =     round(self.transform.scale / camera_transform.scale, 4)
        screen_pos = camera.world_to_screen_pos(self.transform.pos) if camera else self.transform.pos
        
        return screen_pos, rotation, scale

@dataclass
class DrawTexture(DrawCommand):
    texture: Texture
    layer: int = 0
    anchor: Vec2 = field(default_factory=lambda: Anchor.C)
    
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        dims =      round(self.texture.dims * scale)
        key =       (id(self.texture.surface), rotation, scale)
        
        if dims[0] <= 0 or dims[1] <= 0:
            return
        
        if not surface_cache.has(key):
            surface = pg.transform.rotozoom(self.texture.surface, rotation, scale).convert_alpha() if rotation or scale != 1 else self.texture.surface
            surface_cache.add(key, surface)
        else:
            surface = surface_cache.get(key)
        
        self.blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims, rotation))


@dataclass
class DrawRect(DrawCommand):
    dims: Vec2
    style: RectStyle
    layer: int = 0
    anchor: Vec2 = field(default_factory=lambda: Anchor.C)
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        bg_color =  tuple(self.style.bg_color)
        border =    round(self.style.border * scale)
        bd_color =  tuple(self.style.bd_color)
        bd_radius = round(self.style.bd_radius * scale)
        
        dims =      round(self.dims * scale)
        key =       (tuple(dims), bg_color, border, bd_color, bd_radius, rotation, scale)
        
        if dims[0] <= 0 or dims[1] <= 0:
            return
        
        if not surface_cache.has(key):
            surface = pg.Surface(dims, pg.SRCALPHA)
            pg.draw.rect(surface, bg_color, surface.get_rect(), 0, bd_radius)
            if border:
                pg.draw.rect(surface, bd_color, surface.get_rect(), border, bd_radius)
            if rotation:
                surface = pg.transform.rotozoom(surface, rotation, 1).convert_alpha()
            surface_cache.add(key, surface)
        else:
            surface = surface_cache.get(key)
        
        self.blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims, rotation))


@dataclass
class DrawCircle(DrawCommand):
    radius: int
    style: CircleStyle
    layer: int = 0
    anchor: Vec2 = field(default_factory=lambda: Anchor.C)
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        radius =    round(self.radius * scale)
        bg_color =  tuple(self.style.bg_color)
        border =    round(self.style.border * scale)
        bd_color =  tuple(self.style.bd_color)
        
        dims =      Vec2(radius*2, radius*2)
        key =       (radius, bg_color, border, bd_color, scale)
        
        if radius <= 0:
            return
        
        if not surface_cache.has(key):
            surface = pg.Surface((radius*2, radius*2), pg.SRCALPHA)
            pg.draw.circle(surface, bg_color, (radius, radius), radius, 0)
            if border:
                pg.draw.circle(surface, bg_color, (radius, radius), radius, border)
            surface_cache.add(key, surface)
        else:
            surface = surface_cache.get(key)
        
        self.blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, dims))
    
    
@dataclass
class DrawText(DrawCommand):
    text: str
    font: Font
    layer: int = 0
    anchor: Vec2 = field(default_factory=lambda: Anchor.TL)
    
    def draw(self, blit_call_queue: list[tuple[pg.Surface, Vec2]], camera: Camera, surface_cache, font_cache):
        screen_pos, rotation, scale = self.get_composed_transform(camera)
        
        font_size = round(self.font.size * scale)
        color =     tuple(self.font.color)
        spacing =   round(self.font.line_spacing * scale)
        
        key = (self.font.key, font_size)
        
        if self.text == "":
            return
        
        if key not in font_cache:
            font = pg.font.SysFont(self.font.name, font_size, self.font.bold, self.font.italic)
            font_cache[key] = font
        else:
            font = font_cache[key]
        
        lines = []
        width = 0
        height = 0
        for line in self.text.split("\n"):
            surf = font.render(line, True, color)
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
        
        self.blit(blit_call_queue, surface, screen_pos, surface_pos_from_uv_pos(self.anchor, Vec2(width, height), rotation))

    