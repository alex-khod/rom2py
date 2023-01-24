from .base import ROM256, ROM256Frame
from ._sprites_cy_func import ROM256_to_color_indexes
import numpy as np


class ROM256FrameCython(ROM256Frame):
    def to_color_indexes(self):
        w, h = self.width, self.height
        data = self._sprite.data
        data_size = self._sprite.data_size
        return ROM256_to_color_indexes(data, data_size, w, h)


class ROM256Cython(ROM256):
    _frame_class = ROM256FrameCython
