import io
import struct
import numpy as np
from src.formats.autogenerated.rage_of_mages_1_256 import RageOfMages1256
from PIL import Image as PILImage
from pyglet.image import ImageData

TILE_SIZE = 32


def texture_to_pil_image(texture):
    data = texture.get_image_data().get_data()
    w, h = texture.length, texture.height
    image = PILImage.frombytes('RGBA', (w, h), data)
    return image


class ROM256Frame:
    _x_flip = 0
    _cache = None

    def __init__(self, parent, sprite, _canvas_size=None, cache=None):
        self._parent = parent
        self._sprite = sprite
        self._cache = cache
        self._canvas_size = _canvas_size

        self.width = self._sprite.width
        self.height = self._sprite.height

    def set_x_flip(self, x_flip):
        self._x_flip = x_flip
        return self

    @staticmethod
    def do_x_flip(output):
        output[:, :] = output[:, ::-1]
        return output

    def blit_to_canvas(self, output):
        cw, ch = self._canvas_size
        shape = output.shape
        h, w = shape[:3]
        cw = max(cw, w)
        ch = max(ch, h)
        canvas_shape = (cw, ch) + shape[3:]
        canvas = np.zeros(canvas_shape, dtype="uint8")
        x0 = (cw - w) // 2
        y0 = (ch - h) // 2
        canvas[y0:y0 + h, x0:x0 + w] = output
        return canvas

    def to_color_indexes(self):
        sprite = self._sprite
        data = sprite.data
        data_size = sprite.data_size

        w, h = self.width, self.height
        output = np.zeros((h, w), dtype='uint8')

        x, y = 0, 0
        offset = 0
        while offset < data_size:
            _byte = data[offset]
            val, code = _byte & 0x3f, _byte & 0xc0
            offset += 1
            if code > 0:
                # skip transparent bytes
                if code == 0x40:
                    y += val
                else:
                    x += val
                continue

            for _ in range(val):
                y += x // w
                x = x % w
                idx = data[offset]
                # check if there is non-zero data byte. if there is at least one, there will be errors on paletting..
                # assert idx > 0
                output[y][x] = idx
                offset += 1
                x += 1

        if self._x_flip:
            output = self.do_x_flip(output)
        if self._canvas_size:
            return self.blit_to_canvas(output)
        return output

    def to_rgba(self, palette=None):
        palette = palette or self._parent.palette
        palette = np.array(palette.colors, dtype="uint8")
        idxs = self.to_color_indexes()
        return palette[idxs]

    def to_rgba_image_data(self, palette=None):
        rgba = self.to_rgba(palette)
        h, w, _ = rgba.shape
        data = rgba.tobytes()
        data = ImageData(w, h, "RGBA", data)
        return data

    def to_r_image_data(self):
        idxs = self.to_color_indexes()
        # h, w = idxs.shape
        h, w = len(idxs), len(idxs[0])
        # data = idxs.tobytes()
        data = b''.join([bytes(row) for row in idxs])
        data = ImageData(w, h, "R", data)
        return data

    def to_pil_image(self, palette=None):
        return PILImage.fromarray(self.to_rgba(palette))


class ROM256(RageOfMages1256):
    _palette = None
    _canvas_size = None
    _cache = None
    _frame_class = ROM256Frame

    def __getitem__(self, keys):
        if not self._cache:
            self._cache = [None] * self.count
        if type(keys) is slice:
            return [self._frame_class(self, self.sprite_records[idx], self._canvas_size, self._cache[idx]) for idx in
                    range(*keys.indices(self.count))]
        idx = keys
        return self._frame_class(self, self.sprite_records[idx], self._canvas_size, self._cache[idx])

    def set_canvas_size(self, canvas_size):
        self._canvas_size = canvas_size
        return self

    @property
    def count(self):
        return len(self.sprite_records)

    def __len__(self):
        return self.count

    @property
    def palette(self):
        if self._palette is None:
            self._palette = self.load_inner_palette()
        return self._palette

    def load_inner_palette(self):
        return Palette.data_to_palette(self.inner_palette)

    def to_tiles(self, tile_width: int, tile_height: int, offset: int = 0):
        """
            Interpret frames at :offset as parts of tiled picture with dimensions :tile_width x :tile_height.
            :return RGBA array
        """
        tw, th = tile_width, tile_height
        frames = self[offset:offset + (tw * th)]
        output = np.zeros((32 * th, 32 * tw, 4), dtype='uint8')
        for j in range(th):
            for i in range(tw):
                rgba = frames[j * tw + i].to_rgba()
                # place 32x32 tile to its
                output[j * 32:(j + 1) * 32, i * 32:(i + 1) * 32] = rgba
        return output

    def __repr__(self):
        return f"{self.count}-frame {self.__class__}"


class ROM16AFrame(ROM256Frame):

    def to_color_indexes(self):
        sprite = self._sprite
        data = sprite.data
        data_size = sprite.data_size
        w, h = self.width, self.height
        colors = np.zeros((h, w, 2), dtype='uint8')
        x, y = 0, 0
        offset = 0
        while offset < data_size:
            val, code = data[offset:offset + 2]
            offset += 2
            if code > 0:
                # skip transparent bytes
                if code == 0x40:
                    y += val
                else:
                    x += val
                continue

            for _ in range(val):
                y += x // w
                x = x % w
                raw = data[offset] + (data[offset + 1] << 8)
                idx = (raw >> 1) & 0xFF
                alpha = ((raw >> 9) & 0b1111) * 0x11
                colors[y][x] = (idx, alpha)
                offset += 2
                x += 1
        return colors

    def to_rgba(self, palette=None):
        palette = palette or self._parent.palette
        palette = np.array(palette.colors, dtype="uint8")
        # transform to  RGB
        palette = palette[:, :3]
        idxs_alpha = self.to_color_indexes()
        idxs = idxs_alpha[:, :, 0]
        alpha = idxs_alpha[:, :, 1]
        rgb = palette[idxs]
        # append alpha channel to colors
        rgba = np.dstack((rgb, alpha))
        return rgba

    def to_rg_image_data(self):
        idxs_alpha = self.to_color_indexes()
        h, w, _ = idxs_alpha.shape
        data = idxs_alpha.tobytes()
        data = ImageData(w, h, "RG", data)
        return data


class ROM16A(ROM256):
    _frame_class = ROM16AFrame


class Palette:
    data_offset = 0x36
    colors_size = 256
    bytes_size = colors_size * len("RGBA")

    def __init__(self, colors):
        self.colors = colors

    def to_rgb_image_data(self):
        colors = sum([list(color[:3]) for color in self.colors], [])
        data = ImageData(self.colors_size, 1, "RGB", bytes(colors))
        return data

    @classmethod
    def data_to_palette(cls, buffer, format="RGB"):
        colors = [[0, 0, 0, 0] for _ in range(cls.colors_size)]
        for idx in range(cls.colors_size):
            colors[idx] = tuple(buffer[idx * 4:idx * 4 + 3][::-1] + b'\xFF')
        colors[0] = (0, 0, 0, 0)
        palette = Palette(colors)
        return palette

    @classmethod
    def from_file(cls, fn: str):
        with open(fn, 'rb') as f:
            buffer = f.read(cls.data_offset + cls.bytes_size)
            data = cls.from_bytes(buffer)
            return cls.data_to_palette(buffer)

    @classmethod
    def from_bytes(cls, buffer):
        data = buffer[cls.data_offset:cls.data_offset + cls.bytes_size]
        return cls.data_to_palette(data)

    @classmethod
    def from_random(cls):
        buffer = np.random.randint(0, 255, size=cls.data_offset + cls.bytes_size, dtype="uint8").tobytes()
        return cls.from_bytes(buffer)

    def to_pil_image(self):
        array = np.array(self.colors, dtype='uint8').reshape(16, 16, 4)
        return PILImage.fromarray(array).resize((256, 256), resample=PILImage.Resampling.NEAREST)


class BmpHandler:

    def __init__(self, image):
        self.image = image

    def get_image_data(self):
        image = self.image
        _bytes = self.image.tobytes()
        return ImageData(image.width, image.height, image.mode, data=_bytes, pitch=-len(image.mode)*image.width)

    @classmethod
    def from_file(cls, path):
        return cls(PILImage.open(path))

    @classmethod
    def from_bytes(cls, data):
        bytesio = io.BytesIO(data)
        return cls(PILImage.open(bytesio))


__all__ = ["ROM256", "ROM256Frame", "ROM16A", "ROM16AFrame", "Palette", "BmpHandler"]
# ehh why not?
__all__ += ["np", "PILImage"]
