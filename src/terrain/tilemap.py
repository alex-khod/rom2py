import pyglet

MAP_PADDING = 8
TILE_SIZE = 32
import numpy as np
from src.resources import Resources

class TileMap:
    """
        Class for loading ROM2 tilemap onto texture and allowing tile-by-tile access of the texture.
    """

    def __getitem__(self, stripe_id):
        return self.tiles[stripe_id]

    def __init__(self):
        self.stripe_order = None
        self.stripes = None
        self.texture = None
        self.tiles = None

        self.load_stripes()
        self.blit_tiles_to_texture()

    def load_stripes(self):
        terrain_stripe_list = Resources["graphics", "terrain"]
        self.stripe_order = [x.record.name for x in terrain_stripe_list]
        stripes = [x.record.content for x in terrain_stripe_list]
        # stripes = [extrude_stripe(x, 0) for x in stripes]
        # add brightness
        # stripes = [x + 8 for x in stripes]
        stripes = [np.array(x.convert("RGB")) for x in stripes]
        stripes = [[x.shape[1], x.shape[0], x.tobytes()] for x in stripes]
        stripes = [pyglet.image.ImageData(width=x[0], height=x[1], fmt="RGB", data=x[2]) for x in stripes]
        self.stripes = stripes

    def blit_tiles_to_texture(self):
        stripes = self.stripes
        border = 0
        bordered_ts = TILE_SIZE + border * 2
        # tex_w, tex_h = len(stripes) * bordered_ts, max([x.height for x in stripes])
        self.texture = pyglet.image.Texture.create(2048, 2048)
        self.tiles = []
        for i, stripe in enumerate(stripes):
            stripe_tiles = []
            self.texture.blit_into(stripe, bordered_ts * i, 0, 0)
            for j in range(stripe.height // bordered_ts):
                tile_tex = self.texture.get_region(x=border + i * bordered_ts,
                                                   y=border + j * bordered_ts,
                                                   width=TILE_SIZE,
                                                   height=TILE_SIZE)
                stripe_tiles.append(tile_tex)
            self.tiles.append(stripe_tiles)

def extrude_stripe(stripe, border=1):
    """
        Take PILImage :stripe with (height=*, width=TILE_SIZE) and
        extrude it's border pixels by :border in four directions.
        :return mumpy array.
    """

    b, ts = border, TILE_SIZE
    tsb, w = ts + b, ts + b * 2

    arr = np.array(stripe.convert("RGB"))
    h = arr.shape[0]
    stripe_buff = np.zeros((w * h // ts, w, 3), dtype='uint8')
    buff = np.zeros((w, w, 3), dtype='uint8')
    for j in range(h // TILE_SIZE):
        buff[b:tsb, b:tsb] = arr[j * ts:(j + 1) * ts]
        buff[0:b, b:tsb] = arr[j * ts:j * ts + 1]
        buff[tsb:w, b:tsb] = arr[(j + 1) * ts - 1:(j + 1) * ts]
        buff[b:tsb, 0:b] = arr[j * ts:(j + 1) * ts, 0:1]
        buff[b:tsb, tsb:w] = arr[j * ts:(j + 1) * ts, ts - 1:ts]

        stripe_buff[j * w:(j + 1) * w] = buff
    return stripe_buff