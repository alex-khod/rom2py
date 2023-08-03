import math
from collections import deque
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple, List

from src.formats.alm2 import Alm2
from src.utils import Vec2, lerp

# directions_map = ((3, 4, 5),
#                   (2, 7, 6),
#                   (1, 0, 7))

directions_map = ((96, 128, 160),
                  (64, 0, 192),
                  (32, 0, 224))

ROTATION_PHASES = len(directions_map)


def direction_to_tile(from_xy: Vec2, to_xy: Vec2):
    dxdy = to_xy - from_xy
    dxdy.x = dxdy.x // abs(dxdy.x) if dxdy.x != 0 else 0
    dxdy.y = dxdy.y // abs(dxdy.y) if dxdy.y != 0 else 0
    # the lookup is Y first
    dxdy = round(dxdy)
    direction = directions_map[dxdy.y + 1][dxdy.x + 1]
    return direction


def angle_diff_shortest(angle_from: int, angle_to: int, period=256):
    """ Return shortest angle between operands. """
    half_period = period // 2
    diff = (angle_to - angle_from + period) % period
    if diff > half_period:
        return diff - period
    return diff
