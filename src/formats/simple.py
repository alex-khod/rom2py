import io

import pyglet


class ItemnameBin:
    """
        Load itemname.bin structure from file or buffer.
    """

    @classmethod
    def items_by_id(cls, buffer):
        items_by_id = {}
        idx = 0
        for i in range(0, len(buffer), 2):
            val = (buffer[i + 1] << 8) + buffer[i]
            # val = struct.unpack("<H", buffer)[0]
            items_by_id[val] = idx
            idx += 1
        return items_by_id

    @classmethod
    def from_file(cls, path):
        with open(path, 'rb') as f:
            buffer = f.read()
        return cls.items_by_id(buffer)

    @classmethod
    def from_bytes(cls, bytes):
        return cls.items_by_id(buffer=bytes)


class TextLines:
    """
        Load text file as a list of lines.
    """

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            lines = f.read().splitlines()
        return lines

    @classmethod
    def from_bytes(cls, bytes):
        bytesio = io.BytesIO(bytes)
        reader = io.BufferedReader(bytesio)
        wrapper = io.TextIOWrapper(reader)
        lines = wrapper.read().splitlines()
        return lines


class ShaderSource:
    """
        Load .glsl as text file.
    """

    @classmethod
    def from_file(cls, path):
        with open(path, 'r') as f:
            lines = f.read()
        return lines

    @classmethod
    def from_bytes(cls, bytes):
        bytesio = io.BytesIO(bytes)
        reader = io.BufferedReader(bytesio)
        wrapper = io.TextIOWrapper(reader)
        lines = wrapper.read()
        return lines


class WavHandler:

    @classmethod
    def from_file(cls, path):
        return pyglet.media.load(path)

    @classmethod
    def from_bytes(cls, data):
        bytesio = io.BytesIO(data)
        source = pyglet.media.load("file.wav", bytesio)
        # shouldn't be static for music.res
        media = pyglet.media.StaticSource(source)
        return media
