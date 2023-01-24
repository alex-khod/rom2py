# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RageOfMages1Bmp(KaitaiStruct):
    """This format is just a subtype of a typical bmp file format used in ROM
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.read_bytes(2)
        if not self.magic == b"\x42\x4D":
            raise kaitaistruct.ValidationNotEqualError(b"\x42\x4D", self.magic, self._io, u"/seq/0")
        self.unused0 = self._io.read_u4le()
        self.unused1 = self._io.read_u4le()
        self.bfh_pixeldata = self._io.read_u4le()
        self.bi_version = self._io.read_u4le()
        if  ((self.bi_version != 12) and (self.bi_version == 40)) :
            self.data = RageOfMages1Bmp.BmpData(self._io, self, self._root)


    class BmpData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()
            self.bi_planes_unused = self._io.read_u2le()
            self.bi_bitcount = self._io.read_u2le()
            self.bi_compression_unused = self._io.read_u4le()
            self.bi_sizeimage_unused = self._io.read_u4le()
            self.bi_xpelspermeter_unused = self._io.read_u4le()
            self.bi_ypelspermeter_unused = self._io.read_u4le()
            self.bi_clrused_unused = self._io.read_u4le()
            self.bi_clrimportant_unused = self._io.read_u4le()
            if self.bi_bitcount == 8:
                self.palette = [None] * (256)
                for i in range(256):
                    self.palette[i] = self._io.read_u4le()



        @property
        def pixels_data(self):
            if hasattr(self, '_m_pixels_data'):
                return self._m_pixels_data if hasattr(self, '_m_pixels_data') else None

            io = self._root._io
            _pos = io.pos()
            io.seek(self._root.bfh_pixeldata)
            self._m_pixels_data = io.read_bytes(((self.width * self.height) * self.bi_bitcount) // 8)
            io.seek(_pos)
            return self._m_pixels_data if hasattr(self, '_m_pixels_data') else None



