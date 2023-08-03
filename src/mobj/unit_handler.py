import os

import pyglet.sprite
from pyglet.math import Vec4

from src.formats.alm2 import Alm2
from src.graphics.object_pool import ObjectPool
from src.graphics.registry import TextureRegistry
from src.graphics.renderers.paletted import PalettedSprite
from src.mobj.units import MapUnit
from src.systems import movement
from src.systems.animations.units import AnimationRegistry, EAnimType
from collections import defaultdict
from src.utils import Vec2
from pyglet.gl import *

from src.systems.battle_game import BattleGame


class SpatialHash:

    def __init__(self, cell_size=64):
        self._cells = defaultdict(set)
        self._cell_size = cell_size
        self._keys = {}

    def _hash(self, x, y):
        return int(x / self._cell_size), int(y / self._cell_size)

    def add_at(self, item, aabb):
        min_vec, max_vec = self._hash(*aabb[0:2]), self._hash(*aabb[2:4])
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                self._cells[(i, j)].add(item)
        self._keys[item] = aabb

    def remove(self, item):
        aabb = self._keys[item]
        self.remove_at(item, aabb)

    def remove_at(self, item, aabb):
        min_vec, max_vec = self._hash(*aabb[0:2]), self._hash(*aabb[2:4])
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                self._cells[(i, j)].remove(item)

    def get(self, aabb):
        min_vec, max_vec = self._hash(*aabb[0:2]), self._hash(*aabb[2:4])
        items = set()
        for i in range(min_vec[0], max_vec[0] + 1):
            for j in range(min_vec[1], max_vec[1] + 1):
                items = items.union(self._cells[(i, j)])
        return items


class Palettes:

    def __init__(self, game: BattleGame):
        self.units_by_id = game.units.unit_registry.units_by_id
        self.textures = TextureRegistry.get_instance()
        self.palettes = {}
        self.palette_tex = None
        self.get_palettes()

    def get_palettes(self):
        for utid, unit_record in self.units_by_id.items():
            key = "units\\" + unit_record.filename + ".256"
            pal_key = "units\\" + os.path.dirname(unit_record.filename) + "\\"
            palette_paths = [key + "inner"] + [pal_key + "palette%d.pal" % i for i in range(2, 5)]

            palettes = []
            for path in palette_paths:
                try:
                    texture = self.textures[path]
                    palettes.append(texture)
                except KeyError:
                    # print("Palette not found", path)
                    pass
            self.palettes[utid] = palettes
            self.palette_tex = self.textures[palette_paths[0]][0]

    def __getitem__(self, utid):
        return self.palettes[utid]


class UnitHandler:
    alm: "Alm2"

    def __init__(self, game: BattleGame):
        self.game = game
        self.alm = self.game.alm
        self.sprite_pool = ObjectPool(PalettedSprite)
        self.spatial_hash = SpatialHash()
        self.batch = pyglet.graphics.Batch()
        self.units = self.game.units.units
        self.palettes = Palettes(game)

    def on_add_unit(self, unit):
        rect = self.get_visual_bounds(unit)
        self.spatial_hash.add_at(unit, rect)

    def on_remove_unit(self, unit):
        self.spatial_hash.remove(unit)

    def on_rotation_start(self, unit, from_angle, to_angle):
        unit.sprite_kind = EAnimType.idle

    def on_movement_start(self, unit, from_tile_xy, to_tile_xy):
        # move_angle = movement.direction_to_tile(from_tile_xy, to_tile_xy)
        # unit.ai.angle = move_angle
        unit.sprite_kind = EAnimType.move

    def on_movement(self, unit, from_tile_xy, to_tile_xy, factor):
        from_xy = self.game.alm.tile_center_at(from_tile_xy)
        to_xy = self.game.alm.tile_center_at(to_tile_xy)
        curr_xy = from_xy.lerp(to_xy, factor)
        offset_xy = curr_xy - from_xy
        unit.offset_xy = offset_xy

        unit.frame_id += 1
        if unit.frame_id >= (unit.record.movebeginphases + unit.record.movephases):
            unit.frame_id -= unit.record.movephases

        # ...

        self.spatial_hash.remove(unit)
        aabb = self.get_visual_bounds(unit)
        self.spatial_hash.add_at(unit, aabb)

    def on_movement_end(self, unit, from_tile_xy, to_tile_xy):
        unit.offset_xy = Vec2(0, 0)
        # if len(unit.ai.tasks) == 1:
        #     # last task
        #     unit.sprite_kind = EAnimType.idle
        #     unit.frame_id = 0

    def get_current_frame(self, unit: MapUnit):
        # image = self.get_frame_for_unit(unit)
        textures = TextureRegistry.get_instance()
        animations = AnimationRegistry.get_instance()

        # some units have 16
        divisor = 16 if unit.sprite_kind.name == "idle" else 32
        angle = unit.ai.angle // divisor

        seq = animations.seq_by_utid[unit.type_id]
        seq_frames = seq.frameids(unit.sprite_kind, angle)

        seq_frame_id = min(unit.frame_id, len(seq_frames))
        frame_id = seq_frames[seq_frame_id]
        frames = textures["units\\" + unit.record.filename + ".256"]
        image = frames[frame_id]
        return image

    def get_visual_bounds(self, unit: MapUnit):
        image = self.get_current_frame(unit)
        xy = self.alm.tile_center_at(unit.tile_xy) + unit.offset_xy

        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        x, y = self.mobj_frame_correction(xy, unit.record)
        aabb = x, y, x + image.width, y + image.height
        return aabb

    def mobj_frame_correction(self, xy, record):
        w, h = record.width, record.height
        cx, cy = record.centerx, record.centery
        anchor = Vec2(cx - w // 2, cy - h // 2)
        new_xy = xy - anchor
        return new_xy

    def get_palette(self, unit: MapUnit):
        palettes = self.palettes[unit.type_id]
        palette_id = unit.face_id - 1 if unit.face_id - 1 < len(palettes) else 0
        palette = palettes[palette_id][0]
        return palette

    def draw(self, camera):
        x, y = camera.x, camera.y
        bounds = x, y, x + 1024, y + 768
        to_draw = self.spatial_hash.get(bounds)
        batch = pyglet.graphics.Batch()
        sprites = []

        for unit in to_draw:
            image = self.get_current_frame(unit)
            aabb = self.get_visual_bounds(unit)
            xy = aabb[:2]
            palette = self.get_palette(unit)
            sprite = PalettedSprite(image, *xy, palette_tex=palette, batch=batch)
            if unit.record.flip and unit.ai.angle > unit.ai.rotation_phases // 2:
                sprite.scale_x = -1
            sprites.append(sprite)

        palette_tex = self.palettes.palette_tex
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(palette_tex.owner.target, palette_tex.owner.id)

        batch.draw()
        sprites.clear()

    def draw_unit_animations(self, unit):
        textures = TextureRegistry.get_instance()
        animations = AnimationRegistry.get_instance()

        images = textures["units\\" + unit.record.filename + ".256"]
        palette = self.get_palette(unit)
        dx = 100
        batch = pyglet.graphics.Batch()
        sprites = []
        for i in EAnimType:
            seq = animations.seq_by_utid[unit.type_id]
            divisor = 16 if i.name == "idle" else 32
            angle = unit.ai.angle // divisor
            seq_frame_ids = seq.frameids(i, angle)
            draw_frame_id = self.game.frame_id % seq.length_by_type[i]
            if i == i.move:
                draw_frame_id = unit.record.movebeginphases + self.game.frame_id % unit.record.movephases
            frame_id = seq_frame_ids[draw_frame_id % seq.length_by_type[i]]

            image = images[frame_id]
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
            xy = Vec2(100, -100) + Vec2(dx * i, 768)
            xy = self.mobj_frame_correction(xy, unit.record)
            sprite = PalettedSprite(image, *xy, palette_tex=palette, batch=batch)
            sprite.scale = 2
            sprites.append(sprite)
        batch.draw()

    def draw_unit_frames(self, unit):
        textures = TextureRegistry.get_instance()
        animations = AnimationRegistry.get_instance()

        images = textures["units\\" + unit.record.filename + ".256"]
        palette = self.get_palette(unit)
        dx = unit.record.width
        dy = unit.record.height // 2
        batch = pyglet.graphics.Batch()
        sprites = []
        for i in EAnimType:
            seq = animations.seq_by_utid[unit.type_id]
            divisor = 16 if i.name == "idle" else 32
            angle = unit.ai.angle // divisor
            seq_frame_ids = seq.frameids(i, angle)
            for j, frame_id in enumerate(seq_frame_ids):
                image = images[frame_id]
                image.anchor_x = image.width // 2
                image.anchor_y = image.height // 2
                xy = Vec2(100, 768-100) + Vec2(dx * i, -dy * j)
                xy = self.mobj_frame_correction(xy, unit.record)
                sprite = PalettedSprite(image, *xy, palette_tex=palette, batch=batch)
                sprites.append(sprite)
        batch.draw()

