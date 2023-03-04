import pyglet
import os
from src.graphics.shaders import get_sprite_shader
from pyglet.gl import *
from src.graphics.textures import TextureAtlas, TextureBin, Texture

jn = os.path.join

MAP_PADDING = 8
TILE_SIZE = 32


class PalettedSpriteRenderer:

    def __init__(self, graphics, batch=None):
        self.batch = batch or pyglet.graphics.Batch()
        self.graphics = graphics
        self.atlases = {}
        self.sprites = []
        self._first_image = None

    def redraw_shadow(self, sprite: 'PalettedSprite'):
        img = sprite._texture
        x1 = -img.anchor_x
        y1 = -img.anchor_y
        x2 = x1 + img.width
        y2 = y1 + img.height

        offset = img.height * 0.3
        offset2 = -offset * (1 - 0.3)
        vertices = (x1 + offset, y1, x2 + offset, y1, x2, y2, x1, y2)

        shadow = sprite.shadow
        shadow._set_texture(img)
        shadow.x = sprite.x
        shadow.y = sprite.y
        shadow._vertex_list.position[:] = vertices

    def add_sprite(self, x, y, animation, palette):
        shadow = PalettedSprite(animation, x, y, 0, batch=self.batch, palette_tex=palette)
        shadow.color = (0, 0, 0)
        shadow.opacity = 127
        sprite = PalettedSprite(animation, x, y, 0, batch=self.batch, palette_tex=palette)
        sprite.shadow = shadow
        self.redraw_shadow(sprite)
        self.sprites.append(sprite)
        return sprite

    def draw(self):
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(self.graphics.palette_atlas.texture.target, self.graphics.palette_atlas.texture.id)
        self.batch.draw()
        # self._first_image.blit(0, 0)
        # self.atlas.texture.blit(0, 512)
        # self.palette_atlas.texture.blit(0,0)


class PalettedSprite(pyglet.sprite.Sprite):
    _palette_tex = None
    shadow = None

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
        _palette_tex = self._palette_tex[0]
        self._vertex_list = self.program.vertex_list_indexed(
            4, GL_TRIANGLES, [0, 1, 2, 0, 2, 3], self._batch, self._group,
            translate=('f', (self._x, self._y, self._z) * 4),
            tex_coords=('f', self._texture.tex_coords),
            pal_coords=('f', _palette_tex.tex_coords[:3] * 4),
            colors=('Bn', (*self._rgb, int(self._opacity)) * 4),
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
