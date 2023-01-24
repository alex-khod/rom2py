import pyglet.graphics
from profilehooks import timecall

from src.resources import Resources

TILE_SIZE = 32


class Structures:

    def __init__(self, alm, renderer):
        self.alm = alm
        self.registry = Resources.special("structures.reg").content
        self.renderer = renderer
        self.graphics = renderer.graphics
        self.animations = {}
        self.palettes = {}
        self.sprites = []
        self.prepare_structures()
        self.load_structures(alm)

    def prepare_structures(self):
        for sid, str_record in self.registry.structures_by_id.items():
            key = "structures\\" + str_record["filename"] + ".256"
            frames = self.graphics[key.lower()]
            self.animations[sid] = frames
            palette = self.graphics[key.lower() + "inner"]
            self.palettes[sid] = palette

    @timecall
    def load_structures(self, alm):
        for structure in alm["structures"].body.structures:
            sid = structure.type_id
            str_record = self.registry.structures_by_id[sid]

            try:
                animation = self.animations[sid]
                palette = self.palettes[sid]
            except KeyError:
                print(f"No anim for sid {sid}")
                continue

            tw, th, fh = str_record["tilewidth"], str_record["tileheight"], str_record["fullheight"]
            tile_x = structure.x >> 8
            tile_y = structure.y >> 8
            height = alm.heights[tile_y][tile_x]
            x0 = tile_x * TILE_SIZE
            y0 = (tile_y + th - fh) * TILE_SIZE - height
            for j in range(fh):
                for i in range(tw):
                    image = animation[j * tw + i]
                    x = x0 + i * TILE_SIZE
                    y = y0 + j * TILE_SIZE
                    sprite = self.renderer.add_sprite(x, y, animation=image, palette=palette)
            # sprite.animation = animation
            self.sprites.append(sprite)
