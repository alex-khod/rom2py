import pyglet
import os

from src.resources import Resources
from .animation import UnitAnimationSequencer, AnimRegistry, EAnimType, EFacing, EIdleFacing

from profilehooks import timecall

jn = os.path.join
import numpy as np

MAP_PADDING = 8
TILE_SIZE = 32


class Units:

    def __init__(self, alm, renderer):
        self.alm = alm

        self.databin = Resources.special("data.bin").content
        self.unit_registry = Resources.special("units.reg").content
        # anim_registry = AnimRegistry()
        self.batch = pyglet.graphics.Batch()
        self.renderer = renderer
        self.animations = {}
        self.sprites = []
        self.unit_frames = {}

        self.prepare_units()
        self.anim_showcase()

    @timecall
    def prepare_units(self):
        monsters_by_type_id = self.databin.monsters_by_type_id
        units_by_id = list(self.unit_registry.units_by_id.items())[:16]
        for uid, unit_record in units_by_id:
            a256 = Resources["graphics", "units", unit_record["filename"] + ".256"].content
            a256_frames = self.renderer.a256_to_frames(a256=a256, record=unit_record, sprite_key=uid)
            self.renderer.prepare_palette(a256.palette, palette_key=uid)
            self.unit_frames[uid] = a256_frames

        for uid, unit_record in units_by_id:
            self.animations[uid] = self.animations_for_uid(uid)

        print(
            f"VRAM consumed: real {self.renderer.mem_usage_real / 1024 / 1024:.2f} total {self.renderer.mem_usage_total / 1024 / 1024 :.2f} mb")

    def animations_for_uid(self, uid):
        unit_frames = self.unit_frames[uid]
        unit_record = self.unit_registry.units_by_id[uid]
        anim_seq = UnitAnimationSequencer(unit_frames, unit_record)

        dying_id = unit_record["dying"]
        dying_frames = self.unit_frames[dying_id]
        dying_record = self.unit_registry.units_by_id[dying_id]
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
        units_by_id = list(unit_registry.units_by_id.items())[:16]

        x0 = 64
        y0 = 0
        for uid, unit_record in units_by_id:
            for atype in EAnimType:
                for facing in UnitAnimationSequencer.facings_by_type(atype):
                    tiles = unit_record["tilesize"]
                    x = TILE_SIZE * tiles * facing.value + x0
                    y = TILE_SIZE * tiles * atype.value + y0
                    anim = self.animations[uid][atype][facing]
                    if not anim:
                        print(
                            f"Empty animation: {unit_record['desctext']} id={unit_record['id']} atype={atype.name} facing={facing.name}")
                        continue
                    sprite = self.renderer.add_sprite(anim, x, y, palette_key=uid)
                    self.sprites.append(sprite)
            y0 = y + TILE_SIZE * tiles

    def render(self):
        self.batch.draw()
