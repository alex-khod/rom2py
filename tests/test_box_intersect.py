from . import TestCase
from src.utils import Box, has_intersection, get_intersection


class Testbox(TestCase):

    def test_boxes_are_comparable(self):
        # x y w h
        box1 = Box(0, 0, 4, 4)
        box2 = Box(-2, -2, 4, 4)
        box3 = Box(0, 0, 4, 4)
        assert box1 == box3
        assert box1 == Box(0, 0, 4, 4)
        assert box2 != box1
        assert box2 != box3

    def test_no_intersection(self):
        box1 = Box(0, 0, 4, 4)
        box2 = Box(-2, -2, 2, 2)
        res = get_intersection(box1, box2)
        assert res is None

    def test_intersect_oob_upleft(self):
        box1 = Box(0, 0, 4, 4)
        box2 = Box(-2, -2, 4, 4)
        res = get_intersection(box1, box2)
        res == Box(0, 0, 2, 2)

    def test_intersect_oob_bottomright(self):
        box1 = Box(0, 0, 4, 4)
        box2 = Box(2, 2, 4, 4)
        res = get_intersection(box1, box2)
        res == Box(2, 2, 2, 2)
