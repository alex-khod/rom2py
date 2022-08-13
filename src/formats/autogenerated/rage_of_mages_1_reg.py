# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RageOfMages1Reg(KaitaiStruct):

    class ERegistryRecordType(Enum):
        string = 0
        directory = 1
        int = 2
        float = 4
        int_array = 6
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.signature = self._io.read_bytes(4)
        if not self.signature == b"\x26\x59\x41\x31":
            raise kaitaistruct.ValidationNotEqualError(b"\x26\x59\x41\x31", self.signature, self._io, u"/seq/0")
        self.registry_header = RageOfMages1Reg.RootRegistryHeaderT(self._io, self, self._root)

    class RegistryHeaderList(KaitaiStruct):
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
                self.header.append(RageOfMages1Reg.RegistryHeader(_io__raw_header, self, self._root))
                i += 1



    class DirectoryEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.e_offset = self._io.read_u4le()
            self.e_count = self._io.read_u4le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value if hasattr(self, '_m_value') else None

            io = self._root._io
            _pos = io.pos()
            io.seek((24 + (32 * self.e_offset)))
            self._raw__m_value = io.read_bytes((self.e_count * 32))
            _io__raw__m_value = KaitaiStream(BytesIO(self._raw__m_value))
            self._m_value = RageOfMages1Reg.RegistryHeaderList(_io__raw__m_value, self, self._root)
            io.seek(_pos)
            return self._m_value if hasattr(self, '_m_value') else None


    class ByteEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = self._io.read_u1()


    class StringEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.e_offset = self._io.read_u4le()
            self.e_count = self._io.read_u4le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value if hasattr(self, '_m_value') else None

            io = self._root._io
            _pos = io.pos()
            io.seek((self._root.registry_header.data_origin + self.e_offset))
            self._m_value = (KaitaiStream.bytes_terminate(io.read_bytes(self.e_count), 0, False)).decode(u"IBM866")
            io.seek(_pos)
            return self._m_value if hasattr(self, '_m_value') else None


    class RegistryHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.junk = self._io.read_u4le()
            _on = self.rec_type
            if _on == RageOfMages1Reg.ERegistryRecordType.int_array:
                self._raw_value = self._io.read_bytes(8)
                _io__raw_value = KaitaiStream(BytesIO(self._raw_value))
                self.value = RageOfMages1Reg.IntArrayEntry(_io__raw_value, self, self._root)
            elif _on == RageOfMages1Reg.ERegistryRecordType.float:
                self._raw_value = self._io.read_bytes(8)
                _io__raw_value = KaitaiStream(BytesIO(self._raw_value))
                self.value = RageOfMages1Reg.FloatEntry(_io__raw_value, self, self._root)
            elif _on == RageOfMages1Reg.ERegistryRecordType.string:
                self._raw_value = self._io.read_bytes(8)
                _io__raw_value = KaitaiStream(BytesIO(self._raw_value))
                self.value = RageOfMages1Reg.StringEntry(_io__raw_value, self, self._root)
            elif _on == RageOfMages1Reg.ERegistryRecordType.int:
                self._raw_value = self._io.read_bytes(8)
                _io__raw_value = KaitaiStream(BytesIO(self._raw_value))
                self.value = RageOfMages1Reg.IntEntry(_io__raw_value, self, self._root)
            elif _on == RageOfMages1Reg.ERegistryRecordType.directory:
                self._raw_value = self._io.read_bytes(8)
                _io__raw_value = KaitaiStream(BytesIO(self._raw_value))
                self.value = RageOfMages1Reg.DirectoryEntry(_io__raw_value, self, self._root)
            else:
                self._raw_value = self._io.read_bytes(8)
                _io__raw_value = KaitaiStream(BytesIO(self._raw_value))
                self.value = RageOfMages1Reg.ByteEntry(_io__raw_value, self, self._root)
            self.type = self._io.read_u4le()
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(16), 0, False)).decode(u"IBM866")

        @property
        def rec_type(self):
            if hasattr(self, '_m_rec_type'):
                return self._m_rec_type if hasattr(self, '_m_rec_type') else None

            _pos = self._io.pos()
            self._io.seek(12)
            self._m_rec_type = KaitaiStream.resolve_enum(RageOfMages1Reg.ERegistryRecordType, self._io.read_u4le())
            self._io.seek(_pos)
            return self._m_rec_type if hasattr(self, '_m_rec_type') else None


    class IntArrayEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.e_offset = self._io.read_u4le()
            self.e_size = self._io.read_u4le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value if hasattr(self, '_m_value') else None

            io = self._root._io
            _pos = io.pos()
            io.seek((self._root.registry_header.data_origin + self.e_offset))
            self._m_value = [None] * (self.e_size // 4)
            for i in range(self.e_size // 4):
                self._m_value[i] = io.read_s4le()

            io.seek(_pos)
            return self._m_value if hasattr(self, '_m_value') else None


    class IntEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = self._io.read_s4le()


    class FloatEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value = self._io.read_f8le()


    class RootRegistryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.root_offset = self._io.read_u4le()
            self.root_size = self._io.read_u4le()
            self.registry_flags = self._io.read_u4le()
            self.registry_eat_size = self._io.read_u4le()
            self.junk = self._io.read_u4le()

        @property
        def data_origin(self):
            if hasattr(self, '_m_data_origin'):
                return self._m_data_origin if hasattr(self, '_m_data_origin') else None

            self._m_data_origin = (28 + (32 * self.registry_eat_size))
            return self._m_data_origin if hasattr(self, '_m_data_origin') else None


    @property
    def nodes(self):
        if hasattr(self, '_m_nodes'):
            return self._m_nodes if hasattr(self, '_m_nodes') else None

        _pos = self._io.pos()
        self._io.seek((24 + (32 * self.registry_header.root_offset)))
        self._raw__m_nodes = self._io.read_bytes((self.registry_header.root_size * 32))
        _io__raw__m_nodes = KaitaiStream(BytesIO(self._raw__m_nodes))
        self._m_nodes = RageOfMages1Reg.RegistryHeaderList(_io__raw__m_nodes, self, self._root)
        self._io.seek(_pos)
        return self._m_nodes if hasattr(self, '_m_nodes') else None


