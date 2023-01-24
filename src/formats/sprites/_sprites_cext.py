from .base import ROM256, ROM256Frame, ROM16A, ROM16AFrame
import numpy as np
import src._c_extensions.routines as routines


class ROM256FrameCExt(ROM256Frame):

    def to_color_indexes(self):
        data = self._sprite.data
        data_size = self._sprite.data_size
        w, h = self.width, self.height
        output = bytes(w * h)
        routines.ROM256_to_color_indexes(data, output, data_size, w, h)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w)
        if self._x_flip:
            output = self.do_x_flip(output)
        if self._canvas_size:
            return self.blit_to_canvas(output)
        return output


class ROM256CExt(ROM256):
    _frame_class = ROM256FrameCExt


class ROM16AFrameCExt(ROM16AFrame):

    def to_color_indexes(self):
        data = self._sprite.data
        data_size = self._sprite.data_size
        w, h = self.width, self.height
        output = bytes(w * h * 2)
        routines.ROM16A_to_color_indexes(data, output, data_size, w, h)
        output = np.frombuffer(output, dtype="uint8").reshape(h, w, 2)
        if self._x_flip:
            output = self.do_x_flip(output)
        if self._canvas_size:
            return self.blit_to_canvas(output)
        return output


class ROM16ACExt(ROM16A):
    _frame_class = ROM16AFrameCExt
