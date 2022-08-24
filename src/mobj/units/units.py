import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple

from src.utils import Vec2

from src.systems import movement

import pyglet
import os

from src.formats.alm2 import Alm2
from src.resources import Resources
from .animation import UnitAnimationSequencer, AnimRegistry, EAnimType, EDirection8, EDirection16

from profilehooks import timecall

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

    def __init__(self, alm, renderer):
        self.alm = alm

        self.databin = Resources.special("data.bin").content
        self.unit_registry = Resources.special("units.reg").content
        # anim_registry = AnimRegistry()
        self.renderer = renderer
        self.graphics = renderer.graphics
        self.sprites = []
        self.animations = {}
        self.palettes = {}
        self.unit_frames = {}

        self.prepare_units()
        # self.anim_showcase()

        self.units = []
        w, h = alm.width, alm.height
        self.unit_map = [[None for _ in range(w)] for _ in range(h)]
        self.load_units(alm)

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
        for _, unit in enumerate(alm["units"].body.units):
            unit_template = self.databin.units_by_server_id[unit.server_id]
            utid = unit.type_id
            palette_id = 0
            tile_x = unit.x >> 8
            tile_y = unit.y >> 8
            direction = unit.direction
            x = tile_x * TILE_SIZE + TILE_SIZE // 2
            y = tile_y * TILE_SIZE + TILE_SIZE // 2

            animations = self.animations[utid]
            animation = animations[EAnimType.idle][direction]
            palettes = self.palettes[utid]
            palette_id = unit.face_id - 1 if unit.face_id - 1 < len(palettes) else 0
            palette = palettes[palette_id]
            image = animation
            image = animation.frames[0].image

            avg_height = alm.tile_avg_heights_at(tile_x, tile_y)
            sprite = self.renderer.add_sprite(x, y - avg_height, animation=image, palette=palette)
            sprite.animation = animation
            self.sprites.append(sprite)

            # TODO in dire need of a factory
            unit.animations = animations
            unit.sprite = sprite
            unit.frame_id = 0
            unit.state = movement.UnitAiStates.idle
            unit.move_frame_id = 0
            ai = movement.UnitAi()
            ai.angle = unit.direction
            walk_ai = ai.walk_ai

            unit_record = self.unit_registry.units_by_id[utid]

            walk_ai.rotation_phases = len(EDirection16)
            walk_ai.move_begin_phases = unit_record["movebeginphases"]
            walk_ai.move_phases = len(animations[EAnimType.move][0].frames)
            walk_ai.tile_xy = Vec2(tile_x, tile_y)
            walk_ai.xy = Vec2(x, y)
            walk_ai.height = avg_height
            walk_ai.frame_id = 0

            unit.ai = ai
            unit.EID = "u%d" % unit.unit_id

            def unit_redraw(unit: Unit):
                state = unit.ai.state
                angle = unit.ai.angle
                state_animations = unit.animations[state]
                angle_animations = state_animations[angle]

                frame_id = unit.move_frame_id % len(angle_animations.frames)
                frame = angle_animations.frames[frame_id]
                texture = frame.image

                height = unit.ai.walk_ai.height
                sprite_xy = unit.ai.walk_ai.xy
                unit.sprite.x = sprite_xy.x
                unit.sprite.y = sprite_xy.y - height
                unit.sprite._set_texture(texture)
                unit.sprite._update_position()

                self.renderer.redraw_shadow(unit.sprite)

            unit.redraw = unit_redraw

            self.units.append(unit)
            self.unit_map[tile_y][tile_x] = unit

    def render(self):
        self.batch.draw()
