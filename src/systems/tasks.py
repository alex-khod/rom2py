import math
from enum import IntEnum
from src.systems import movement
from src.utils import Vec2, lerp

TILE_SIZE = 32


class UnitSpriteKind(IntEnum):
    idle = 0
    move = 1
    attack = 2
    die = 3
    bones = 4


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
        self.angle_diff = movement.angle_diff_shortest(from_angle, to_angle)
        self.final_angle = self.from_angle + self.angle_diff
        self.progress = Progress(mobj.rot_speed, from_angle, self.final_angle)

    def tick(self):
        mobj = self.mobj
        self.progress.tick()
        factor = self.progress.progress
        angle = lerp(self.from_angle, self.final_angle, factor)
        mobj.ai.angle = int(angle) % 256
        if factor >= 1:
            mobj.ai.angle = self.to_angle
            return True
        return False


class MoveTask:
    ticks_per_move = 4

    def __init__(self, mobj, from_tile_xy, to_tile_xy, world: 'World'):
        self.mobj = mobj
        self.from_tile_xy = from_tile_xy
        self.to_tile_xy = to_tile_xy
        self.move_angle = movement.direction_to_tile(from_tile_xy, to_tile_xy)

        self.world = world
        self.from_xy = world.alm.tile_center_at(from_tile_xy)
        self.to_xy = world.alm.tile_center_at(to_tile_xy)

        next_tile_dxdy = to_tile_xy - from_tile_xy
        duration = math.hypot(*next_tile_dxdy) * TILE_SIZE

        self.progress = Progress(mobj.speed, 0, duration)
        self.callback = None

    def tick(self):
        mobj = self.mobj
        mobj.ai.angle = self.move_angle
        mobj.ai.sprite_kind = UnitSpriteKind.move

        self.progress.tick()
        factor = self.progress.progress
        mobj.xy = self.from_xy.lerp(self.to_xy, factor)
        frame_id = lerp(mobj.ai.move_begin_phases, mobj.ai.move_phases - 1, factor)
        mobj.frame_id = int(frame_id)

        if factor >= 1:
            # should be animation effect?
            self.callback()

            mobj.ai.sprite_kind = UnitSpriteKind.idle
            return True
        return False


class AttackTask:

    def __init__(self, mobj, target):
        self.mobj = mobj
        self.target = target

        self.progress = Progress(1 / mobj.ai.attack_phases, 0, mobj.ai.attack_phases)

    def tick(self):
        mobj = self.mobj
        mobj.ai.sprite_kind = UnitSpriteKind.attack
        mobj.ai.angle = movement.direction_to_tile(mobj.tile_xy, self.target.tile_xy)
        self.progress.tick()
        factor = self.progress.progress

        mobj.frame_id = int(lerp(0, mobj.ai.attack_phases - 1, factor))
        return factor > 1


class DieTask:

    def tick(self):
        mobj.ai.sprite_kind = UnitSpriteKind.die
        mobj.ai.angle = self.angle
        self._tick += 1
        if self._tick % 4 != 0:
            return False
        mobj.move_frame_id += 1
        if mobj.move_frame_id > 10:
            return True
        return False
