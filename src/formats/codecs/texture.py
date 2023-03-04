from pyglet.gl import *
import PIL.Image

format_dict = {
    GL_RED: ("R", "L"),
    GL_RG: ("RG", "LA")
}

mode_dict = {
    "L": "R",
    "LA": "RG"
}


def get_format_string(internalformat):
    return format_dict[internalformat][0] if internalformat in format_dict else "RGBA"


def get_pil_mode(internalformat):
    return format_dict[internalformat][1] if internalformat in format_dict else "RGBA"


def get_image_format(pil_mode):
    return mode_dict[pil_mode] if pil_mode in mode_dict else "RGBA"


class RawTextureDecoder:
    @classmethod
    def decode(cls, filename=None, file=None):
        if not file:
            file = open(filename, "rb")
        internalformat = int.from_bytes(file.read(4), "little")
        width = int.from_bytes(file.read(4), "little")
        height = int.from_bytes(file.read(4), "little")

        fmt = get_format_string(internalformat)
        _bytes = file.read()
        data = pyglet.image.ImageData(width, height, fmt=fmt, data=_bytes)
        return data.get_texture()


class RawTextureEncoder:
    @classmethod
    def encode(self, texture, filename=None, file=None):
        fmt = get_format_string(texture.internalformat)
        image_data = texture.get_image_data(fmt=fmt, gl_format=texture.fmt)
        data = image_data.get_data()
        _bytes = bytes(data)
        file.write(texture.internalformat.to_bytes(4, "little"))
        file.write(texture.width.to_bytes(4, "little"))
        file.write(texture.height.to_bytes(4, "little"))
        file.write(_bytes)


class PilTextureDecoder:
    @classmethod
    def decode(cls, filename=None, file=None):
        if not file:
            file = open(filename, "rb")
        image = PIL.Image.open(file)
        fmt = get_image_format(image.mode)
        data = image.tobytes()
        imdata = pyglet.image.ImageData(image.width, image.height, fmt=fmt, data=data)
        return imdata.get_texture()


class PilTextureEncoder:
    @classmethod
    def encode(self, texture, filename=None, file=None):
        fmt = get_format_string(texture.internalformat)
        image_data = texture.get_image_data(fmt=fmt, gl_format=texture.fmt)
        data = image_data.get_data()
        mode = get_pil_mode(texture.internalformat)
        image = PIL.Image.frombytes(mode, size=(texture.width, texture.height), data=data)
        image.save(file, format="png")
