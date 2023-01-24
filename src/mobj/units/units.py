import pyglet
import os

from src.resources import Resources
from .animation import UnitAnimationSequencer, AnimRegistry, EAnimType, EFacing, EIdleFacing

from profilehooks import timecall

jn = os.path.join
MAP_PADDING = 8
TILE_SIZE = 32


class Units:

    def __init__(self, alm, renderer, graphics):
        self.alm = alm

        self.graphics = graphics
        self.databin = Resources.special("data.bin").content
        self.unit_registry = Resources.special("units.reg").content
        # anim_registry = AnimRegistry()
        self.batch = pyglet.graphics.Batch()
        self.renderer = renderer
        self.sprites = []
        self.animations = {}
        self.palettes = {}
        self.unit_frames = {}

        self.prepare_units()
        self.anim_showcase()
        self.load_units(alm)

    @timecall
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
                except KeyError as e:
                    print(e)
                    pass
            self.palettes[utid] = palettes

        for utid, unit_record in units_by_id:
            self.animations[utid] = self.animations_for_utid(utid)

    def animations_for_utid(self, utid):
        unit_frames = self.unit_frames[utid]
        unit_record = self.unit_registry.units_by_id[utid]
        anim_seq = UnitAnimationSequencer(unit_frames, unit_record)

        dying_tid = unit_record["dying"]
        dying_frames = self.unit_frames[dying_tid]
        dying_record = self.unit_registry.units_by_id[dying_tid]
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

        x0 = 64
        y0 = 0
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

    def load_units(self, alm):
        for _, unit in enumerate(alm["units"].body.units):
            unit_template = self.databin.units_by_server_id[unit.server_id]
            utid = unit.type_id
            palette_id = 0
            tile_x = unit.x >> 8
            tile_y = unit.y >> 8
            direction = unit.direction
            x = tile_x * TILE_SIZE + TILE_SIZE // 2
            y = tile_y * TILE_SIZE + TILE_SIZE // 2

            try:
                animation = self.animations[utid][EAnimType.idle][direction]
                palettes = self.palettes[utid]
                palette_id = unit.face_id - 1 if unit.face_id - 1 < len(palettes) else 0
                palette = palettes[palette_id]
                image = animation
                image = animation.frames[0].image
                sprite = self.renderer.add_sprite(x, y, animation=image, palette=palette)
                sprite.animation = animation
                self.sprites.append(sprite)
            except KeyError:
                print(f"No anim for utid {utid}")

    def render(self):
        self.batch.draw()
