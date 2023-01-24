# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RageOfMages1256(KaitaiStruct):
    """This format contains opaque strips of paletted pixels(256 colors)
    Uses Run Length Encoding To pack transparent areas of a sprite
    As a result we have a decent small sprites which can be rendered very
    effectively.
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        if self.has_palette != 0:
            self.inner_palette = self._io.read_bytes((256 * 4))

        self.sprite_records = [None] * (self.sprite_count)
        for i in range(self.sprite_count):
            self.sprite_records[i] = RageOfMages1256.SpriteRecord(self._io, self, self._root)


    class SpriteRecord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            self.data = self._io.read_bytes(self.data_size)


    @property
    def sprite_count_internal(self):
        if hasattr(self, '_m_sprite_count_internal'):
            return self._m_sprite_count_internal if hasattr(self, '_m_sprite_count_internal') else None

        _pos = self._io.pos()
        self._io.seek((self._io.size() - 4))
        self._m_sprite_count_internal = self._io.read_u4le()
        self._io.seek(_pos)
        return self._m_sprite_count_internal if hasattr(self, '_m_sprite_count_internal') else None

    @property
    def sprite_count(self):
        if hasattr(self, '_m_sprite_count'):
            return self._m_sprite_count if hasattr(self, '_m_sprite_count') else None

        self._m_sprite_count = (self.sprite_count_internal & 2147483647)
        return self._m_sprite_count if hasattr(self, '_m_sprite_count') else None

    @property
    def has_palette(self):
        if hasattr(self, '_m_has_palette'):
            return self._m_has_palette if hasattr(self, '_m_has_palette') else None

        self._m_has_palette = (self.sprite_count_internal & 2147483648)
        return self._m_has_palette if hasattr(self, '_m_has_palette') else None


