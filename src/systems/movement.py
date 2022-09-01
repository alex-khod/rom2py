import math
from collections import deque
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple, List

from src.formats.alm2 import Alm2
from src.utils import Vec2, lerp

TILE_SIZE = 32


class WalkAiStates(IntEnum):
    rotate = 0
    move = 1


class AttackAiStates(IntEnum):
    start_attack = 0
    attacking = 1
    end_attack = 2


class UnitAiStates(IntEnum):
    idle = 0
    move = 1
    attack = 2
    die = 3
    bones = 4


@dataclass
class UnitAi:
    state = UnitAiStates.idle
    target = None
    tasks = None
    dead = False

    def __init__(self):
        self.tasks = deque()
        self.angle = 0


# directions_map = ((3, 4, 5),
#                   (2, 7, 6),
#                   (1, 0, 7))

directions_map = ((96, 128, 160),
                  (64, 192, 192),
                  (32, 0, 224))


@dataclass
class World:
    alm: Alm2
    units: List


class MovementSystem:

    @staticmethod
    def direction_to_tile(from_xy: Vec2, to_xy: Vec2):
        dxdy = to_xy - from_xy
        dxdy.x = dxdy.x // abs(dxdy.x) if dxdy.x != 0 else 0
        dxdy.y = dxdy.y // abs(dxdy.y) if dxdy.y != 0 else 0
        # the lookup is Y first
        dxdy = round(dxdy)
        direction = directions_map[dxdy.y + 1][dxdy.x + 1]
        return direction

    @staticmethod
    def rotation_dphi(rotate_from: int, rotate_to: int, period=256):
        """ Return shortest angle between operands. """
        half_period = period // 2
        diff = (rotate_to - rotate_from + period) % period
        if diff > half_period:
            return diff - period
        return diff

    @staticmethod
    def rotation_dphi_direction(rotate_from: int, rotate_to: int, period=256):
        res = MovementSystem.rotation_dphi(rotate_from, rotate_to, period)
        if res != 0:
            res = res // abs(res)
        return res


class Progress:
    def __init__(self, speed=0.1, elapsed=0, duration=1):
        self.speed = speed
        self.elapsed = elapsed
        self.duration = duration

        self.progress = elapsed / duration if duration > 0 else 1

    def tick(self):
        self.elapsed += self.speed
        self.progress = self.elapsed / self.duration if self.duration > 0 else 1


class RotateTask:
    def __init__(self, mobj, from_angle, to_angle):
        self.mobj = mobj
        self.from_angle = from_angle
        self.to_angle = to_angle
        self.dphi = MovementSystem.rotation_dphi(from_angle, to_angle)
        self.to_angle_shortest = self.from_angle + self.dphi
        self.progress = Progress(mobj.rot_speed, from_angle, self.to_angle_shortest)

    def tick(self):
        mobj = self.mobj
        self.progress.tick()
        factor = self.progress.progress
        angle = lerp(self.from_angle, self.to_angle_shortest, factor)
        mobj.ai.angle = int(angle) % 256
        return factor >= 1


class MoveTask:
    ticks_per_move = 4

    def __init__(self, mobj, from_tile_xy, to_tile_xy, world: World):
        self.mobj = mobj
        self.from_tile_xy = from_tile_xy
        self.to_tile_xy = to_tile_xy
        self.move_angle = MovementSystem.direction_to_tile(from_tile_xy, to_tile_xy)

        self.world = world
        self.from_xy = world.alm.tile_center_at(from_tile_xy)
        self.to_xy = world.alm.tile_center_at(to_tile_xy)

        next_tile_dxdy = to_tile_xy - from_tile_xy
        duration = math.hypot(*next_tile_dxdy) * TILE_SIZE

        self.progress = Progress(mobj.speed, 0, duration)

    def tick(self):
        mobj = self.mobj
        mobj.ai.angle = self.move_angle
        mobj.ai.state = UnitAiStates.move

        self.progress.tick()
        factor = self.progress.progress
        mobj.xy = self.from_xy.lerp(self.to_xy, factor)
        frame_id = lerp(mobj.ai.move_begin_phases, mobj.ai.move_phases - 1, factor)
        mobj.frame_id = int(frame_id)

        if factor >= 1:
            # should be animation effect?
            mobj.tile_xy = self.to_tile_xy
            self.world.units.layer[self.from_tile_xy] = None
            self.world.units.layer[self.to_tile_xy] = mobj

            mobj.ai.state = UnitAiStates.idle
            return True
        return False


class AttackTask:

    def __init__(self, mobj, target):
        self.mobj = mobj
        self.target = target

        self.progress = Progress(1 / mobj.ai.attack_phases, 0, mobj.ai.attack_phases)

    def tick(self):
        mobj = self.mobj
        mobj.ai.state = UnitAiStates.attack
        mobj.ai.angle = MovementSystem.direction_to_tile(mobj.tile_xy, self.target.tile_xy)
        self.progress.tick()
        factor = self.progress.progress

        mobj.frame_id = int(lerp(0, mobj.ai.attack_phases - 1, factor))
        return factor > 1


class DieTask:

    def tick(self):
        mobj.ai.state = UnitAiStates.die
        mobj.ai.angle = self.angle
        self._tick += 1
        if self._tick % 4 != 0:
            return False
        mobj.move_frame_id += 1
        if mobj.move_frame_id > 10:
            return True
        return False


def scan_surroundings(mobj, world):
    tile_xy = mobj.tile_xy
    units = world.units.layer
    for j in range(-1, 2):
        for i in range(-1, 2):
            if j == 0 and i == 0:
                continue
            check = Vec2(tile_xy.x + i, tile_xy.y + j)
            unit = units[check]
            if unit:
                return unit


class ThinkSystem:
    think_stuff = {}
    world: World

    def move_to_tile_xy(self, mobj, grid, to_tile_xy: Tuple[int, int]):
        # maybe refer to mobj as parent?
        from src import pathfind
        from_xy = mobj.tile_xy
        path = pathfind.bfs(grid, from_xy, to_tile_xy)
        if path:
            path = list(map(lambda x: Vec2(*x), path))
            mobj.ai.path = path
            mobj.ai.tasks.clear()
            # mobj.ai.commands.clear()
            # mobj.ai.commands.append(0)
            self.think_stuff[mobj.EID] = mobj

    def get_new_tasks(self, mobj):

        if not mobj.ai.path and not mobj.ai.target:
            target = scan_surroundings(mobj, self.world)
            if target:
                task = AttackTask(mobj, target)
                mobj.ai.tasks.append(task)

        path = mobj.ai.path
        if path:
            tile_xy = mobj.tile_xy
            next_tile = path.pop()
            angle = mobj.ai.angle
            next_angle = MovementSystem.direction_to_tile(tile_xy, next_tile)
            rotation_phases = mobj.ai.rotation_phases
            if rotation_phases and angle != next_angle:
                task = RotateTask(mobj, angle, next_angle)
                print(f"rotate from {angle} to {next_angle}")
                mobj.ai.tasks.append(task)
            task = MoveTask(mobj, tile_xy, next_tile, self.world)
            print(f"move from {tile_xy} to {next_tile}")
            mobj.ai.tasks.append(task)
        return bool(mobj.ai.tasks)

    def tick(self):
        think_stuff = self.think_stuff
        to_pop = []
        for EID, mobj in think_stuff.items():
            if not mobj.ai.tasks:
                self.get_new_tasks(mobj)
            while mobj.ai.tasks and mobj.ai.tasks[0].tick():
                mobj.ai.tasks.popleft()

        for EID in to_pop:
            think_stuff.pop(EID)
