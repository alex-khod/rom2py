from typing import List, Type

from kaitaistruct import KaitaiStruct

from src.systems import tasks, movement, vision
from src.utils import Vec2


def move_callback(world, mobj, from_tile_xy, to_tile_xy):
    mobj.tile_xy = to_tile_xy
    world.units.layer[from_tile_xy] = None
    world.units.layer[to_tile_xy] = mobj

    world.vision.set_vision_at(mobj, from_tile_xy, scan_range=3, value=False)
    world.vision.set_vision_at(mobj, to_tile_xy, scan_range=3, value=True)
    x, y = to_tile_xy

    for other_mobj in world.vision.tiles[y][x]:
        if other_mobj.ai.state:
            continue
        state_class = other_mobj.ai.new_vision_state
        other_mobj.ai.state = state_class(other_mobj, world, other_mobj.tile_xy)
        world.think.add(other_mobj)


class AIState:
    pass


class AIStateIdle(AIState):

    def __init__(self, mobj):
        self.mobj = mobj

    def get_next_task(self):
        return None


from src import pathfind


class Pathfinder:
    def __init__(self, world: 'World', from_tile_xy, to_tile_xy):
        self.world = world
        self.path = None
        self.from_tile_xy = from_tile_xy
        self.to_tile_xy = to_tile_xy

    # def build_path(self, from_tile_xy, to_tile_xy):
    #     return pathfind.bfs(world.grid, from_tile_xy, to_tile_xy)

    def get_next_tile(self, from_tile_xy, to_tile_xy: Vec2):
        world = self.world
        path = pathfind.bfs(world.grid, from_tile_xy, to_tile_xy)
        if path:
            next_tile = Vec2(*path[-1])
            if not world.units.layer[next_tile]:
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
        task = tasks.MoveTask(mobj, mobj.tile_xy, next_tile, self.world)
        task.callback = lambda: move_callback(self.world, mobj, mobj.tile_xy, next_tile)
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

    def __init__(self, mobj, world, to_tile_xy):
        self.mobj = mobj
        self.world = world
        self.to_tile_xy = to_tile_xy
        self.pathfinder = Pathfinder(world, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        return self.pathfinder.get_movement_task(self.mobj, self.mobj.tile_xy, self.to_tile_xy)


class AIStateHoldPosition(AIState):
    """
        Attack anyone in attack range.
        If not possible, move one step closer to destination tile.
    """

    def __init__(self, mobj, world, to_tile_xy=None):
        self.mobj = mobj
        self.world = world
        self.to_tile_xy = to_tile_xy or mobj.tile_xy
        self.pathfinder = Pathfinder(world, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        mobj = self.mobj

        targets = self.world.vision.scan_surroundings(mobj, self.world, scan_range=3)
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

    def __init__(self, mobj, world, to_tile_xy=None):
        self.mobj = mobj
        self.world = world
        self.to_tile_xy = to_tile_xy or mobj.tile_xy
        self.pathfinder = Pathfinder(world, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        mobj = self.mobj
        targets = self.world.vision.scan_surroundings(mobj, self.world, scan_range=3)

        task = get_attack_task(mobj, targets)
        if task:
            return task

        if targets:
            target = targets.pop()
            return self.pathfinder.get_movement_task(self.mobj, self.mobj.tile_xy, target.tile_xy)

        return self.pathfinder.get_movement_task(self.mobj, self.mobj.tile_xy, self.to_tile_xy)
