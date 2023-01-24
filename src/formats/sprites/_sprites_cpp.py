from .base import A256, A256Frame
from ctypes import *
import os
import numpy as np


# python > cython > numba > test_cpp

class A256FrameCpp(A256Frame):
    _dll = None

    @classmethod
    def load_dll(cls):
        from src.resources import get_resource_at_root
        _dll = CDLL(get_resource_at_root("routines.dll"))
        cls._dll = _dll
        return _dll

    def to_colors(self):
        _dll = self.__class__._dll or self.load_dll()

        w, h = self.width, self.height
        data = self._sprite.data
        data_size = self._sprite.data_size
        output = bytes(w * h)
        _dll.to_colors(data, output, data_size, w, h, self.x0, self.y0, self._x_flip)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w)
        return output


class A256Cpp(A256):
    _record_class = A256FrameCpp
