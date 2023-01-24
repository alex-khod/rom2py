from .base import A256, A256Frame
from ._sprites_cy_func import to_colors
import numpy as np


class A256FrameCython(A256Frame):
    def to_colors(self):
        w, h = self.width, self.height
        data = self._sprite.data
        data_size = self._sprite.data_size
        return to_colors(data, data_size, w, h, self.x0, self.y0, self._x_flip)


class A256Cython(A256):
    _record_class = A256FrameCython
