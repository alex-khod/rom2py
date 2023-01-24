from . import TestCase
from src.utils import Vec2


class TestVecs(TestCase):

    def test_distance(self):
        a = Vec2(0, 0)
        assert a.max_dxdy(Vec2(1, 1)) == 1
        assert a.max_dxdy(Vec2(0, 1)) == 1
        assert a.max_dxdy(Vec2(1, 0)) == 1

        assert a.max_dxdy(Vec2(-2, 0)) == 2
        assert a.max_dxdy(Vec2(0, -2)) == 2
        assert a.max_dxdy(Vec2(-2, -2)) == 2
