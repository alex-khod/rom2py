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
        alm = Resources.from_file("data", "atest.alm")
        h, w = 4, 4
        alm.general_map_info.width = w
        alm.general_map_info.height = h
        alm["heights"].body.heights = sum([[0, 0, 0, 1] for _ in range(h)], [])
        assert alm.heights_column_at(w - 1) == (1, 1, 1, 1)

    def test_tilecoords_are_cached(self):
        alm = Resources.from_file("data", "atest.alm")
        tilecoords = alm.tilecoords
        assert id(alm.tilecoords) == id(tilecoords)
