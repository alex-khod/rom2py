import pyglet

from ..formats.alm2 import TILE_SIZE, Alm2


class Terrain:

    def __init__(self, alm: "Alm2"):
        self.alm = alm
        self.grid = [[0 * alm.width] for _ in range(alm.height)]

