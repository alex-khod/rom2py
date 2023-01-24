from . import TestCase
from src.formats.sprites.base import A256 as A256Python
from src.formats.sprites._sprites_cy import A256Cython
from src.formats.sprites._sprites_numba import A256Numba
from src.formats.sprites._sprites_cpp import A256Cpp

from src.units.cache import load_units
from src.content import Selector


# speed: python < cython < numba < cpp
# butthurt: python < cpp < numba < cython

class TestLoaders(TestCase):

    def test_python(self):
        Selector.ext_map[".256"] = A256Python
        load_units()

    def test_cython(self):
        Selector.ext_map[".256"] = A256Cython
        load_units()

    def test_numba(self):
        Selector.ext_map[".256"] = A256Numba
        load_units()

    def test_cpp(self):
        Selector.ext_map[".256"] = A256Cpp
        load_units()
