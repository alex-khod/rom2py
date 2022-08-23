from . import TestCase

from src import pathfind


class TestPathfind(TestCase):

    def test_heights_array_same_values_as_flat_heights(self):
        w, h = 3, 3
        grid = [[0] * w for _ in range(h)]

        path = pathfind.bfs(grid, start=(0, 0), goal=(2, 2))
        # assert path == [(0, 0), (1, 1), (2, 2)]
        assert path == [(2, 2), (1, 1)]
