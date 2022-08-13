import pyglet
from src.textures import TextureBin

MAP_PADDING = 8
TILE_SIZE = 32


class AnimSprite(pyglet.sprite.Sprite):

    def _animate(self, dt):
        super()._animate(dt)
        # change geometry because frames can have different geometry (width, height)
        self._update_position()


class DefaultSpriteRenderer:

    def __init__(self, batch=None):
        self.batch = batch or pyglet.graphics.Batch()
        self.sprites = []
        self.frames = {}
        self.animations = {}
        self.atlas = TextureBin()
        self.mem_usage_real = 0
        self.mem_usage_total = 0

    def a256_to_frames(self, a256, record, sprite_key):
        frames = []
        w, h = record["width"], record["height"]
        cx, cy = record["centerx"], record["centery"]

        for image in a256:
            image = image.to_rgba_image_data()
            self.mem_usage_real += image.width * image.height * 4
            # blit to atlas texture and get reference to blitted region
            image = self.atlas.add(image)
            # anchor should be set after blitting to atlas
            image.anchor_x = cx + (-w + image.width) // 2
            image.anchor_y = cy + (-h + image.height) // 2
            frames.append(image)
        return frames

    def prepare_palette(self, palette, palette_key):
        pass

    def add_sprite(self, animation, x, y, palette_key=None):
        sprite = AnimSprite(animation, x, y, 0, batch=self.batch)
        self.sprites.append(sprite)
        return sprite

    def draw(self):
        self.batch.draw()
