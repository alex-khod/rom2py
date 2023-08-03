from pyglet.math import Vec2

from . import TestCase

from src.systems import movement
from src.systems.animations.units import EDirection16
from unittest.mock import Mock


class TestMovement(TestCase):

    def test_direction_to_cell(self):
        cur_cell = Vec2(1, 1)
        mul = 16
        assert movement.direction_to_tile(cur_cell, Vec2(0, 0)) == EDirection16.upleft.value * mul
        # why not?
        assert movement.direction_to_tile(cur_cell, cur_cell) == EDirection16.down.value * mul
        assert movement.direction_to_tile(cur_cell, Vec2(0, 1)) == EDirection16.left.value * mul
        assert movement.direction_to_tile(cur_cell, Vec2(2, 2)) == EDirection16.downright.value * mul

        # two cells away
        assert movement.direction_to_tile(cur_cell, Vec2(3, 3)) == EDirection16.downright.value * mul
        assert movement.direction_to_tile(cur_cell, Vec2(-1, -1)) == EDirection16.upleft.value * mul

    def _test_direction_to_next_cell(self):
        walk_ai = Mock()
        walk_ai.x = 1
        walk_ai.y = 1
        walk_ai.path = [[0, 0]]
        assert movement.direction_to_next_cell(walk_ai) == EDirection16.upleft.value
        walk_ai.path = [[1, 1]]
        assert movement.direction_to_next_cell(walk_ai) == EDirection16.right.value
        walk_ai.path = [[0, 1]]
        assert movement.direction_to_next_cell(walk_ai) == EDirection16.left.value
        walk_ai.path = [[2, 2]]
        assert movement.direction_to_next_cell(walk_ai) == EDirection16.downright.value

        # two cells away
        walk_ai.path = [[3, 3]]
        assert movement.direction_to_next_cell(walk_ai) == EDirection16.downright.value
        walk_ai.path = [[-1, -1]]
        assert movement.direction_to_next_cell(walk_ai) == EDirection16.upleft.value

    def test_angle_diff_shortest(self):
        assert movement.angle_diff_shortest(0, 3, period=4) == -1
        assert movement.angle_diff_shortest(3, 0, period=4) == 1
        assert movement.angle_diff_shortest(0, 2, period=4) == 2
        assert movement.angle_diff_shortest(2, 0, period=4) == 2
