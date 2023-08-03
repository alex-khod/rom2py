import pyglet

from src.formats.alm2 import TILE_SIZE
import math

from src.terrain.renderers.shader import TerrainShaderRenderer
from src.utils import file_cache


def calc_light_map(alm):
    w, h = alm.width, alm.height
    solar_angle = alm.general.negative_sun_angle
    solar_angle_radians = solar_angle * (math.pi / 180.0)
    sunx = math.cos(solar_angle_radians)
    suny = math.sin(solar_angle_radians)
    sunz = -0.75
    heights = alm.heights

    light_map_w = 2 ** math.ceil(math.log2(w))
    light_map_h = 2 ** math.ceil(math.log2(h))

    # @file_cache("lightmap.bin")
    def light_map_manual():
        # lighting of a tile is dot(tile_normal, sun_vec) * 64 + 96
        light_map = [[0] * light_map_w for _ in range(light_map_h)]
        for x in range(1, w-1):
            for y in range(1, h-1):
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
                # light_map[y][x] = 96
        return tuple(map(tuple, light_map))

    return light_map_manual()


class TerrainGraphics:

    def __init__(self, alm):
        self.alm = alm
        self.renderer = TerrainShaderRenderer(alm)
        self.light_map = calc_light_map(alm)
        # pad each row with zeros to get POT image
        h, w = len(self.light_map), len(self.light_map[0])
        light_map_tex_data = b''.join([bytes(row) for row in self.light_map])
        light_map_tex = pyglet.image.ImageData(w, h, "R", light_map_tex_data)
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
        self.renderer.draw()
        self.draw_origin()
