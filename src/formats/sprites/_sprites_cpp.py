from .base import ROM256, ROM256Frame, ROM16A, ROM16AFrame
import numpy as np


def lazy_load_dll():
    # injected in src.resources.setup_sprites()
    raise Exception("Not initialized")

class ROM256FrameCpp(ROM256Frame):

    def to_color_indexes(self):
        _dll = lazy_load_dll()
        data = self._sprite.data
        data_size = self._sprite.data_size
        w, h = self.width, self.height
        output = bytes(w * h)
        _dll.ROM256_to_color_indexes(data, output, data_size, w, h)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w)
        # if self._x_flip:
        #     output = self.do_x_flip(output)
        # if self._canvas_size:
        #     return self.blit_to_canvas(output)
        # free_dll()
        return output


class ROM256Cpp(ROM256):
    _frame_class = ROM256FrameCpp

class ROM16AFrameCpp(ROM16AFrame):

    def to_color_indexes(self):
        _dll = lazy_load_dll()

        w, h = self.width, self.height
        data = self._sprite.data
        data_size = self._sprite.data_size
        output = bytes(w * h * 2)
        _dll.ROM16A_to_color_indexes(data, output, data_size, w, h)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w, 2)
        if self._x_flip:
            output = self.do_x_flip(output)
        if self._canvas_size:
            return self.blit_to_canvas(output)
        # free_dll()
        return output


class ROM16ACpp(ROM16A):
    _frame_class = ROM16AFrameCpp
