"""Normalized and screen-scaled anchor point constants."""

from glm import vec2


class Anchor:
    """Anchor points in normalized object-local coordinates."""

    TL =    vec2(0,     0)
    T =     vec2(0.5,   0)
    TR =    vec2(1,     0)
    L =     vec2(0,     0.5)
    C =     vec2(0.5,   0.5)
    R =     vec2(1,     0.5)
    BL =    vec2(0,     1)
    B =     vec2(0.5,   1)
    BR =    vec2(1,     1)


class ScreenAnchor:
    """Anchor points scaled to the current screen dimensions."""

    TL =    vec2(0,     0)
    T =     vec2(0.5,   0)
    TR =    vec2(1,     0)
    L =     vec2(0,     0.5)
    C =     vec2(0.5,   0.5)
    R =     vec2(1,     0.5)
    BL =    vec2(0,     1)
    B =     vec2(0.5,   1)
    BR =    vec2(1,     1)
    
    SCREEN_DIMENSIONS = vec2(1, 1)
    
    @staticmethod
    def set_screen_dims(dims: vec2):
        """Rescale all screen anchors to the given dimensions.

        :param dims: Screen dimensions used to scale the normalized anchor points.
        """
        ScreenAnchor.TL =    vec2(0,     0) * dims
        ScreenAnchor.T =     vec2(0.5,   0) * dims
        ScreenAnchor.TR =    vec2(1,     0) * dims
        ScreenAnchor.L =     vec2(0,     0.5) * dims
        ScreenAnchor.C =     vec2(0.5,   0.5) * dims
        ScreenAnchor.R =     vec2(1,     0.5) * dims
        ScreenAnchor.BL =    vec2(0,     1) * dims
        ScreenAnchor.B =     vec2(0.5,   1) * dims
        ScreenAnchor.BR =    vec2(1,     1) * dims
        
        ScreenAnchor.SCREEN_DIMENSIONS = vec2(1, 1) * dims