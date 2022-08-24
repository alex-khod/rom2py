from . import TestCase

from src.mobj.units.units import MovementSystem, UnitAi
from src.mobj.units.animation import EDirection16
from unittest.mock import Mock


class TestMovement(TestCase):

    def test_direction_to_cell(self):
        cur_cell = (1, 1)
        assert MovementSystem.direction_to_tile(cur_cell, (0, 0)) == EDirection16.upleft.value
        # why not?
        assert MovementSystem.direction_to_tile(cur_cell, cur_cell) == EDirection16.right.value
        assert MovementSystem.direction_to_tile(cur_cell, (0, 1)) == EDirection16.left.value
        assert MovementSystem.direction_to_tile(cur_cell, (2, 2)) == EDirection16.downright.value

        # two cells away
        assert MovementSystem.direction_to_tile(cur_cell, (3, 3)) == EDirection16.downright.value
        assert MovementSystem.direction_to_tile(cur_cell, (-1, -1)) == EDirection16.upleft.value

    def _test_direction_to_next_cell(self):
        walk_ai = Mock()
        walk_ai.x = 1
        walk_ai.y = 1
        walk_ai.path = [[0, 0]]
        assert MovementSystem.direction_to_next_cell(walk_ai) == EDirection16.upleft.value
        walk_ai.path = [[1, 1]]
        assert MovementSystem.direction_to_next_cell(walk_ai) == EDirection16.right.value
        walk_ai.path = [[0, 1]]
        assert MovementSystem.direction_to_next_cell(walk_ai) == EDirection16.left.value
        walk_ai.path = [[2, 2]]
        assert MovementSystem.direction_to_next_cell(walk_ai) == EDirection16.downright.value

        # two cells away
        walk_ai.path = [[3, 3]]
        assert MovementSystem.direction_to_next_cell(walk_ai) == EDirection16.downright.value
        walk_ai.path = [[-1, -1]]
        assert MovementSystem.direction_to_next_cell(walk_ai) == EDirection16.upleft.value

    def test_rotate_to(self):
        assert MovementSystem.calc_rotate_dx(0, 0) == 0
        assert MovementSystem.calc_rotate_dx(0, 1) == 1
        assert MovementSystem.calc_rotate_dx(0, 8, period=16) == 1
        assert MovementSystem.calc_rotate_dx(0, 9, period=16) == -1
        assert MovementSystem.calc_rotate_dx(8, 0, period=16) == -1
        assert MovementSystem.calc_rotate_dx(9, 0, period=16) == 1


