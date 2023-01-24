import random
from dataclasses import dataclass

from . import TestCase

"""
Test results:
RECT_COUNT = 10 * 256 * 256     
[success] 86.39% time_tests.test_camera_rect.TestFilterRects.test_filter_rects: 0.1380s
[success] 13.61% time_tests.test_camera_rect.TestFilterRectsCython.test_filter_rects: 0.0217s
"""
RECT_COUNT = 10 * 256 * 256


@dataclass
class Rect:
    left: int
    top: int
    right: int
    bottom: int


# NumbaRect = np.dtype([('left', int), ('top', int), ('right', int), ('bottom', int)])

class Dummy:
    rect = None


def create_random_rects(rect_class, n, max_xy=32 * 256, max_dimensions=256):
    sprites = []
    for i in range(n):
        x = random.randint(0, max_xy)
        y = random.randint(0, max_xy)
        w = random.randint(0, max_dimensions)
        h = random.randint(0, max_dimensions)
        rect = rect_class(x, y, x + w, y + h)
        sprite = Dummy()
        sprite.rect = rect
        sprites.append(sprite)
    return sprites


def has_intersection(box1: Rect, box2: Rect):
    return box2.left < box1.right and box2.right > box1.left and box2.top < box1.bottom and box2.bottom > box1.top


class TestFilterRects(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rects = create_random_rects(Rect, RECT_COUNT)

    def test_filter_rects(self):
        rect = Rect(0, 0, 1024, 768)
        list(filter(lambda x: has_intersection(rect, x.rect), self.rects))


from src.rects import filter_rects_by_intersect as filter_rects_cython, Rect as RectCython


class TestFilterRectsCython(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rects = create_random_rects(RectCython, RECT_COUNT)

    def test_filter_rects(self):
        rect = RectCython(0, 0, 1024, 768)
        result = filter_rects_cython(rect, self.rects)
        assert len(result) > 0
