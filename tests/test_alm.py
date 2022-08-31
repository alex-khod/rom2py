from src.formats.alm2 import HeightMap
from . import TestCase
from src.resources import Resources


class TestAlm(TestCase):

    def test_heights_array_same_values_as_flat_heights(self):
        alm = Resources.from_file("data", "atest.alm")
        assert alm.heights[0][:5] == alm["heights"].body.heights[:5]
        start = alm.width
        assert alm.heights[1][:5] == alm["heights"].body.heights[start:start + 5]

    def test_tile_corner_heights_at(self):
        alm = Resources.from_file("data", "atest.alm")
        heights = alm["heights"].body.heights

        w = alm.width
        for j in range(alm.height - 1):
            for i in range(alm.height - 1):
                h00 = heights[j * w + i]
                h10 = heights[j * w + i + 1]
                h11 = heights[(j + 1) * w + i + 1]
                h01 = heights[(j + 1) * w + i]
                assert [h00, h10, h11, h01] == alm.tile_corner_heights_at(i, j)

    def test_heights_column_at(self):
        w, h = 4, 4
        heights = [x for _ in range(h) for x in [0, 0, 0, 1]]
        height_map = HeightMap(heights, w, h)
        assert height_map.heights_column_at(w - 1) == (1, 1, 1, 1)

    def test_tilecoords_are_cached(self):
        alm = Resources.from_file("data", "atest.alm")
        tilecoords = alm.tilecoords
        assert id(alm.tilecoords) == id(tilecoords)

    def test_lerp_heights(self):
        alm = Resources.from_file("data", "atest.alm")
        h, w = 2, 2
        alm.general.width = w
        alm.general.height = h
        alm["heights"].body.heights = [0, 0]

