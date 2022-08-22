from .base import ROM256, ROM256Frame
import numba
import numpy as np


@numba.njit
def ROM256_to_color_indexes(data, output, data_size, w, h):
    # if not self._cache is None:
    #     return self._cache
    x, y = 0, 0
    offset = 0
    while offset < data_size:
        char = data[offset]
        val, code = char & 0x3f, char & 0xc0
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
            output[y][x] = idx
            offset += 1
            x += 1


class ROM256FrameNumba(ROM256Frame):

    def to_color_indexes(self):
        data = self._sprite.data
        data_size = self._sprite.data_size
        w, h = self.width, self.height
        output = np.zeros((h, w), dtype='uint8')
        ROM256_to_color_indexes(data, output, data_size, w, h)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w)
        return output


class ROM256Numba(ROM256):
    _frame_class = ROM256FrameNumba
