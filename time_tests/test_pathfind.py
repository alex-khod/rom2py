from unittest import TestCase
from src import pathfind


def generate_grid():
    import random
    w, h = 256, 256
    grid = [[random.randint(0, 1) for _ in range(h)] for _ in range(w)]

    def generate_unoccupied_cell():
        x, y = (random.randint(0, w - 1), random.randint(0, h - 1))
        while grid[y][x] != 0:
            x, y = (random.randint(0, 255), random.randint(0, h - 1))
        return x, y

    start = generate_unoccupied_cell()
    goal = generate_unoccupied_cell()
    return grid, start, goal


import numba


# TODO needs an implementation of collections.deque
# numba_bfs = numba.njit(pathfind.bfs)


class TestBfs(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.grid, cls.start, cls.goal = generate_grid()
        # numba_bfs(self.grid, self.start, self.goal)

    def test_bfs(self):
        pathfind.bfs(self.grid, self.start, self.goal)

    def _test_numba_bfs(self):
        numba_bfs(self.grid, self.start, self.goal)
