import random
from dataclasses import dataclass
from typing import List

from numba import njit
from numba.experimental import jitclass
from numba.typed import List as NumbaList

from . import TestCase

"""
Test results:     
[success] 54.23% time_tests.test_camera_rect.TestFilterRectsNumba.test_numba_rects_numba_filter_inline: 0.8890s
[success] 41.17% time_tests.test_camera_rect.TestFilterRectsNumba.test_numba_rects_numba_filter: 0.6749s
[success] 3.79% time_tests.test_camera_rect.TestFilterRectsNumba.test_numba_rects_python_filter: 0.0622s
[success] 0.78% time_tests.test_camera_rect.TestFilterRects.test_filter_rects: 0.0128s
[success] 0.03% time_tests.test_camera_rect.TestFilterRectsCython.test_filter_rects: 0.0005s
"""
RECT_COUNT = 256 * 256


@dataclass
class Rect:
    left: int
    top: int
    right: int
    bottom: int


@jitclass
class NumbaRect:
    left: int
    top: int
    right: int
    bottom: int

    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom


def create_random_rects(rect_class, n, max_xy=32 * 256, max_dimensions=256):
    rects = []
    for i in range(n):
        x = random.randint(0, max_xy)
        y = random.randint(0, max_xy)
        w = random.randint(0, max_dimensions)
        h = random.randint(0, max_dimensions)
        rect = rect_class(x, y, x + w, y + h)
        rects.append(rect)
    return rects


def has_intersection(box1: Rect, box2: Rect):
    return box2.left < box1.right and box2.right > box1.left and box2.top < box1.bottom and box2.bottom > box1.top


@njit
def has_intersection_numba(box1: NumbaRect, box2: NumbaRect):
    return box2.left < box1.right and box2.right > box1.left and box2.top < box1.bottom and box2.bottom > box1.top


@njit
def filter_intersections_numba(rect: NumbaRect, rects: List[NumbaRect]) -> List[NumbaRect]:
    return [x for x in rects if has_intersection_numba(rect, x)]


@njit
def filter_intersections_numba_inline(rect: NumbaRect, rects: List[NumbaRect]) -> List[NumbaRect]:
    res = NumbaList()
    for x in rects:
        if rect.left < x.right and rect.right > x.left and rect.top < x.bottom and rect.bottom > x.top:
            res.append(x)
    return res


class TestFilterRects(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rects = create_random_rects(Rect, RECT_COUNT)

    def test_filter_rects(self):
        rect = Rect(0, 0, 1024, 768)
        list(filter(lambda x: has_intersection(rect, x), self.rects))


from time_tests.filter_rects import filter_rects as filter_rects_cython, Rect as RectCython


class TestFilterRectsCython(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rects = create_random_rects(RectCython, RECT_COUNT)

    def test_filter_rects(self):
        rect = RectCython(0, 0, 1024, 768)
        print(rect)
        result = filter_rects_cython(rect, self.rects)
        assert len(result) > 0


class TestFilterRectsCTypes(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rects = create_random_rects(Rect, RECT_COUNT)

    def filter_rects_cext(self):
        rect = Rect(0, 0, 1024, 768)
        print(rect.bottom)
        results = filter_intersections_cext(rect, self.rects)
        print(results)

class TestFilterRectsNumba(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rects = create_random_rects(NumbaRect, RECT_COUNT)

    def test_numba_rects_python_filter(self):
        rect = NumbaRect(0, 0, 1024, 768)
        list(filter(lambda x: has_intersection_numba(rect, x), self.rects))

    def test_numba_rects_numba_filter(self):
        rect = NumbaRect(0, 0, 1024, 768)
        filter_intersections_numba(rect, self.rects)

    def test_numba_rects_numba_filter_inline(self):
        rect = NumbaRect(0, 0, 1024, 768)
        filter_intersections_numba_inline(rect, self.rects)
