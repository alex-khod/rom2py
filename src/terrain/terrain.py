# from .renderers.base import TerrainSpriteRenderer as Renderer
from profilehooks import timecall

from src.utils import file_cache
from .renderers.shader import TerrainShaderRenderer as Renderer
import pyglet

TILE_SIZE = 32


def calc_light_map(alm):
    # light map is light value of each tile
    # TODO move to shader
    import math
    import numpy as np
    w, h = alm.width, alm.height
    solar_angle = alm.general.negative_sun_angle
    solar_angle_radians = solar_angle * (math.pi / 180.0)
    sunx = math.cos(solar_angle_radians)
    suny = math.sin(solar_angle_radians)
    sunz = -0.75
    heights = alm.heights

    def light_map_numpy():
        # lighting of a tile is dot(tile_normal, sun_vec) * 64 + 96
        light_map = np.zeros((w, h), dtype="uint8")
        sun_vec = np.array([sunx, suny, sunz])
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                dh_right = heights[y][x] - heights[y][x + 1]
                dh_bottom = heights[y][x] - heights[y + 1][x]
                # normal to tile surface is calculated as cross product of its two non-parallel edges
                # edge from (x, y) to (x+1,y)
                vec1 = np.array([32, 0, dh_right])
                # edge from (x, y) to (x,y+1)
                vec2 = np.array([0, 32, dh_bottom])
                normal = np.cross(vec1, vec2)
                normal = normal / np.linalg.norm(normal)
                dot = np.dot(normal, sun_vec)
                lighting = abs(dot) * 64 + 96
                light_map[y, x] = lighting
        return light_map

    @file_cache("lightmap.bin")
    def light_map_manual():
        # lighting of a tile is dot(tile_normal, sun_vec) * 64 + 96
        light_map = [[0] * w for _ in range(h)]
        for x in range(1, w - 1):
            for y in range(1, h - 1):
                dh_right = heights[y][x] - heights[y][x + 1]
                dh_bottom = heights[y][x] - heights[y + 1][x]

                # normal to tile surface is calculated as cross product of its two non-parallel edges
                # cross product values are almost constant in case of tiles
                cx = dh_right
                cy = dh_bottom
                cz = TILE_SIZE

                # normalize cross product (cx, cy, cz)
                modulus = math.sqrt((cx * cx) + (cy * cy) + (cz * cz))
                cx /= modulus
                cy /= modulus
                cz /= modulus

                dot_magnitude = abs(cx * sunx + cy * suny + cz * sunz)
                light_map[y][x] = int(dot_magnitude * 64 + 96)
        return tuple(map(tuple, light_map))

    return light_map_manual()


class Terrain:

    @timecall
    def __init__(self, alm):
        self.alm = alm
        self.renderer = Renderer(alm)

        self.light_map = calc_light_map(alm)
        # TODO the texture should be POT
        light_map_tex = b''.join([bytes(row) for row in self.light_map])
        light_map_tex = pyglet.image.ImageData(256, 256, "R", light_map_tex)
        self.renderer.light_map_tex = light_map_tex.get_texture()

    def draw_origin(self):
        alm = self.alm
        WHITE = (255, 255, 255, 255)
        RED = (255, 0, 0, 255)
        colors = WHITE * 4 + RED * 4

        vertices = (0, 0, 0,
                    0, alm.height * TILE_SIZE, 0,
                    0, 0, 0,
                    alm.width * TILE_SIZE, 0, 0,
                    0, alm.height * TILE_SIZE, 0,
                    0, alm.height * TILE_SIZE + 32, 0,
                    alm.width * TILE_SIZE, 0, 0,
                    alm.width * TILE_SIZE + 32, 0, 0)

        pyglet.graphics.draw(8, pyglet.gl.GL_LINES, position=('i', vertices), colors=("f", colors))

    def draw(self):
        self.draw_origin()
        self.renderer.draw()
