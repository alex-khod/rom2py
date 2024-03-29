from typing import List, Tuple

import pyglet
import os
from ..tilemap import TileMap
from src.resources import get_resource_at_root

from pyglet.gl import *

from ...formats.alm2 import Alm2

jn = os.path.join

MAP_PADDING = 8


class BlendGroup(pyglet.graphics.Group):
    blend_src = GL_SRC_ALPHA
    blend_dest = GL_ONE_MINUS_SRC_ALPHA
    blur = None

    def set_state(self):
        glBindTexture(self.blur.target, self.blur.id)

        glPushAttrib(GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

    def unset_state(self):
        glPopAttrib()
        print(glGetError())


class Wireframe(pyglet.graphics.Group):
    def set_state(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def unset_state(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


class Clamp(pyglet.graphics.TextureGroup):
    def set_state(self):
        # doesn't help with tile seams.
        # probably would work if each tile was its own texture, not textured tilemap
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        # doesn't help with tile seams. nearest still interpolates pixels
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


from src.utils import Vec2


class TileSprite(pyglet.sprite.Sprite):
    _heights = (0, 0, 0, 0)

    @classmethod
    def from_color(self, color):
        image = pyglet.image.SolidColorImagePattern(color).create_image(32, 32)
        sprite = TileSprite(image)
        return sprite

    @property
    def heights(self):
        return self._heights

    @heights.setter
    def heights(self, heights):
        self._heights = heights
        self._update_position()

    def set_shape_from_tile_xy(self, alm: Alm2, tile_xy: Vec2):
        xy = alm.xy_from_tile_xy(tile_xy)
        heights = alm.tile_corner_heights_at(*tile_xy)
        self.set_shape(xy, heights)

    def set_shape(self, xy: Vec2, heights: List[int]):
        self._x = xy.x
        self._y = xy.y
        self._vertex_list.translate[:] = (self._x, self._y, self._z) * 4

        self.heights = heights
        self._update_position()

    def _update_position(self):
        img = self._texture
        x1 = - img.anchor_x
        y1 = - img.anchor_y
        x2 = x1 + img.width
        y2 = y1 + img.height

        # vertices for 2d quad in order
        # ↖ ↗ ↘ ↙
        # vertices = (x1, y1, x2, y1, x2, y2, x1, y2)
        # vertices = (x1, y1 - h00, x2, y1 - h10, x2, y2 - h11, x1, y2 - h01)

        # pyglet 2.0.0 uses indexed tris for sprites that are sorta quads
        # vertices for "3d quad" in order
        # ↖ ↗ ↘ ↙
        h00, h10, h11, h01 = self._heights
        vertices = (x1, y1 - h00, 0, x2, y1 - h10, 0, x2, y2 - h11, 0, x1, y2 - h01, 0)
        # vertices = (x1, y1, h00, x2, y1, h10, x2, y2, h11, x1, y2, h01)
        self._vertex_list.position[:] = vertices

    def _tc_nudge(self, tc, width):
        """
            Nudge sprite texture coordinates to prevent tile seams.
            Coordinates are passed in XYZ format, ↖ ↗ ↘ ↙ order and need inverse nudges (↘ ↙ ↖ ↗).
            [0,1,2] [3,4,5] [6,7,8] [9,10,11] -> ++0 -+0 --0 +-0
            Thus, + for 0,1,4,9, - for 3,6,7,10
        """

        nudge = 1 / 32 / width
        tc = list(tc)
        for i in range(len(tc)):
            if i in [0, 1, 4, 9]:
                tc[i] += nudge
            elif i in [3, 6, 7, 10]:
                tc[i] -= nudge
        return tuple(tc)

    def _create_vertex_list(self):
        self._vertex_list = self.program.vertex_list_indexed(
            4, GL_TRIANGLES, [0, 1, 2, 0, 2, 3], self._batch, self._group,
            colors=('Bn', (*self._rgb, int(self._opacity)) * 4),
            translate=('f', (self._x, self._y, self._z) * 4),
            scale=('f', (self._scale * self._scale_x, self._scale * self._scale_y) * 4),
            rotation=('f', (self._rotation,) * 4),
            tex_coords=('f', self._tc_nudge(self._texture.tex_coords, self._texture.width)))
        self._update_position()

    def _set_texture(self, texture):
        if texture.id is not self._texture.id:
            self._group = self._group.__class__(texture,
                                                self._group.blend_src,
                                                self._group.blend_dest,
                                                self._group.program,
                                                0,
                                                self._group.parent)
            self._vertex_list.delete()
            self._texture = texture
            self._create_vertex_list()
        else:
            assert texture.width == texture.height, "Texture is not rectangular - nudge will be incorrect"
            assert len(texture.tex_coords) == 12, "Texture coords have some freaky length?"
            self._vertex_list.tex_coords[:] = self._tc_nudge(texture.tex_coords, texture.width)
        self._texture = texture


class TerrainSpriteRenderer:

    def __init__(self, alm):
        self.alm = alm
        self.tilemap = TileMap()

        batch = pyglet.graphics.Batch()
        wf_group = Wireframe()
        blur_path = get_resource_at_root("data", "blur128.png")
        self.blur = pyglet.image.load(blur_path).get_texture()
        blend_group = BlendGroup()
        blend_group.blur = self.blur

        WATER_TILE_START = 32
        TERRAIN_WIDTH_PER_ID = 16
        TERRAIN_FRAMES = 4

        def water_tile_anim(terrain_start):
            frames = []
            for frameid in range(TERRAIN_FRAMES):
                next_frame_id = terrain_start + (column_id + frameid * TERRAIN_FRAMES) % TERRAIN_WIDTH_PER_ID
                frame = self.tilemap[next_frame_id][row_id]
                frame = pyglet.image.AnimationFrame(frame, 16 / 60)
                frames.append(frame)
            return pyglet.image.Animation(frames)

        sprites = []
        for tile_y in range(alm.height):
            for tile_x in range(alm.width):
                column_id, row_id = alm.tilecoords[tile_y][tile_x]
                x1, y1 = tile_x * TILE_SIZE, tile_y * TILE_SIZE

                # pretend a tile is a single frame animation
                animation = self.tilemap[column_id][row_id]

                # animation = water_tile_anim(column_id - column_id % 16)
                if WATER_TILE_START < column_id < WATER_TILE_START + TERRAIN_WIDTH_PER_ID:
                    animation = water_tile_anim(WATER_TILE_START)

                sprite = TileSprite(animation, x=x1, y=y1, batch=batch)
                sprite.heights = alm.tile_corner_heights_at(tile_x=tile_x, tile_y=tile_y)
                sprites.append(sprite)

        self.batch = batch
        self.sprites = sprites

    def draw(self):
        self.batch.draw()
