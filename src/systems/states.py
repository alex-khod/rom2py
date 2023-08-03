from typing import List, Type

from kaitaistruct import KaitaiStruct

from src.systems import tasks, movement, vision, pathfind
from src.utils import Vec2

class AIState:
    pass


class AIStateIdle(AIState):

    def __init__(self, mobj):
        self.mobj = mobj

    def get_next_task(self):
        return None


class Pathfinder:
    def __init__(self, game: 'game', from_tile_xy, to_tile_xy):
        self.game = game
        self.path = None
        self.from_tile_xy = from_tile_xy
        self.to_tile_xy = to_tile_xy

    # def build_path(self, from_tile_xy, to_tile_xy):
    #     return pathfind.bfs(game.grid, from_tile_xy, to_tile_xy)

    def get_next_tile(self, from_tile_xy, to_tile_xy: Vec2):
        game = self.game
        path = pathfind.bfs(game.grid.grid, from_tile_xy, to_tile_xy)
        if path:
            next_tile = Vec2(*path[-1])
            print(next_tile)
            if not game.units.layer[next_tile]:
                return next_tile
        return None
        # if self.to_tile_xy == to_tile_xy:
        #     if self.path:
        #         return Vec2(*self.path[-1])
        #     return None
        raise NotImplementedError

    def get_movement_task(self, mobj, from_tile_xy, to_tile_xy):
        next_tile = self.get_next_tile(from_tile_xy, to_tile_xy)
        if not next_tile:
            return None

        angle = mobj.ai.angle
        next_angle = movement.direction_to_tile(mobj.tile_xy, next_tile)
        rotation_phases = mobj.ai.rotation_phases
        if rotation_phases and angle != next_angle:
            task = tasks.RotateTask(mobj, angle, next_angle)
            # print(f"rotate from {angle} to {next_angle}")
            return task

        # self.path.pop()
        task = tasks.MoveTask(mobj, mobj.tile_xy, next_tile, self.game)
        # print(f"move from {mobj.tile_xy} to {next_tile}")
        return task


def get_attack_task(mobj, targets: List[Type[KaitaiStruct]]):
    attack_range = mobj.range
    can_attack = list(filter(lambda t: t.tile_xy.max_dxdy(mobj.tile_xy) <= (attack_range), targets))
    if can_attack:
        target = can_attack.pop()
        task = tasks.AttackTask(mobj, target)
        return task


class AIStateMove(AIState):
    """
        Move one step closer to destination tile.
    """

    def __init__(self, mobj, game, to_tile_xy):
        self.mobj = mobj
        self.game = game
        self.to_tile_xy = to_tile_xy
        self.pathfinder = Pathfinder(game, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        return self.pathfinder.get_movement_task(self.mobj, round(self.mobj.tile_xy), self.to_tile_xy)


class AIStateHoldPosition(AIState):
    """
        Attack anyone in attack range.
        If not possible, move one step closer to destination tile.
    """

    def __init__(self, mobj, game, to_tile_xy=None):
        self.mobj = mobj
        self.game = game
        self.to_tile_xy = to_tile_xy or mobj.tile_xy
        self.pathfinder = Pathfinder(game, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        mobj = self.mobj

        targets = self.game.vision.scan_surroundings(mobj, self.game, scan_range=3)
        task = get_attack_task(mobj, targets)
        if task:
            return task

        return self.pathfinder.get_movement_task(self.mobj, self.mobj.tile_xy, self.to_tile_xy)


class AIStateGuard(AIState):
    """
        Attack anyone in attack range.
        If not possible, move one step closer to any visible enemy.
        If not possible, move one step closer to destination tile.
    """

    def __init__(self, mobj, game, to_tile_xy=None):
        self.mobj = mobj
        self.game = game
        self.to_tile_xy = to_tile_xy or mobj.tile_xy
        self.pathfinder = Pathfinder(game, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        mobj = self.mobj
        targets = self.game.vision.scan_surroundings(mobj, self.game, scan_range=3)

        task = get_attack_task(mobj, targets)
        if task:
            return task

        if targets:
            target = targets.pop()
            return self.pathfinder.get_movement_task(self.mobj, self.mobj.tile_xy, target.tile_xy)

        return self.pathfinder.get_movement_task(self.mobj, self.mobj.tile_xy, self.to_tile_xy)
