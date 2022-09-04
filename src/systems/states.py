from src.systems import tasks, movement, vision


def move_callback(world, mobj, from_tile_xy, to_tile_xy):
    mobj.tile_xy = to_tile_xy
    world.units.layer[from_tile_xy] = None
    world.units.layer[to_tile_xy] = mobj

    world.vision.set_vision_at(mobj, from_tile_xy, scan_range=3, value=False)
    world.vision.set_vision_at(mobj, to_tile_xy, scan_range=3, value=True)
    x, y = to_tile_xy

    for other_mobj in world.vision.tiles[y][x]:
        other_mobj.ai.state = AIStateHoldPosition(other_mobj, world, other_mobj.tile_xy)
        world.think.add(other_mobj)


class AIState:
    pass


class AIStateIdle(AIState):

    def __init__(self, mobj):
        self.mobj = mobj

    def get_next_task(self):
        return None


class AIStateMove(AIState):
    def __init__(self, mobj, world, to_tile_xy):
        self.mobj = mobj
        self.world = world
        self.to_tile_xy = to_tile_xy
        self.pathfinder = movement.Pathfinder(world, mobj.tile_xy, to_tile_xy)

    def get_next_task(self):
        next_tile = self.pathfinder.get_next_tile(self.to_tile_xy)
        if not next_tile:
            return None

        mobj = self.mobj
        angle = mobj.ai.angle
        next_angle = movement.direction_to_tile(mobj.tile_xy, next_tile)
        rotation_phases = mobj.ai.rotation_phases
        if rotation_phases and angle != next_angle:
            task = tasks.RotateTask(mobj, angle, next_angle)
            # print(f"rotate from {angle} to {next_angle}")
            return task

        self.pathfinder.path.pop()

        task = tasks.MoveTask(mobj, mobj.tile_xy, next_tile, self.world)
        task.callback = lambda: move_callback(self.world, mobj, mobj.tile_xy, next_tile)
        # print(f"move from {mobj.tile_xy} to {next_tile}")
        return task


class AIStateHoldPosition(AIState):
    def __init__(self, mobj, world, to_tile_xy=None):
        self.mobj = mobj
        self.world = world
        self.to_tile_xy = to_tile_xy or mobj.tile_xy

    def get_next_task(self):
        mobj = self.mobj
        targets = self.world.vision.scan_surroundings(mobj, self.world)
        # sorted(targets, key=lambda t: max((mobj.tile_xy - t.tile_xy)))
        if not targets:
            return None

        target = targets.pop()
        task = tasks.AttackTask(mobj, target)
        return task
