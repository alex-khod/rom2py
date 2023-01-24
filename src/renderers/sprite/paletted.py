import pyglet
import os
from src.shaders import get_sprite_shader
from pyglet.gl import *
from src.textures import TextureAtlas, TextureBin, Texture

jn = os.path.join
import numpy as np

MAP_PADDING = 8
TILE_SIZE = 32


class PalettedSpriteRenderer:

    def __init__(self, batch=None):
        self.batch = batch or pyglet.graphics.Batch()
        self.atlases = {}

        self.palette_atlas = TextureAtlas(2048, 2048)
        self.palettes = {}
        self.sprites = []
        self._first_image = None

        self.mem_usage_total = 0
        self.mem_usage_real = 0

        def texture_factory(width, height):
            self.mem_usage_total += width * height
            tex = Texture.create(width, height, internalformat=1, fmt=GL_RED)
            return tex

        def atlas_factory(width, height):
            return TextureAtlas(width, height, texture_factory=texture_factory)

        self.atlas = TextureBin(atlas_factory=atlas_factory)
        # self.atlas = TextureAtlas(4096 * 10, 4096 * 10, texture_factory=texture_factory)
        # self.mem_usage_total += self.atlas.texture.width * self.atlas.texture.height

    def a256_to_frames(self, a256, record, sprite_key):
        frames = []
        w, h = record["width"], record["height"]
        cx, cy = record["centerx"], record["centery"]
        atlas = self.atlas
        for image in a256:
            image = image.to_r_image_data()
            if not self._first_image:
                self._first_image = image

            self.mem_usage_real += image.width * image.height

            # blit to atlas texture and get reference to blitted region
            image = atlas.add(image)
            # anchor should be set after blitting to atlas
            image.anchor_x = cx + (-w + image.width) // 2
            image.anchor_y = cy + (-h + image.height) // 2
            frames.append(image)
        return frames

    def prepare_palette(self, palette, palette_key):
        palette_data = palette.to_rgb_image_data()
        self.palettes[palette_key] = self.palette_atlas.add(palette_data)

    def add_sprite(self, animation, x, y, palette_key):
        # tile_heights = alm.heights_for_tile(tile_x, tile_y)
        # avg_height = sum(tile_heights) / 4
        avg_height = 0
        palette_tex = self.palettes[palette_key]
        sprite = PalettedSprite(animation, x, y, 0, batch=self.batch, palette_tex=palette_tex)
        sprite.palette = palette_tex
        self.sprites.append(sprite)
        return sprite

    def draw(self):
        glClearColor(255, 255, 255, 255)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(self.palette_atlas.texture.target, self.palette_atlas.texture.id)
        self.batch.draw()
        # self._first_image.blit(0, 0)
        # self.atlas.texture.blit(0, 512)
        # self.palette_atlas.texture.blit(0,0)


class PalettedSprite(pyglet.sprite.Sprite):
    _palette_tex = None

    def __init__(self, *args, **kwargs):
        self._palette_tex = kwargs.pop("palette_tex")
        super().__init__(*args, **kwargs)

    @property
    def program(self):
        program = get_sprite_shader()
        return program

    def _create_vertex_list(self):
        if not self._palette_tex:
            return
        self._vertex_list = self.program.vertex_list_indexed(
            4, GL_TRIANGLES, [0, 1, 2, 0, 2, 3], self._batch, self._group,
            translate=('f', (self._x, self._y, self._z) * 4),
            tex_coords=('f', self._texture.tex_coords),
            pal_coords=('f', self._palette_tex.tex_coords[:3] * 4),
        )
        self._update_position()

    def _animate(self, dt):
        super()._animate(dt)
        # change geometry because frames can have different geometry
        self._update_position()

    def _update_position(self):
        if not self._visible:
            self._vertex_list.position[:] = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        else:
            img = self._texture
            x1 = -img.anchor_x
            y1 = -img.anchor_y
            x2 = x1 + img.width
            y2 = y1 + img.height
            vertices = (x1, y1, x2, y1, x2, y2, x1, y2)

            if not self._subpixel:
                self._vertex_list.position[:] = tuple(map(int, vertices))
            else:
                self._vertex_list.position[:] = vertices


class SpriteGroup(pyglet.sprite.SpriteGroup):

    def __init__(self, texture, blend_src, blend_dest, program, order=0, parent=None):
        super().__init__(order, parent)
        self.texture = texture
        self.blend_src = blend_src
        self.blend_dest = blend_dest
        self.program = program

    def set_state(self):
        self.program.use()

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(self.texture.target, self.texture.id)

        glEnable(GL_BLEND)
        glBlendFunc(self.blend_src, self.blend_dest)

    def unset_state(self):
        glDisable(GL_BLEND)
        self.program.stop()
