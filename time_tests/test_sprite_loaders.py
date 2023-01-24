from . import TestCase
# call setup_sprites
from src import resources

from src.formats.sprites.base import ROM256 as ROM256Python
from src.formats.sprites._sprites_cy import ROM256Cython
from src.formats.sprites._sprites_numba import ROM256Numba
from src.formats.sprites._sprites_cpp import ROM256Cpp
from src.formats.sprites._sprites_cext import ROM256CExt

from src.mobj.units.cache import load_units
from src.content import Selector


# speed: python < cython < numba < cpp
# butthurt: python < cpp < numba < cython

class TestLoaders(TestCase):

    def test_python(self):
        Selector.ext_map[".256"] = ROM256Python
        load_units()

    def test_cython(self):
        Selector.ext_map[".256"] = ROM256Cython
        load_units()

    def test_numba(self):
        Selector.ext_map[".256"] = ROM256Numba
        load_units()

    def test_cpp(self):
        Selector.ext_map[".256"] = ROM256Cpp
        load_units()

    def test_cext(self):
        Selector.ext_map[".256"] = ROM256CExt
        load_units()
