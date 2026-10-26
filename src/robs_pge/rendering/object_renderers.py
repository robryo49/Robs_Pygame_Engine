"""Concrete object renderers for shapes, sprites, text, and icons."""

from __future__ import annotations

from .draw_commands import DrawCircle, DrawLine, DrawRect, DrawText, DrawTexture, DrawSubSurface, DrawChunkedSprite
from .styles import *
from .object_renderer import ObjectRenderer
from ..resources import Icons, Texture
from ..utils import Anchor, Color, Font, Transform, length, vec2, Rect, FRect

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..objects import Layer


class RectRenderer(ObjectRenderer):
    """Renders a rectangle with optional border, corner radius, and style."""

    def __init__(self, dims: vec2, style: Optional[RectStyle] = None, cache=True) -> None:
        """Initialize the rectangle renderer.

        :param dims: Local rectangle dimensions.
        :param style: Rectangle style to copy, or a default style when omitted.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        
        self._dims: vec2 = dims
        
        self._style = (style or RectStyle()).copy()
    
    # region PROPERTIES
    
    # region style
    @property
    def style(self) -> RectStyle:
        """Return the rectangle style used for drawing."""
        return self._style
    
    @style.setter
    def style(self, value: RectStyle):
        """
        Set the rectangle style used for drawing.

        :param value: The new rectangle style used for drawing.
        """
        self._style = value
    # endregion
    
    # region dims
    @property
    def dims(self) -> vec2:
        """Return the rectangle dimensions."""
        return self._dims
    
    @dims.setter
    def dims(self, value: vec2):
        """
        Set the rectangle dimensions.

        :param value: The new rectangle dimensions.
        """
        self._dims = value
    
    @property
    def width(self):
        """Return the rectangle width."""
        return self.dims.x
    
    @width.setter
    def width(self, value: int):
        """
        Set the rectangle width.

        :param value: The new rectangle width.
        """
        self.dims.x = value
    
    @property
    def height(self):
        """Return the rectangle height."""
        return self.dims.y
    
    @height.setter
    def height(self, value: int):
        """
        Set the rectangle height.

        :param value: The new rectangle height.
        """
        self.dims.y = value
    
    # endregion
    
    # region bg_color
    @property
    def bg_color(self):
        """Return the background fill color."""
        return self.style.bg_color
    
    @bg_color.setter
    def bg_color(self, value):
        """
        Set the background fill color.

        :param value: The new background fill color.
        """
        self.style.bg_color = value
    # endregion
    
    # region bd
    @property
    def bd(self):
        """Return the border width."""
        return self.style.bd
    
    @bd.setter
    def bd(self, value):
        """
        Set the border width.

        :param value: The new border width.
        """
        self.style.bd = value
    # endregion
    
    # region bd_color
    @property
    def bd_color(self):
        """Return the border color."""
        return self.style.bd_color
    
    @bd_color.setter
    def bd_color(self, value):
        """
        Set the border color.

        :param value: The new border color.
        """
        self.style.bd_color = value
    # endregion
    
    # region bd_radius
    @property
    def bd_radius(self):
        """Return the corner radius or per-corner radii."""
        return self.style.bd_radius
    
    @bd_radius.setter
    def bd_radius(self, value):
        """
        Set the corner radius or per-corner radii.

        :param value: The new value.
        """
        self.style.bd_radius = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the rectangle.
        :return: The axis-aligned bounding box size in local units.
        """
        return vec2(length(self.dims)) if rotation else self.dims
    
    
    def test_hit(self, local_pos: vec2) -> bool:
        """Return whether a local-space point lies inside the rounded rectangle.

        :param local_pos: Point to test in local coordinates.
        :return: ``True`` when the point lies inside the rectangle shape.
        """
        x, y = local_pos
        w, h = self.dims
        
        if not (0 <= x <= w and 0 <= y <= h):
            return False
        
        max_r = min(float(w), float(h)) / 2
        
        bd_radius = self.bd_radius
        if isinstance(bd_radius, (tuple, list)):
            r_tl, r_tr, r_br, r_bl = (min(r, max_r) for r in bd_radius)
        else:
            r_bl = r_br = r_tl = r_tr = min(self.bd_radius, max_r)
        
        if x < w / 2:
            if y < h / 2:
                r, dx, dy = r_tl, x, y
            else:
                r, dx, dy = r_bl, x, h - y
        else:
            if y < h / 2:
                r, dx, dy = r_tr, w - x, y
            else:
                r, dx, dy = r_br, w - x, h - y
        
        if dx >= r or dy >= r:
            return True
        
        return (r - dx) ** 2 + (r - dy) ** 2 <= r ** 2
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a rectangle draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the rectangle.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawRect(transform, layer, sub_layer, anchor, self._cache, clip_area, self.dims, self.style))


class CircleRenderer(ObjectRenderer):
    """Renders a circle with optional border and style."""

    def __init__(self, radius: int, style: Optional[CircleStyle] = None, cache=True) -> None:
        """Initialize the circle renderer.

        :param radius: Circle radius in local units.
        :param style: Circle style to copy, or a default style when omitted.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        
        self._radius = radius
        
        self._style = (style or CircleStyle()).copy()
    
    # region PROPERTIES
    
    # region style
    @property
    def style(self):
        """Return the circle style used for drawing."""
        return self._style
    
    @style.setter
    def style(self, value: CircleStyle):
        """
        Set the circle style used for drawing.

        :param value: The new circle style used for drawing.
        """
        self._style = value
    # endregion
    
    # region radius
    @property
    def radius(self):
        """Return the circle radius."""
        return self._radius
    
    @radius.setter
    def radius(self, value: int):
        """
        Set the circle radius.

        :param value: The new circle radius.
        """
        self._radius = value
    
    @property
    def diameter(self):
        """Return the circle diameter."""
        return self.radius * 2
    
    @diameter.setter
    def diameter(self, value: int):
        """
        Set the circle diameter by updating the radius.

        :param value: The new value.
        """
        self.radius = value * 0.5
    
    @property
    def dims(self):
        """Return the circle dimensions as a square of the diameter."""
        return vec2(self.diameter)
    
    @property
    def width(self):
        """Return the circle diameter."""
        return self.diameter
    
    @width.setter
    def width(self, value: int):
        """
        Set the circle width by updating the radius.

        :param value: The new value.
        """
        self.radius = value * 0.5
    
    @property
    def height(self):
        """Return the circle diameter."""
        return self.diameter
    
    @height.setter
    def height(self, value: int):
        """
        Set the circle height by updating the radius.

        :param value: The new value.
        """
        self.radius = value * 0.5
    
    # endregion
    
    # region bg_color
    @property
    def bg_color(self):
        """Return the background fill color."""
        return self.style.bg_color
    
    @bg_color.setter
    def bg_color(self, value: Color):
        """
        Set the background fill color.

        :param value: The new background fill color.
        """
        self.style.bg_color = value
    # endregion
    
    # region bd
    @property
    def bd(self):
        """Return the border width."""
        return self.style.bd
    
    @bd.setter
    def bd(self, value: int):
        """
        Set the border width.

        :param value: The new border width.
        """
        self.style.bd = value
    # endregion
    
    # region bd_color
    @property
    def bd_color(self):
        """Return the border color."""
        return self.style.bd_color
    
    @bd_color.setter
    def bd_color(self, value: Color):
        """
        Set the border color.

        :param value: The new border color.
        """
        self.style.bd_color = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float) -> vec2:
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the circle.
        :return: The circle's diameter-based square dimensions.
        """
        return vec2(self.diameter)
    
    def test_hit(self, local_pos: vec2):
        """Return whether a local-space point lies inside the circle.

        :param local_pos: Point to test in local coordinates.
        :return: ``True`` when the point is within the circle radius.
        """
        pos = local_pos - self.get_offset(Anchor.C)
        return length(pos) <= self.radius
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a circle draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the circle.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawCircle(transform, layer, sub_layer, anchor, self._cache, clip_area, self.radius, self.style))


class LineRenderer(ObjectRenderer):
    """Renders a connected polyline."""

    def __init__(self, points: list[vec2], style: Optional[LineStyle] = None, cache: bool = True) -> None:
        """Initialize the polyline renderer.

        :param points: Ordered local-space points that define the polyline.
        :param style: Line style to copy, or a default style when omitted.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        
        self._points = points
        
        self._max_x = max(p.x for p in points) if points else 0
        self._max_y = max(p.y for p in points) if points else 0
        
        self._style = (style or LineStyle()).copy()
    
    # region PROPERTIES
    
    @property
    def dims(self):
        """Return the dimensions spanning the polyline's maximum point."""
        return vec2(self._max_x, self._max_y)
    
    # region points
    @property
    def points(self):
        """Return the polyline points in local coordinates."""
        return self._points
    
    @points.setter
    def points(self, value: list[vec2]):
        """
        Set the polyline points and recompute the maximum extents.

        :param value: The new value.
        """
        self._points = value
        self._max_x = max(p.x for p in value) if value else 0
        self._max_y = max(p.y for p in value) if value else 0
    # endregion
    
    # region style
    @property
    def style(self):
        """Return the line style used for drawing."""
        return self._style
    
    @style.setter
    def style(self, value: LineStyle):
        """
        Set the line style used for drawing.

        :param value: The new line style used for drawing.
        """
        self._style = value
    # endregion
    
    # region color
    @property
    def color(self) -> Color:
        """Return the line color."""
        return self.style.color

    @color.setter
    def color(self, value: Color) -> None:
        """
        Set the line color.

        :param value: The new line color.
        """
        self.style.color = value
    # endregion

    # region width
    @property
    def width(self) -> int:
        """Return the line width."""
        return self.style.width

    @width.setter
    def width(self, value: int) -> None:
        """
        Set the line width.

        :param value: The new line width.
        """
        self.style.width = value
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the polyline.
        :return: The doubled extent size, or its diagonal length when rotated.
        """
        return length(vec2(self._max_x, self._max_y)) * 2 if rotation else vec2(self._max_x, self._max_y) * 2
    
    def test_hit(self, local_pos: vec2):
        """Always report no hit because the line renderer is not hit-testable.

        :param local_pos: Point to test in local coordinates.
        :return: Always ``False``.
        """
        return False
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a polyline draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the polyline.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawLine(transform, layer, sub_layer, anchor, self._cache, clip_area, self.points, self.style))


class SpriteRenderer(ObjectRenderer):
    """Renders a texture as a sprite and hit-tests it by texture alpha."""

    def __init__(self, texture: Texture, cache=True) -> None:
        """Initialize the sprite renderer.

        :param texture: Texture drawn by this renderer.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        
        self._texture = texture
    
    # region PROPERTIES
    
    @property
    def texture(self):
        """Return the texture drawn by this renderer."""
        return self._texture
    
    # region dims
    @property
    def dims(self):
        """Return the texture dimensions."""
        return self.texture.dims
    
    @property
    def width(self):
        """Return the texture width."""
        return self.texture.width
    
    @property
    def height(self):
        """Return the texture height."""
        return self.texture.height
    
    # endregion
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the sprite.
        :return: The axis-aligned bounding box size in local units.
        """
        return vec2(length(self.dims)) if rotation else self.dims
    
    def test_hit(self, local_pos: vec2):
        """Return whether a local-space point hits a non-transparent texel.

        :param local_pos: Point to test in local coordinates.
        :return: ``True`` when the point is inside the texture and its alpha is non-zero.
        """
        
        x, y = local_pos
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        return self.texture.get_at_pos(local_pos).a > 0
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a texture draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the sprite.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawTexture(transform, layer, sub_layer, anchor, self._cache, clip_area, self.texture))


class IconRenderer(SpriteRenderer):
    """Renders a named icon from the icon registry as a sprite."""

    def __init__(self, icon: str, icon_size: int, icon_color, cache=True) -> None:
        """Initialize the icon renderer and fetch its texture.

        :param icon: Name of the icon in the icon registry.
        :param icon_size: Requested icon size in pixels.
        :param icon_color: Color used to tint the icon.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(Icons.get(icon, icon_size, icon_color), cache)
        
        self._icon = icon
        self._icon_size = icon_size
        self._icon_color = icon_color
        
    # region PROPERTIES
    
    # region icon
    @property
    def icon(self):
        """Return the icon registry name."""
        return self._icon
    
    @icon.setter
    def icon(self, value: str):
        """
        Set the icon name and refresh the cached texture.

        :param value: The new value.
        """
        self._icon = value
        self._update_icon()
    # endregion
    
    # region icon_size
    @property
    def icon_size(self):
        """Return the requested icon size."""
        return self._icon_size
    
    @icon_size.setter
    def icon_size(self, value: int):
        """
        Set the icon size and refresh the cached texture.

        :param value: The new value.
        """
        self._icon_size = value
        self._update_icon()
    # endregion
    
    # region icon_color
    @property
    def icon_color(self):
        """Return the icon tint color."""
        return self._icon_color
    
    @icon_color.setter
    def icon_color(self, value):
        """
        Set the icon tint color and refresh the cached texture.

        :param value: The new value.
        """
        self._icon_color = value
        self._update_icon()
    # endregion
    
    # endregion
    
    def _update_icon(self):
        """Refresh the sprite texture from the icon registry."""
        self._texture = Icons.get(self._icon, self._icon_size, self._icon_color)
        

class TextRenderer(ObjectRenderer):
    """Renders multi-line text using a font and reports its rendered bounds."""

    def __init__(self, text: str, font: Optional[Font]=None, cache=True) -> None:
        """Initialize the text renderer.

        :param text: Text to render, including any newline characters.
        :param font: Font to use, or a default font when omitted.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        
        self._text = text
        
        self._font = font or Font()
        self._dims = vec2(self.font.get_render_size(self.text))
    
    # region PROPERTIES
    
    # region text
    @property
    def text(self):
        """Return the text being rendered."""
        return self._text
    
    @text.setter
    def text(self, value):
        """
        Set the text and recompute its single-line render size.

        :param value: The new value.
        """
        self._text = value
        self._dims = vec2(self.font.get_render_size(self.text))
    # endregion
    
    @property
    def font(self):
        """Return the font used to render the text."""
        return self._font
    
    @property
    def dims(self):
        """Return the combined dimensions of all text lines and line spacing."""
        all_dims = list(self.font.get_render_size(txt) for txt in self.text.split("\n"))
        return vec2(max(v.x for v in all_dims), sum(v.y for v in all_dims) + self.font.line_spacing * (len(all_dims) - 1))
    
    # region color
    @property
    def color(self):
        """Return the text color."""
        return self.font.color
    
    @color.setter
    def color(self, value):
        """
        Set the text color.

        :param value: The new text color.
        """
        self.font.color = value
    # endregion
    
    @property
    def width(self):
        """Return the rendered text width."""
        return self.dims.x
    
    @property
    def height(self):
        """Return the rendered text height."""
        return self.dims.y
    
    # endregion
    
    def get_aabb_size(self, rotation: float):
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the text.
        :return: The axis-aligned bounding box size in local units.
        """
        return vec2(length(self.dims)) if rotation else self.dims
    
    def test_hit(self, local_pos: vec2):
        """Return whether a local-space point lies inside the text bounds.

        :param local_pos: Point to test in local coordinates.
        :return: ``True`` when the point is inside the rendered text rectangle.
        """
        x, y = local_pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a text draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the text.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawText(transform, layer, sub_layer, anchor, self._cache, clip_area, self.text, self.font))


class SubSurfaceRenderer(ObjectRenderer):
    """Renders a cropped region of a texture scaled into fixed target dimensions."""

    def __init__(self, texture: Texture, sub_rect: Rect, target_dims: vec2, cache=True) -> None:
        """Initialize the sub-surface renderer.

        :param texture: Source texture that contains the cropped region.
        :param sub_rect: Rectangle in the source texture to render.
        :param target_dims: Local dimensions of the rendered view.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        self._texture = texture
        self._sub_rect = Rect(sub_rect)
        self._target_dims = target_dims
    
    # region PROPERTIES
    @property
    def texture(self):
        """Return the source texture."""
        return self._texture
    
    @property
    def sub_rect(self):
        """Return the source rectangle being rendered."""
        return self._sub_rect
    
    @sub_rect.setter
    def sub_rect(self, value):
        """
        Set the source rectangle being rendered.

        :param value: The new source rectangle being rendered.
        """
        self._sub_rect = Rect(value)
    
    @property
    def target_dims(self):
        """Return the target view dimensions."""
        return self._target_dims
    
    @target_dims.setter
    def target_dims(self, value: vec2):
        """
        Set the target view dimensions.

        :param value: The new target view dimensions.
        """
        self._target_dims = value
    
    @property
    def dims(self):
        """Return the target view dimensions."""
        return self._target_dims
    
    @property
    def width(self):
        """Return the target view width."""
        return self._target_dims.x
    
    @width.setter
    def width(self, value: int):
        """
        Set the target view width.

        :param value: The new target view width.
        """
        self._target_dims.x = value
    
    @property
    def height(self):
        """Return the target view height."""
        return self._target_dims.y
    
    @height.setter
    def height(self, value: int):
        """
        Set the target view height.

        :param value: The new target view height.
        """
        self._target_dims.y = value
    # endregion
    
    def get_aabb_size(self, rotation: float):
        """Return the fixed target size rather than the cropped texture bounds.

        :param rotation: Rotation in degrees applied to the rendered region.
        :return: The target view dimensions.
        """
        # Returns the fixed target size (like the screen size) instead of the bounding box of the cropped texture
        return self._target_dims
    
    def test_hit(self, local_pos: vec2):
        """Return whether a local-space point hits a non-transparent source texel.

        :param local_pos: Point to test in local view coordinates.
        :return: ``True`` when the mapped source texel exists and has non-zero alpha.
        """
        x, y = local_pos
        # Fast initial check against our screen canvas boundaries
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        # 1. Reverse the scaling ratio to go from screen canvas coordinates back to sub_rect coordinates
        x_ratio = self._sub_rect.w / self.width
        y_ratio = self._sub_rect.h / self.height
        
        # 2. Check where the click landed inside our sub_rect window
        sub_x = x * x_ratio
        sub_y = y * y_ratio
        
        # 3. Calculate absolute position on the root texture
        orig_x = int(self._sub_rect.x + sub_x)
        orig_y = int(self._sub_rect.y + sub_y)
        
        # 4. Grab bounds of the master texture
        texture_rect = self.texture.surface.get_rect()
        
        # 5. If the hit position lands inside the raw texture boundaries, check alpha transparency
        if texture_rect.collidepoint(orig_x, orig_y):
            return self.texture.get_at_pos(vec2(orig_x, orig_y)).a > 0
        
        # Click was in the out-of-bounds transparent gutter area
        return False
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a sub-surface draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the rendered region.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawSubSurface(
            transform, layer, sub_layer, anchor, self._cache, clip_area, self.texture, self.sub_rect, self.target_dims
        ))


class ChunkedSpriteRenderer(ObjectRenderer):
    """Renders a texture in chunks so only visible regions are processed."""

    def __init__(self, texture: Texture, chunk_size: int = 256, cache=True) -> None:
        """Initialize the chunked sprite renderer.

        :param texture: Texture drawn by this renderer.
        :param chunk_size: Size in pixels of each square texture chunk.
        :param cache: Whether draw commands may use the shared surface cache.
        """
        super().__init__(cache)
        self._texture = texture
        self._chunk_size = chunk_size
    
    # region PROPERTIES
    @property
    def texture(self):
        """Return the texture drawn by this renderer."""
        return self._texture
    
    @property
    def chunk_size(self):
        """Return the size of each texture chunk."""
        return self._chunk_size
    
    @chunk_size.setter
    def chunk_size(self, value: int) -> None:
        """
        Set the chunk size, clamped to at least one pixel.

        :param value: The new value.
        """
        self._chunk_size = max(1, value)
    
    # region dims
    @property
    def dims(self):
        """Return the texture dimensions."""
        return self.texture.dims
    
    @property
    def width(self):
        """Return the texture width."""
        return self.texture.width
    
    @property
    def height(self):
        """Return the texture height."""
        return self.texture.height
    # endregion
    # endregion
    
    def get_aabb_size(self, rotation: float):
        """Return the axis-aligned bounding box size for the given rotation.

        :param rotation: Rotation in degrees applied to the sprite.
        :return: The axis-aligned bounding box size in local units.
        """
        return vec2(length(self.dims)) if rotation else self.dims
    
    def test_hit(self, local_pos: vec2):
        """Return whether a local-space point hits a non-transparent texel.

        :param local_pos: Point to test in local coordinates.
        :return: ``True`` when the point is inside the texture and its alpha is non-zero.
        """
        x, y = local_pos
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        return self.texture.get_at_pos(local_pos).a > 0
    
    def render(self, submit, transform: Transform, layer: Layer, sub_layer: int, anchor: vec2, clip_area: Optional[FRect] = None):
        """Submit a chunked sprite draw command for this renderer.

        :param submit: Callback that queues a draw command.
        :param transform: World transform supplied by the owning object.
        :param layer: Layer used to resolve camera and screen coordinates.
        :param sub_layer: Sub-layer index used for draw ordering.
        :param anchor: UV anchor point for the sprite.
        :param clip_area: Optional world-space rectangle used to clip drawing.
        """
        submit(DrawChunkedSprite(transform, layer, sub_layer, anchor, self._cache, clip_area, self.texture, self.chunk_size))