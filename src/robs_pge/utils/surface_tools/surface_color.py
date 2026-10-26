"""Surface pixel color replacement helpers."""

import pygame as pg
import numpy as np

def replace_color(surface, old_color, new_color):
    """Replace every pixel matching an old color with a new color in place.

    :param surface: Surface whose pixels are modified.
    :param old_color: Color to match, using its first three channels.
    :param new_color: Replacement color, using its first three channels.
    """
    pixels = pg.surfarray.pixels3d(surface)
    
    mask = np.all(pixels == old_color[:3], axis=2)
    pixels[mask] = new_color[:3]
    
    del pixels