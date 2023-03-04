import pyglet
import os
import random
import itertools
from enum import IntEnum

from profilehooks import timecall

from src.resources import Resources
from .cache import UnitsCache


class EAnimType(IntEnum):
    idle = 0
    move = 1
    attack = 2
    die = 3
    bones = 4


class EDirection(IntEnum):
    pass


class EDirection8(EDirection):
    # ↓ ↙ ← ↖ ↑ ↗ → ↘
    down = 0  # ↓
    downleft = 1  # ↙
    left = 2  # ←
    upleft = 3  # ↖
    up = 4  # ↑
    upright = 5  # ↗
    right = 6  # →
    downright = 7  # ↘

    flip_x_start = 4


class EDirection16(EDirection):
    down = 0  # ↓
    downleft = 2  # ↙
    left = 4  # ←
    upleft = 6  # ↖
    up = 8  # ↑
    upright = 10  # ↗
    right = 12  # →
    downright = 14  # ↘

    flip_x_start = 8

    down0 = 0  # ↓
    down22 = 1
    down45 = 2  # ↙
    down67 = 3
    down90 = 4  # ←
    down112 = 5
    down135 = 6  # ↖
    down157 = 7
    down180 = 8  # ↑
    down202 = 9
    down225 = 10  # ↗
    down247 = 11
    down270 = 12  # →
    down292 = 13
    down315 = 14  # ↘
    down337 = 15


assert len(EDirection16) == 16


class UnitAnimationSequencer:
    """
    The class retrieves frame_ids or frames themselves for animations.
    Length of animations is defined by 1) unit_record, a part of units registry "units.reg"
    2) Unit's associated .256 sprite, defined in unit_record.

    The .256 sprite for a unit is a collection of frames, ordered in 5 groups - idle, move, attack, die, bones,
    that represent a particular animation type.
    Groups themselves are ordered in by direction - a complete animation for direction 0, then direction 1, etc.
    Idle group has either 9 or 16 directions (depending on horizontal flip x_flip flag of the unit_record).
    Direction 0 corresponds to a unit that faces downwards, and then 1 and subsequent directions correspond to
    clockwise direction with some angle: ↓ ↙ ← ↖ ↑ ↗ → ↘.

    1. Idle group, just one frame of a unit looking in a particular direction, per direction.
    There are 16 or 9 directions for this group, depending on x_flip. The directions correspond to EDirection16 enum.

    If x_flip is off, there is 16 directions and 16 frames for the group.
    If x_flip flag is on, then the sprite is deemed symmetrical and just 9 directions (0..8) are stored in .256 file.
    The rest is obtained by flipping the already existing frames: direction 9 is obtained from flipping frame 7,
    10 - frame 6, and so on.

    2. Move, moving animation group. Moving animations start at next frame index after Idle group.
        The count of frames for each animation is mphases=(movebeginphases + movephases).
        Animations come in 8 or 5 directions (EDirection8 enum), depending on x_flip flag.
        First there is entire moving animation for direction 0, then animation for direction 1, etc.
        So with a hypothetical animation with mphases 2, frames will be faced to: ↓ ↓ ↙ ↙ ← ←...

    3. Attack animation group. Length for each animation is attackphases. Start after all the frames of move animations.
    4. Die, dying animation group. Length for each animation is dyingphases.
    5. Bones, remains animation group. Length for each animation is bonephases.
    """

    types = EAnimType
    facings = EDirection8

    def __init__(self, unit_frames, unit_record):
        self.unit_record = unit_record
        self.unit_frames = unit_frames

        self._has_dying_anim = not ('dying' in unit_record and unit_record["dying"] != unit_record["id"])

        moves = unit_record['movephases']
        movestart = unit_record['movebeginphases']
        attacks = unit_record['attackphases']
        deaths = unit_record['dyingphases']
        bones = unit_record['bonephases']

        self.x_flip = int('flip' in unit_record and unit_record['flip'])

        # len(↙ ← ↖) = 3 directions are flipped
        facings_sans_flip = len(EDirection8) - self.x_flip * 3
        # len(↖ * 3, ←, ↙ * 3) = 7 directions are flipped
        idle_facings_sans_flip = len(EDirection16) - self.x_flip * 7

        length = [1, movestart + moves, attacks, deaths, bones]
        facings = [idle_facings_sans_flip, facings_sans_flip, facings_sans_flip, facings_sans_flip,
                   facings_sans_flip]
        offsets = [0] + [dirs * length for dirs, length in zip(facings, length)]
        offsets = list(itertools.accumulate(offsets))

        atypes = list(EAnimType)
        length_by_type = dict(zip(atypes, length))
        offsets_by_type = dict(zip(atypes, offsets))
        self.length_by_type = length_by_type
        self.offsets_by_type = offsets_by_type

    @classmethod
    def facings_by_type(cls, atype: EAnimType):
        return EDirection16 if atype == EAnimType.idle else EDirection8

    def offset(self, atype: EAnimType, facing: int):
        total_facings = len(self.facings_by_type(atype=atype))
        flipstart = total_facings // 2
        if self.x_flip and facing > flipstart:
            # 8-facings: facing 5 same as 3, 6 as 2, 7 as 1
            # 16-facings: 9 as 7, 10 as 6, 11 as 5, etc.
            facing = total_facings - facing
        return self.offsets_by_type[atype] + facing * self.length_by_type[atype]

    def frameids(self, atype: EAnimType, facing: int):
        offset = self.offset(atype, facing)
        movestart = self.unit_record['movebeginphases']
        if atype == EAnimType.move:
            frameids = list(range(movestart)) + [fidx + movestart for fidx in self.unit_record['moveanimframe']]
        elif atype == EAnimType.attack:
            frameids = self.unit_record['attackanimframe']
        elif atype in (EAnimType.die, EAnimType.bones):
            if not self._has_dying_anim:
                text = self.unit_record["desctext"]
                id = self.unit_record["id"]
                raise Exception(f"{id} ({text}) Don't know how to - \"die\"")
            frameids = list(range(self.length_by_type[atype]))
        else:
            # idle probably
            if atype not in EAnimType:
                raise KeyError("Unknown atype %d " % atype)
            frameids = list(range(self.length_by_type[atype]))
        frameids = list(map(lambda fidx: fidx + offset, frameids))
        return frameids

    def sequence(self, atype: EAnimType, facing: int):
        unit_frames = self.unit_frames
        frameids = self.frameids(atype, facing)
        total_facings = len(self.facings_by_type(atype=atype))
        flipstart = total_facings // 2
        frames = []
        for idx in frameids:
            frame = unit_frames[idx]
            record = self.unit_record
            w, h = record["width"], record["height"]
            cx, cy = record["centerx"], record["centery"]
            frame.anchor_x = cx + (-w + frame.width) // 2
            frame.anchor_y = cy + (-h + frame.height) // 2
            x_flip = int(self.x_flip and facing > flipstart)
            # NOOOO that shouldn't have happened. Sequencer shouldn't need to know HOW to flip the image,
            # only that it needs to be flipped. Oh well...
            if x_flip:
                frame = frame.get_transform(flip_x=True)
            frames.append(frame)
        return frames


class AnimRegistry:
    _cache = None

    @timecall
    def __init__(self, unit_registry=None):
        if not self.__class__._cache is None:
            return
        # broken

        # if unit_registry is None:
        #     unit_registry = Resources.special('units.reg').content
        # self.unit_registry = unit_registry
        #
        # units_by_id = unit_registry.units_by_id
        # animstate_by_id = {}
        # anim_by_id = {}
        #
        # for type_id, unit_record in units_by_id.items():
        #     filename = unit_record["filename"]
        #     unit256 = Resources["graphics", "units", filename + '.256'].content
        #     unit256._cache = UnitsCache()[filename]
        #     animstate_by_id[type_id] = AnimState(unit_record, unit256)
        #     anim_by_id[type_id] = PygletAnim(unit_record, unit256)
        #
        # for type_id, unit_record in units_by_id.items():
        #     if 'dying' in unit_record and unit_record["dying"] != unit_record["id"]:
        #         dying_id = unit_record['dying']
        #         animstate_by_id[type_id].dyinganim = animstate_by_id[dying_id]
        #         anim_by_id[type_id].dyinganim = animstate_by_id[dying_id]
        #
        # pyg_anim_by_id = {}
        # self.texture_bin = pyglet.image.atlas.TextureBin()
        # for type_id, unit_record in units_by_id.items():
        #     anim = anim_by_id[type_id]
        #     pyg_anim_by_id[type_id] = {}
        #     for atype in anim.types:
        #         pyg_anim_by_id[type_id][atype] = {}
        #         for facing in anim.facings_by_type(atype):
        #             pyg_anim_by_id[type_id][atype][facing] = anim.animation(atype, facing, self.texture_bin)
        #
        # self.animstate_by_id = animstate_by_id
        # self.anim_by_id = anim_by_id
        # self.pyg_anim_by_id = pyg_anim_by_id

    def __getitem__(self, key):
        if type(key) is int:
            type_id = key
            return self.animstate_by_id[type_id]
        elif type(key) is tuple:
            type_id, atype, facing = key
            return self.pyg_anim_by_id[type_id][atype][facing]
        raise KeyError("Can't handle key: %s" % key)
