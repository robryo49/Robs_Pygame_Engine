from glm import vec2


class Anchor:
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
    TL =    vec2(0,     0)
    T =     vec2(0.5,   0)
    TR =    vec2(1,     0)
    L =     vec2(0,     0.5)
    C =     vec2(0.5,   0.5)
    R =     vec2(1,     0.5)
    BL =    vec2(0,     1)
    B =     vec2(0.5,   1)
    BR =    vec2(1,     1)
    
    @staticmethod
    def set_screen_dims(dims: vec2):
        ScreenAnchor.TL =    vec2(0,     0) * dims
        ScreenAnchor.T =     vec2(0.5,   0) * dims
        ScreenAnchor.TR =    vec2(1,     0) * dims
        ScreenAnchor.L =     vec2(0,     0.5) * dims
        ScreenAnchor.C =     vec2(0.5,   0.5) * dims
        ScreenAnchor.R =     vec2(1,     0.5) * dims
        ScreenAnchor.BL =    vec2(0,     1) * dims
        ScreenAnchor.B =     vec2(0.5,   1) * dims
        ScreenAnchor.BR =    vec2(1,     1) * dims