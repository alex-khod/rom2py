from . import TestCase
from src.resources import Resources, get_resource_at_root
from src.formats.sprites.base import ROM256 as ROM256Python
from src.formats.sprites.base import ROM16A as ROM16APython
from src.formats.sprites._sprites_cpp import ROM256Cpp, ROM16ACpp
from src.formats.sprites._sprites_cy import ROM256Cython
from src.formats.sprites._sprites_numba import ROM256Numba
import numpy as np

class TestBase(TestCase):

    def test_x_flip(self):
        a = np.array([[1, 0], [0, 1]])
        b = np.array([[0, 1], [1, 0]])
        a_flipped = ROM256Python._frame_class.do_x_flip(a.copy())
        assert (a_flipped == b).all()


class SpriteTest:
    impl_class = None
    _bytes = None
    test_resource_path = None
    good_data_path = None

    def setUp(self):
        self._bytes = Resources[self.test_resource_path].bytes
        with open(get_resource_at_root(*self.good_data_path), "rb") as f:
            self._good_data = f.read()

    def test_color_indexes(self):
        sprite = self.impl_class.from_bytes(self._bytes)
        frame = sprite[0].to_color_indexes()
        frame_bytes = frame.tobytes()
        assert self._good_data == frame_bytes


class TestROM256Python(SpriteTest, TestCase):
    impl_class = ROM256Python
    test_resource_path = "graphics", "objects", "bambuk1", "sprites.256"
    good_data_path = "data", "bambuk.bin"


class TestROM256Cpp(SpriteTest, TestCase):
    impl_class = ROM256Cpp
    test_resource_path = "graphics", "objects", "bambuk1", "sprites.256"
    good_data_path = "data", "bambuk.bin"

class Test256Numba(SpriteTest, TestCase):
    impl_class = ROM256Numba
    test_resource_path = "graphics", "objects", "bambuk1", "sprites.256"
    good_data_path = "data", "bambuk.bin"

class Test256Cython(SpriteTest, TestCase):
    impl_class = ROM256Cython
    test_resource_path = "graphics", "objects", "bambuk1", "sprites.256"
    good_data_path = "data", "bambuk.bin"

class TestROM16APython(SpriteTest, TestCase):
    impl_class = ROM16APython
    test_resource_path = "graphics", "interface", "inn", "unit1", "sprites.16a"
    good_data_path = "data", "unit.bin"

class TestROM16ACpp(SpriteTest, TestCase):
    impl_class = ROM16ACpp
    test_resource_path = "graphics", "interface", "inn", "unit1", "sprites.16a"
    good_data_path = "data", "unit.bin"
