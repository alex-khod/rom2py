import pyglet
import os
import random

from ..tilemap import TileMap
from src.resources import Resources

from pyglet.gl import *

jn = os.path.join
import numpy as np

MAP_PADDING = 8
TILE_SIZE = 32
WHITE = (255, 255, 255)
GRAY = (20, 25, 25)
BLACK = (0, 0, 0)


class TerrainShaderRenderer:

    def __init__(self, alm):
        self.alm = alm
        self.tilemap = TileMap()

        batch = pyglet.graphics.Batch()

        def water_tile_anim(terrain_start):
            TERRAIN_WIDTH_PER_ID = 16
            TERRAIN_FRAMES = 4
            frames = []
            for frameid in range(TERRAIN_FRAMES):
                next_frame_id = terrain_start + (column_id + frameid * TERRAIN_FRAMES) % TERRAIN_WIDTH_PER_ID
                frame = self.tiles[next_frame_id][row_id]
                frame = pyglet.image.AnimationFrame(frame, 16 / 60)
                frames.append(frame)
            return pyglet.image.Animation(frames)

        from src.shaders import get_terrain_shader

        program = get_terrain_shader()
        program.uniforms["map_size"].set((alm.width, alm.height))
        group = pyglet.graphics.ShaderGroup(program)
        batch = pyglet.graphics.Batch()
        tot = alm.width * alm.height
        tileids = tuple(x.tile_id for x in alm["tiles"].body.tiles)
        tilenos = tuple(range(tot))
        hate_map_flat = [height for i in range(alm.width * alm.height)
                         for height in alm.tile_corner_heights_at(i % alm.width, i // alm.width)]
        program.vertex_list(tot, GL_POINTS, tile_id=("i", tileids), tile_no=("i", tilenos),
                            hate_map=("i", hate_map_flat),
                            group=group, batch=batch)
        self.batch = batch

    def draw(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.tilemap.texture.target, self.tilemap.texture.id)
        self.batch.draw()
