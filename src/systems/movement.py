import math
from collections import deque
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple

from src.formats.alm2 import Alm2
from src.utils import Vec2

TILE_SIZE = 32


class WalkAiStates(IntEnum):
    rotate = 0
    move = 1


@dataclass
class WalkAi:
    redraw = False
    state: WalkAiStates = None
    prev_state: WalkAiStates = None
    path: list = None

    ticks_per_rotate = 4
    ticks_per_move = 4
    frame_id = 0
    tile_xy: Vec2 = None
    xy: Vec2 = None
    height = 0

    rotation_phases = 0
    move_phases = 0
    move_begin_phases = 0


class AttackAiStates(IntEnum):
    start_attack = 0
    attacking = 1
    end_attack = 2


class AttackAi:
    state = None


class UnitAiStates(IntEnum):
    idle = 0
    move = 1
    attack = 2
    die = 3
    bones = 4


@dataclass
class UnitAi:
    state = UnitAiStates.idle
    walk_ai = None
    attack_ai = None
    tasks = None
    commands = None
    dead = False

    def __init__(self):
        self.walk_ai = WalkAi()
        self.attack_ai = AttackAi()
        self.tasks = deque()
        self.commands = deque()


directions_8_map = ((3, 4, 5),
                    (2, 7, 6),
                    (1, 0, 7))

directions_16_map = ((6, 8, 10),
                     (4, 12, 12),
                     (2, 0, 14))


class MovementSystem:
    moving_stuff = {}
    alm: Alm2 = None

    def __init__(self, alm: Alm2):
        self.alm = alm

    @staticmethod
    def direction_to_tile(from_xy: Vec2, to_xy: Vec2, dirmap: tuple = None):
        dxdy = to_xy - from_xy
        dxdy.x = dxdy.x // abs(dxdy.x) if dxdy.x != 0 else 0
        dxdy.y = dxdy.y // abs(dxdy.y) if dxdy.y != 0 else 0
        # the lookup is Y first
        direction = dirmap[dxdy.y + 1][dxdy.x + 1]
        return direction

    @staticmethod
    def get_next_tile(walk_ai: WalkAi) -> Vec2:
        return walk_ai.path[-1]

    @staticmethod
    def get_next_tile_dxdy(walk_ai: WalkAi) -> Vec2:
        dxdy = walk_ai.path[-1] - walk_ai.tile_xy
        return dxdy

    @staticmethod
    def calc_angle_direction(rotate_from: int, rotate_to: int, period=16):
        # calculate the fastest rotation direction between two angles
        if rotate_from == rotate_to:
            return 0
        angle_diff = rotate_to - rotate_from
        angle_magnitude = abs(angle_diff)
        # normalize to -1 / 1
        angle_direction = angle_diff // angle_magnitude
        if angle_magnitude > period // 2:
            return -angle_direction
        return angle_direction

    def tick(self):
        moving_stuff = self.moving_stuff
        to_pop = []
        for EID, mobj in moving_stuff.items():
            if not mobj.ai.tasks:
                to_pop.append(EID)
                continue
            task = mobj.ai.tasks[0]
            if task.tick(mobj):
                mobj.ai.tasks.popleft()

        for EID in to_pop:
            moving_stuff.pop(EID)


@dataclass
class RotationTask:
    from_angle: int = 0
    to_angle: int = 0
    dphi: int = 0
    mobj: object = None
    _tick = 0
    ticks_per_rotate = 2

    def tick(self, mobj):
        if mobj.ai.angle == self.to_angle:
            return True
        if self._tick >= self.ticks_per_rotate:
            self._tick = 0
            mobj.ai.angle += self.dphi
            mobj.ai.angle %= mobj.ai.walk_ai.rotation_phases
        else:
            self._tick += 1
        # ticks_per_rotate = 8
        return False


@dataclass
class MoveTask:
    from_xy: Vec2
    to_xy: Vec2
    dxdy: Vec2
    alm: Alm2
    distance: float = 0
    angle: int = 0
    _tick = 0
    traversed = 0
    ticks_per_move = 4

    def tick(self, mobj):
        mobj.ai.angle = self.angle
        mobj.ai.state = UnitAiStates.move

        # todo if movephases?
        if self._tick >= self.ticks_per_move:
            self._tick = 0
            mobj.move_frame_id += 1
        else:
            self._tick += 1

        # speed = 0.5
        speed = mobj.speed
        self.traversed += speed
        factor = self.traversed / self.distance

        # Calc visual coords ---
        walk_ai = mobj.ai.walk_ai
        base_xy = self.from_xy * Vec2(TILE_SIZE, TILE_SIZE) + Vec2(TILE_SIZE // 2, TILE_SIZE // 2)
        walk_ai.xy = base_xy + self.dxdy * Vec2(factor, factor) * Vec2(TILE_SIZE, TILE_SIZE)

        alm = self.alm
        avg_heights1 = alm.tile_avg_heights_at(*self.from_xy)
        avg_heights2 = alm.tile_avg_heights_at(*self.to_xy)
        ht1 = (1.0 - factor)
        ht2 = factor
        walk_ai.height = ht1 * avg_heights1 + ht2 * avg_heights2
        # ---

        if self.traversed >= self.distance:
            walk_ai.tile_xy = self.to_xy

            # TODO mobj_map
            tile_x, tile_y = self.from_xy
            alm.unit_map[tile_y][tile_x] = None
            tile_x, tile_y = self.to_xy
            alm.unit_map[tile_y][tile_x] = mobj

            walk_ai.xy = self.to_xy * Vec2(TILE_SIZE, TILE_SIZE) + Vec2(TILE_SIZE // 2, TILE_SIZE // 2)
            walk_ai.height = alm.tile_avg_heights_at(*walk_ai.tile_xy)

            mobj.ai.state = UnitAiStates.idle
            mobj.ai.angle = self.angle * 2
            return True
        return False

@dataclass
class MoveTask:
    from_xy: Vec2
    to_xy: Vec2
    dxdy: Vec2
    alm: Alm2
    distance: float = 0
    angle: int = 0
    _tick = 0
    traversed = 0
    ticks_per_move = 4

    def tick(self, mobj):
        mobj.ai.angle = self.angle
        mobj.ai.state = UnitAiStates.move

        # todo if movephases?
        if self._tick >= self.ticks_per_move:
            self._tick = 0
            mobj.move_frame_id += 1
        else:
            self._tick += 1

        # speed = 0.5
        speed = mobj.speed
        self.traversed += speed
        factor = self.traversed / self.distance

        # Calc visual coords ---
        walk_ai = mobj.ai.walk_ai
        base_xy = self.from_xy * Vec2(TILE_SIZE, TILE_SIZE) + Vec2(TILE_SIZE // 2, TILE_SIZE // 2)
        walk_ai.xy = base_xy + self.dxdy * Vec2(factor, factor) * Vec2(TILE_SIZE, TILE_SIZE)

        alm = self.alm
        avg_heights1 = alm.tile_avg_heights_at(*self.from_xy)
        avg_heights2 = alm.tile_avg_heights_at(*self.to_xy)
        ht1 = (1.0 - factor)
        ht2 = factor
        walk_ai.height = ht1 * avg_heights1 + ht2 * avg_heights2
        # ---

        if self.traversed >= self.distance:
            walk_ai.tile_xy = self.to_xy

            # TODO mobj_map
            tile_x, tile_y = self.from_xy
            alm.unit_map[tile_y][tile_x] = None
            tile_x, tile_y = self.to_xy
            alm.unit_map[tile_y][tile_x] = mobj

            walk_ai.xy = self.to_xy * Vec2(TILE_SIZE, TILE_SIZE) + Vec2(TILE_SIZE // 2, TILE_SIZE // 2)
            walk_ai.height = alm.tile_avg_heights_at(*walk_ai.tile_xy)

            mobj.ai.state = UnitAiStates.idle
            mobj.ai.angle = self.angle * 2
            return True
        return False

@dataclass
class AttackTask:
    from_xy: Vec2
    to_xy: Vec2
    angle : int
    distance: float = 0
    _tick = 0
    traversed = 0
    ticks_per_move = 4

    def tick(self, mobj):
        mobj.ai.state = UnitAiStates.attack
        mobj.ai.angle = self.angle
        self._tick += 1
        if self._tick % 4 != 0:
            return False
        mobj.move_frame_id += 1
        return False

@dataclass
class DieTask:
    angle : int
    distance: float = 0
    _tick = 0
    traversed = 0
    ticks_per_move = 4

    def tick(self, mobj):
        mobj.ai.state = UnitAiStates.die
        mobj.ai.angle = self.angle
        self._tick += 1
        if self._tick % 4 != 0:
            return False
        mobj.move_frame_id += 1
        if mobj.move_frame_id > 10:
            return True
        return False

class ThinkSystem:
    think_stuff = {}
    movement: MovementSystem = None

    def move_to_tile_xy(self, mobj, grid, to_xy: Tuple[int, int]):
        # maybe refer to mobj as parent?
        from src import pathfind
        from_xy = mobj.ai.walk_ai.tile_xy
        path = pathfind.bfs(grid, from_xy, to_xy)
        if path:
            path = list(map(lambda x: Vec2(*x), path))
            mobj.ai.walk_ai.path = path
            mobj.ai.tasks.clear()
            # mobj.ai.commands.clear()
            # mobj.ai.commands.append(0)
            self.think_stuff[mobj.EID] = mobj

    def tick(self):
        think_stuff = self.think_stuff
        to_pop = []
        movement = self.movement
        for EID, mobj in think_stuff.items():
            if mobj.ai.walk_ai.path and not mobj.ai.tasks:
                next_tile = mobj.ai.walk_ai.path.pop()
                next_angle = movement.direction_to_tile(mobj.ai.walk_ai.tile_xy, next_tile, dirmap=directions_16_map)
                if mobj.ai.walk_ai.rotation_phases and mobj.ai.angle != next_angle:
                    dphi = movement.calc_angle_direction(mobj.ai.angle, next_angle)
                    task = RotationTask(mobj.ai.angle, next_angle, dphi, mobj)
                    mobj.ai.tasks.append(task)

                next_tile_dxdy = next_tile - mobj.ai.walk_ai.tile_xy
                walk_distance = math.hypot(*next_tile_dxdy) * TILE_SIZE
                # TODO when path changes distance can be zero
                if walk_distance < 1:
                    continue
                angle = movement.direction_to_tile(mobj.ai.walk_ai.tile_xy, next_tile, dirmap=directions_8_map)
                task = MoveTask(mobj.ai.walk_ai.tile_xy, next_tile, dxdy=next_tile_dxdy, distance=walk_distance,
                                angle=angle, alm=movement.alm)
                mobj.ai.tasks.append(task)
                movement.moving_stuff[EID] = mobj

            if not mobj.dead and not mobj.ai.walk_ai.path and not mobj.ai.tasks:
                tile_xy = mobj.ai.walk_ai.tile_xy
                target = None
                for j in range(-1, 2):
                    for i in range(-1, 2):
                        if j == 0 and i == 0: continue
                        check = Vec2(tile_xy.x + i, tile_xy.y + j)
                        unit = movement.alm.unit_map[check.y][check.x]
                        if unit:
                            target = check
                            break
                    if target:
                        break
                if target:
                    next_tile = target
                    next_angle = movement.direction_to_tile(mobj.ai.walk_ai.tile_xy, next_tile,
                                                            dirmap=directions_16_map)
                    if mobj.ai.walk_ai.rotation_phases and mobj.ai.angle != next_angle:
                        dphi = movement.calc_angle_direction(mobj.ai.angle, next_angle)
                        task = RotationTask(mobj.ai.angle, next_angle, dphi, mobj)
                        mobj.ai.tasks.append(task)
                    attack_angle = movement.direction_to_tile(mobj.ai.walk_ai.tile_xy, next_tile,
                                                            dirmap=directions_8_map)
                    mobj.move_frame_id = 0
                    task = AttackTask(tile_xy, next_tile, attack_angle)
                    mobj.ai.tasks.append(task)
                    movement.moving_stuff[EID] = mobj
            # pop

        for EID in to_pop:
            think_stuff.pop(EID)
