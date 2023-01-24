# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum

if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception(
        "Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))


class RageOfMages1Res(KaitaiStruct):
    class EResourceRecordType(Enum):
        file = 0
        directory = 1

    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.signature = self._io.read_bytes(4)
        if not self.signature == b"\x26\x59\x41\x31":
            raise kaitaistruct.ValidationNotEqualError(b"\x26\x59\x41\x31", self.signature, self._io, u"/seq/0")
        self.resource_header = RageOfMages1Res.RootResourceHeaderT(self._io, self, self._root)

    class ResourceRecordFile(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"IBM866")

        @property
        def bytes(self):
            if hasattr(self, '_m_bytes'):
                return self._m_bytes if hasattr(self, '_m_bytes') else None

            io = self._root._io
            _pos = io.pos()
            io.seek(self._parent.root_offset)
            self._m_bytes = io.read_bytes(self._parent.root_size)
            io.seek(_pos)
            return self._m_bytes if hasattr(self, '_m_bytes') else None

    class ResourceHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.junk = self._io.read_u4le()
            self.root_offset = self._io.read_u4le()
            self.root_size = self._io.read_u4le()
            self.rec_type = KaitaiStream.resolve_enum(RageOfMages1Res.EResourceRecordType, self._io.read_u4le())
            _on = self.rec_type
            if _on == RageOfMages1Res.EResourceRecordType.file:
                self.record = RageOfMages1Res.ResourceRecordFile(self._io, self, self._root)
            elif _on == RageOfMages1Res.EResourceRecordType.directory:
                self.record = RageOfMages1Res.ResourceRecordDirectory(self._io, self, self._root)

    class RootResourceHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.root_offset = self._io.read_u4le()
            self.root_size = self._io.read_u4le()
            self.record_flags = self._io.read_u4le()
            self.fat_offset = self._io.read_u4le()
            self.fat_size = self._io.read_u4le()

    class ResourceRecordDirectory(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"IBM866")

        @property
        def nodes(self):
            if hasattr(self, '_m_nodes'):
                return self._m_nodes if hasattr(self, '_m_nodes') else None

            io = self._root._io
            _pos = io.pos()
            io.seek((self._root.resource_header.fat_offset + (self._parent.root_offset * 32)))
            self._raw__m_nodes = io.read_bytes((self._parent.root_size * 32))
            _io__raw__m_nodes = KaitaiStream(BytesIO(self._raw__m_nodes))
            self._m_nodes = RageOfMages1Res.ResourceHeaderList(_io__raw__m_nodes, self, self._root)
            io.seek(_pos)
            return self._m_nodes if hasattr(self, '_m_nodes') else None

    class ResourceHeaderList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_header = []
            self.header = []
            i = 0
            while not self._io.is_eof():
                self._raw_header.append(self._io.read_bytes(32))
                _io__raw_header = KaitaiStream(BytesIO(self._raw_header[-1]))
                self.header.append(RageOfMages1Res.ResourceHeader(_io__raw_header, self, self._root))
                i += 1

    @property
    def nodes(self):
        if hasattr(self, '_m_nodes'):
            return self._m_nodes if hasattr(self, '_m_nodes') else None

        _pos = self._io.pos()
        self._io.seek((self.resource_header.fat_offset + (self._root.resource_header.root_offset * 32)))
        self._raw__m_nodes = self._io.read_bytes((self.resource_header.root_size * 32))
        _io__raw__m_nodes = KaitaiStream(BytesIO(self._raw__m_nodes))
        self._m_nodes = RageOfMages1Res.ResourceHeaderList(_io__raw__m_nodes, self, self._root)
        self._io.seek(_pos)
        return self._m_nodes if hasattr(self, '_m_nodes') else None
