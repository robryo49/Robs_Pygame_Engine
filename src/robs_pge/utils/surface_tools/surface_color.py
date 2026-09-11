import pygame as pg
import numpy as np

def replace_color(surface, old_color, new_color):
    pixels = pg.surfarray.pixels3d(surface)
    
    mask = np.all(pixels == old_color[:3], axis=2)
    pixels[mask] = new_color[:3]
    
    del pixels