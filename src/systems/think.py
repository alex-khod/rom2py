from collections import deque
from dataclasses import dataclass
from typing import Tuple

from src.systems.tasks import UnitSpriteKind
from src.systems import states
from src.utils import Vec2


@dataclass
class UnitAi:
    sprite_kind = UnitSpriteKind.idle
    state: "UnitAiState"
    target = None
    tasks = None
    dead = False

    def __init__(self):
        self.state = None
        self.tasks = deque()
        self.angle = 0


class ThinkSystem:
    think_stuff = None
    world: 'World'

    def __init__(self, world):
        self.world = world
        self.think_stuff = {}
        self.to_add = []

    def add(self, mobj):
        self.to_add.append(mobj)

    def move_to_tile_xy(self, mobj, to_tile_xy: Tuple[int, int]):
        world = self.world
        to_tile_xy = Vec2(*to_tile_xy)
        mobj.ai.state = states.AIStateMove(mobj, world, to_tile_xy)
        self.add(mobj)

    def tick(self):
        think_stuff = self.think_stuff
        to_pop = []
        for EID, mobj in think_stuff.items():
            if not mobj.ai.tasks:
                if mobj.ai.state:
                    task = mobj.ai.state.get_next_task()
                    if task:
                        mobj.ai.tasks.append(task)
            while mobj.ai.tasks and mobj.ai.tasks[0].tick():
                mobj.ai.tasks.popleft()

        for EID in to_pop:
            think_stuff.pop(EID)

        for mobj in self.to_add:
            think_stuff[mobj.EID] = mobj
