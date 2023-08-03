import math

from src.formats.alm2 import TILE_SIZE
from src.systems.animations.units import EAnimType
from src.systems import movement
from src.utils import Vec2, lerp

class Progress:
    def __init__(self, speed=1, elapsed=0, duration=60):
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
        # self.game = game
        self.angle_diff = movement.angle_diff_shortest(from_angle, to_angle)
        self.final_angle = self.from_angle + self.angle_diff
        self.progress = Progress(mobj.rot_speed, from_angle, self.final_angle)
        # game.events.dispatch_event("on_rotation_start", mobj, from_angle, to_angle)
        mobj.sprite_kind = EAnimType.idle
        self.mobj.frame_id = 0

    def tick(self):
        mobj = self.mobj
        self.progress.tick()
        factor = self.progress.progress
        angle = lerp(self.from_angle, self.final_angle, factor)
        # self.game.events.dispatch_event("on_rotation", mobj, self.from_angle, self.to_angle, factor)

        mobj.ai.angle = int(angle) % mobj.ai.rotation_phases
        if factor >= 1:
            # self.game.events.dispatch_event("on_rotation_end", mobj, self.from_angle, self.to_angle, factor)
            mobj.ai.angle = self.to_angle
            return True
        return False


class MoveTask:
    ticks_per_move = 4

    def __init__(self, mobj, from_tile_xy, to_tile_xy, game: 'BattleGame'):
        self.mobj = mobj
        self.from_tile_xy = from_tile_xy
        self.to_tile_xy = to_tile_xy
        self.game = game
        next_tile_dxdy = to_tile_xy - from_tile_xy
        duration = math.hypot(*next_tile_dxdy) * TILE_SIZE
        game.events.dispatch_event("on_movement_start", mobj, from_tile_xy, to_tile_xy)

        self.progress = Progress(1, 0, int(duration / mobj.speed))

    def tick(self):
        mobj = self.mobj
        self.progress.tick()
        factor = self.progress.progress
        self.game.events.dispatch_event("on_movement", mobj, self.from_tile_xy, self.to_tile_xy, factor)
        if factor >= 1:
            self.game.events.dispatch_event("on_movement_end", mobj, self.from_tile_xy, self.to_tile_xy)
            return True
        return False


class AttackTask:

    def __init__(self, mobj, target):
        self.mobj = mobj
        self.target = target

        self.progress = Progress(1, 0, mobj.ai.attack_phases)

    def tick(self):
        mobj = self.mobj
        mobj.ai.sprite_kind = EAnimType.attack
        mobj.ai.angle = movement.direction_to_tile(mobj.tile_xy, self.target.tile_xy)
        self.progress.tick()
        factor = self.progress.progress

        mobj.frame_id = int(lerp(0, mobj.ai.attack_phases - 1, factor))
        return factor > 1


class DieTask:

    def __init__(self, mobj):
        self.mobj = mobj

    def tick(self):
        mobj.ai.sprite_kind = EAnimType.die
        mobj.ai.angle = self.angle
        self._tick += 1
        if self._tick % 4 != 0:
            return False
        mobj.move_frame_id += 1
        if mobj.move_frame_id > 10:
            return True
        return False
