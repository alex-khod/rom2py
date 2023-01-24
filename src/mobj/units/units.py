import math
from dataclasses import dataclass
from enum import IntEnum
import random
from typing import Tuple
from unittest.mock import Mock

from src.utils import Vec2

from src.systems import movement, DieTask

import pyglet
import os

from src.formats.alm2 import Alm2
from src.resources import Resources
from .animation import UnitAnimationSequencer, AnimRegistry, EAnimType, EDirection8, EDirection16

from profilehooks import timecall

from ..layer import Layer
from ...graphics.renderers.paletted import PalettedSprite

jn = os.path.join
MAP_PADDING = 8
TILE_SIZE = 32


def get_tile_xy(x, y):
    x = x >> 8
    y = y >> 8
    return x, y


class Unit(Alm2.UnitEntry):
    sprite: PalettedSprite
    direction = 0


class Units:

    def __init__(self, renderer):
        self.databin = Resources.special("data.bin").content
        self.unit_registry = Resources.special("units.reg").content
        # anim_registry = AnimRegistry()
        self.renderer = renderer
        self.graphics = renderer.graphics
        self.animations = {}
        self.palettes = {}
        self.unit_frames = {}

        self.prepare_units()
        # self.anim_showcase()
        self.sprites = None
        self.units = None
        self.layer = None

    def prepare_units(self):
        units_by_id = list(self.unit_registry.units_by_id.items())
        for utid, unit_record in units_by_id:
            key = "units\\" + unit_record["filename"] + ".256"
            frames = self.graphics[key]
            self.unit_frames[utid] = frames
            pal_key = "units\\" + os.path.dirname(unit_record["filename"]) + "\\"
            palette_paths = [key + "inner"] + [pal_key + "palette%d.pal" % i for i in range(2, 5)]

            palettes = []
            for path in palette_paths:
                try:
                    palettes.append(self.graphics[path])
                except KeyError:
                    pass
            self.palettes[utid] = palettes

        for utid, unit_record in units_by_id:
            self.animations[utid] = self.animations_for_utid(utid)

    def animations_for_utid(self, utid):
        unit_frames = self.unit_frames[utid]
        unit_record = self.unit_registry.units_by_id[utid]
        anim_seq = UnitAnimationSequencer(unit_frames, unit_record)

        dying_utid = unit_record["dying"]
        dying_frames = self.unit_frames[dying_utid]
        dying_record = self.unit_registry.units_by_id[dying_utid]
        death_seq = UnitAnimationSequencer(dying_frames, dying_record)

        animations = {}
        for atype in anim_seq.types:
            animations[atype] = {}
            for facing in anim_seq.facings_by_type(atype):
                seq = death_seq if atype in (atype.die, atype.bones) else anim_seq
                frames = seq.sequence(atype, facing)
                animation = None
                if len(frames) > 0:
                    frames = [pyglet.image.AnimationFrame(fr, 15 / 60) for fr in frames]
                    animation = pyglet.image.Animation(frames)
                animations[atype][facing] = animation
        return animations

    def anim_showcase(self):
        """
            Place every available animation on the map.
        """
        unit_registry = self.unit_registry
        units_by_id = list(unit_registry.units_by_id.items())

        tiles = 0
        x0 = 64
        y, y0 = 0, 0
        for utid, unit_record in units_by_id:
            for atype in EAnimType:
                for facing in UnitAnimationSequencer.facings_by_type(atype):
                    tiles = unit_record["tilesize"]
                    x = TILE_SIZE * tiles * facing.value + x0
                    y = TILE_SIZE * tiles * atype.value + y0
                    animation = self.animations[utid][atype][facing]
                    palette = self.palettes[utid][0]
                    if not animation:
                        print(
                            f"Empty animation: {unit_record['desctext']} id={unit_record['id']} atype={atype.name} facing={facing.name}")
                        break
                    image = animation.frames[0].image
                    sprite = self.renderer.add_sprite(x, y, animation=image, palette=palette)
                    sprite.animation = animation
                    self.sprites.append(sprite)
            y0 = y + TILE_SIZE * tiles

    @timecall
    def load_units(self, alm: Alm2):
        self.sprites = []
        self.units = []
        self.layer = Layer(alm.width, alm.height)

        for _, unit in enumerate(alm["units"].body.units):
            unit_template = self.databin.units_by_server_id[unit.server_id]
            utid = unit.type_id
            tile_x = unit.x >> 8
            tile_y = unit.y >> 8
            tile_xy = Vec2(tile_x, tile_y)
            direction = unit.direction

            animations = self.animations[utid]
            animation = animations[EAnimType.idle][direction]
            palettes = self.palettes[utid]
            palette_id = unit.face_id - 1 if unit.face_id - 1 < len(palettes) else 0
            palette = palettes[palette_id]

            image = animation
            image = animation.frames[0].image

            unit.tile_xy = tile_xy
            unit.xy = alm.tile_center_at(tile_xy)
            sprite = self.renderer.add_sprite(*unit.xy, animation=image, palette=palette)
            sprite.animation = animation

            from src.rects import Rect

            unit.rect = Rect(*unit.xy, *(unit.xy + Vec2(image.width, image.height)))

            self.sprites.append(sprite)

            # TODO in dire need of a factory
            unit.animations = animations
            unit.sprite = sprite
            unit.frame_id = 0
            unit.sprite_kind = movement.UnitSpriteKind.idle

            unit.dead = False

            ai = movement.UnitAi()

            unit_record = self.unit_registry.units_by_id[utid]
            ai.rotation_phases = len(EDirection16) * 16
            ai.move_begin_phases = unit_record["movebeginphases"]
            ai.move_phases = unit_record["movephases"]
            ai.attack_phases = unit_record["attackphases"]

            # unit.speed = 0.5
            unit.speed = unit_template.speed / 20 * 8
            unit.rot_speed = unit.speed * 4

            unit.ai = ai
            unit.EID = "u%d" % unit.unit_id

            def unit_redraw(unit: Unit):
                state = unit.ai.sprite_kind
                divisor = 16 if state.name == "idle" else 32
                angle = unit.ai.angle // divisor
                state_animations = unit.animations[state]
                angle = min(angle, len(state_animations) - 1)
                angle_animations = state_animations[angle]

                frame_id = unit.frame_id % len(angle_animations.frames)
                frame = angle_animations.frames[frame_id]
                texture = frame.image

                unit.sprite.x = unit.xy.x
                unit.sprite.y = unit.xy.y
                unit.sprite.z = unit.xy.y / (alm.height * 32) * 256
                # unit.sprite.z = 1 - unit.xy.y / (alm.height * 32)
                unit.sprite._set_texture(texture)
                unit.sprite._update_position()

                self.renderer.redraw_shadow(unit.sprite)

            unit.redraw = unit_redraw.__get__(unit, Unit)

            self.units.append(unit)
            self.layer[tile_xy] = unit
