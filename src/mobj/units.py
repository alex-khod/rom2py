import math
from dataclasses import dataclass
from enum import IntEnum
import random
from typing import Tuple, Union, List

from src.utils import Vec2
from src.systems import movement

import os

from src.formats.alm2 import Alm2
from src.formats.databin import DataBin
from src.resources import Resources
from src.systems.animations.units import EAnimType, EDirection16
from ..formats.registry import UnitRegistry

from profilehooks import timecall

from .layer import Layer
from ..systems.think import UnitAi

jn = os.path.join
MAP_PADDING = 8


def get_tile_xy(x, y):
    x = x >> 8
    y = y >> 8
    return x, y


class DummyUnitEntry:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.type_id = 64
        self.server_id = 1
        self.face_id = 0
        self.unit_id = 0


class DummyTemplate:

    def __init__(self):
        self.speed = 20


class MapUnit(Alm2.UnitEntry):
    record: "UnitRecord"
    template: Union["DataBin.TMonster", "DataBin.THuman"]
    direction = 0
    EID: int

    @property
    def eid(self):
        return self.EID

    # def __hash__(self):
    #     return self.EID

    def __init__(self, alm_unit: Alm2.UnitEntry, registry: "UnitRegistry", databin):
        unit = alm_unit

        self.x = unit.x >> 8
        self.y = unit.y >> 8
        self.record = registry.units_by_id[unit.type_id]
        self.template = databin.units_by_server_id[unit.server_id]

        self.face_id = unit.face_id
        self.type_id = unit.type_id
        self.frame_id = 0
        self.sprite_kind = EAnimType.idle

        self.is_dead = False

        ai = UnitAi()
        ai.rotation_phases = len(EDirection16) * 16

        self.rot_speed = self.template.speed * 4

        self.ai = ai
        self.EID = "u%d" % unit.unit_id
        self.vision = set()
        self.offset_xy = Vec2(0, 0)

    @property
    def tile_xy(self):
        x = self.x
        y = self.y
        return Vec2(x, y)

    @tile_xy.setter
    def tile_xy(self, value: Vec2):
        self.x, self.y = value

    @property
    def speed(self):
        speed = self.template.speed / 20 * 8
        return speed


@dataclass
class UnitStats:

    def __init__(self):
        pass

    @classmethod
    def from_template(cls, template):
        template = template


class MapUnits:
    units: List["MapUnit"]

    def __init__(self):
        self.databin = Resources.special("data.bin").content
        self.unit_registry = Resources.special("units.reg").content
        # anim_registry = AnimationRegistry()
        self.animations = {}
        self.palettes = {}
        self.unit_frames = {}

        self.units = []
        self.layer = None

    @timecall
    def load_units(self, alm: Alm2):
        self.units = []
        self.layer = Layer(alm.width, alm.height)
        registry = Resources.special("units.reg").content
        databin = Resources.special("data.bin").content

        for _, alm_unit in enumerate(alm["units"].body.units):
            map_unit = MapUnit(alm_unit, registry, databin)
            self.units.append(map_unit)
        alm_unit = alm["units"].body.units[0]
        alm_unit.type_id = 1
        alm_unit.x += 1 << 8
        map_unit = MapUnit(alm_unit, registry, databin)
        self.units.append(map_unit)

    def on_add_unit(self, unit):
        self.layer[unit.tile_xy] = unit

    def on_movement_end(self, unit, from_tile_xy, to_tile_xy):
        self.layer[from_tile_xy] = None
        self.layer[to_tile_xy] = unit
        unit.tile_xy = to_tile_xy

    def on_remove_unit(self, unit):
        self.layer[unit.tile_xy] = None
