import pyglet

MAP_PADDING = 8
TILE_SIZE = 32
import numpy as np
from src.resources import Resources

class TileMap:
    """
        Class for loading ROM2 tilemap onto texture and allowing tile-by-tile access of the texture.
    """

    def __getitem__(self, column_id):
        return self.tiles[column_id]

    def __init__(self):
        self.column_order = None
        self.columns = None
        self.texture = None
        self.tiles = None

        self.load_columns()
        self.blit_tiles_to_texture()

    def load_columns(self):
        column_list = Resources["graphics", "terrain"]
        self.column_order = [x.record.name for x in column_list]
        columns = [x.record.content for x in column_list]
        # columns = [extrude_column(x, 0) for x in columns]
        # add brightness
        # columns = [x + 8 for x in columns]
        columns = [np.array(x.convert("RGB")) for x in columns]
        columns = [[x.shape[1], x.shape[0], x.tobytes()] for x in columns]
        columns = [pyglet.image.ImageData(width=x[0], height=x[1], fmt="RGB", data=x[2]) for x in columns]
        self.columns = columns

    def blit_tiles_to_texture(self):
        columns = self.columns
        border = 0
        bordered_ts = TILE_SIZE + border * 2
        # tex_w, tex_h = len(columns) * bordered_ts, max([x.height for x in columns])
        self.texture = pyglet.image.Texture.create(2048, 2048)
        self.tiles = []
        for i, column in enumerate(columns):
            column_tiles = []
            self.texture.blit_into(column, bordered_ts * i, 0, 0)
            for j in range(column.height // bordered_ts):
                tile_tex = self.texture.get_region(x=border + i * bordered_ts,
                                                   y=border + j * bordered_ts,
                                                   width=TILE_SIZE,
                                                   height=TILE_SIZE)
                column_tiles.append(tile_tex)
            self.tiles.append(column_tiles)

def extrude_column(column, border=1):
    """
        Take PILImage :column with (height=*, width=TILE_SIZE) and
        extrude it's border pixels by :border in four directions.
        :return mumpy array.
    """

    b, ts = border, TILE_SIZE
    tsb, w = ts + b, ts + b * 2

    arr = np.array(column.convert("RGB"))
    h = arr.shape[0]
    column_buffer = np.zeros((w * h // ts, w, 3), dtype='uint8')
    buffer = np.zeros((w, w, 3), dtype='uint8')
    for j in range(h // TILE_SIZE):
        buffer[b:tsb, b:tsb] = arr[j * ts:(j + 1) * ts]
        buffer[0:b, b:tsb] = arr[j * ts:j * ts + 1]
        buffer[tsb:w, b:tsb] = arr[(j + 1) * ts - 1:(j + 1) * ts]
        buffer[b:tsb, 0:b] = arr[j * ts:(j + 1) * ts, 0:1]
        buffer[b:tsb, tsb:w] = arr[j * ts:(j + 1) * ts, ts - 1:ts]

        column_buffer[j * w:(j + 1) * w] = buffer
    return column_buffer