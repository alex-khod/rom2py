from .base import A256, A256Frame
import numba
import numpy as np


@numba.njit
def to_colors(data, output, data_size, w, h, x0, y0, x_flip=False):
    # if not self._cache is None:
    #     return self._cache
    x, y = 0, 0
    offset = 0
    while offset < data_size:
        char = data[offset]
        val, code = char & 0x3f, char & 0xc0
        offset += 1
        if (code > 0):
            # skip transparent bytes
            if (code == 0x40):
                y += val
            else:
                x += val
        else:
            for j in range(val):
                y += x // w
                x = x % w
                idx = data[offset]
                target_x = w - 1 - x0 - x if x_flip else x0 + x
                output[y0 + y][target_x] = idx
                offset += 1
                x += 1


class A256FrameNumba(A256Frame):

    def to_colors(self):
        w, h = self.width, self.height
        data = self._sprite.data
        data_size = self._sprite.data_size
        output = np.zeros((h, w), dtype='uint8')
        to_colors(data, output, data_size, w, h, self.x0, self.y0, self._x_flip)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w)
        return output


class A256Numba(A256):
    _record_class = A256FrameNumba
