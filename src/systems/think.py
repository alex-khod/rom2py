from collections import deque
from dataclasses import dataclass
from typing import Tuple

from src.systems.animations.units import EAnimType
from src.systems import states
from src.utils import Vec2


@dataclass
class UnitAi:
    sprite_kind = EAnimType.idle
    state: "UnitAiState"
    target = None
    tasks = None
    dead = False
    new_vision_state = states.AIStateGuard

    def __init__(self):
        self.state = None
        self.tasks = deque()
        self.angle = 0


class ThinkSystem:
    thinkers = None
    world: 'World'

    def __init__(self, world):
        self.world = world
        self.thinkers = {}
        self.to_add = []

    def add(self, mobj):
        self.to_add.append(mobj)

    def move_to_tile_xy(self, mobj, to_tile_xy: Tuple[int, int]):
        world = self.world
        to_tile_xy = Vec2(*to_tile_xy)
        mobj.ai.state = states.AIStateMove(mobj, world, to_tile_xy)
        self.add(mobj)

    def tick(self):
        thinkers = self.thinkers
        to_pop = []
        for EID, mobj in thinkers.items():
            if not mobj.ai.tasks:
                if mobj.ai.state:
                    task = mobj.ai.state.get_next_task()
                    if task:
                        mobj.ai.tasks.append(task)
                if not mobj.ai.tasks:
                    to_pop.append(mobj.EID)
                    print("POP", mobj)
                    mobj.sprite_kind = EAnimType.idle
                    mobj.frame_id = 0
            while mobj.ai.tasks and mobj.ai.tasks[0].tick():
                mobj.ai.tasks.popleft()

        for EID in to_pop:
            thinkers.pop(EID)

        for mobj in self.to_add:
            thinkers[mobj.EID] = mobj
        self.to_add.clear()
