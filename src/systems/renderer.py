import os

from pyglet.math import Vec2

from src.formats.alm2 import Alm2, TILE_SIZE
from src.graphics.registry import TextureRegistry
from src.mobj.layer import Layer
from src.mobj.units.animation import UnitAnimationSequencer, EAnimType, EDirection16
from src.resources import Resources
from src.graphics.renderers.paletted import PalettedSprite
import pyglet

from src.systems.tasks import EAnimType
from src.systems.think import UnitAi
from pyglet.gl import *

from src.terrain import Terrain


class UnitsRenderer:
    def __init__(self, world, graphics):
        self.world = world
        self.graphics = graphics
        self.databin = Resources.special("data.bin").content
        self.unit_registry = Resources.special("units.reg").content
        # anim_registry = AnimationRegistry()
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
                    # print("Palette not found", path)
                    pass
            self.palettes[utid] = palettes

        for utid, unit_record in units_by_id:
            self.animations[utid] = self.animations_for_utid(utid)

    def animations_for_utid(self, utid):
        unit_frames = self.unit_frames[utid]
        unit_record = self.unit_registry.units_by_id[utid]
        anim_seq = UnitAnimationSequencer(unit_record)

        dying_utid = unit_record.dying
        dying_frames = self.unit_frames[dying_utid]
        dying_record = self.unit_registry.units_by_id[dying_utid]
        death_seq = UnitAnimationSequencer(dying_record)

        animations = {}
        for atype in anim_seq.types:
            animations[atype] = {}
            for facing in anim_seq.facings_by_type(atype):

                seq_frames, seq = (dying_frames, death_seq) if atype in (atype.die, atype.bones) else (unit_frames, anim_seq)
                frames = seq.sequence(seq_frames, atype, facing)
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
            for atype in Alm2.EAnimType:
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

    def draw_units(self, units):
        batch = pyglet.graphics.Batch()
        for unit in units:
            state = unit.ai.sprite_kind
            divisor = 16 if state.name == "idle" else 32
            angle = unit.ai.angle // divisor
            state_animations = self.animations[unit.utid]
            angle = min(angle, len(state_animations) - 1)
            angle_animations = state_animations[angle]

            utid = unit.type_id
            animations = self.animations[utid]
            animation = animations[EAnimType.idle][direction]
            palettes = self.palettes[utid]
            palette_id = unit.face_id - 1 if unit.face_id - 1 < len(palettes) else 0
            palette = palettes[palette_id]

            frame_id = unit.frame_id % len(angle_animations.frames)
            frame = angle_animations.frames[frame_id]
            texture = frame.image

            z = unit.xy.y / (alm.height * 32) * 256
            sprite = PalettedSprite(frame, *unit.xy, z)
            # self.sprite.z = 1 - self.xy.y / (alm.height * 32)

    def draw(self):
        self.draw_units(self.world.units.units)


class ObjectsRenderer:

    def __init__(self, game, graphics):
        self.game = game
        self.world = self.game.game
        self.graphics = graphics
        self.registry = Resources.special("objects.reg").content
        self.animations = {}
        self.palettes = {}
        self.layer = None
        self.sprites = None
        self.objects = []
        self.batch = pyglet.graphics.batch()
        self.prepare_objects()

    def prepare_objects(self):
        for oid, obj_record in self.registry.objects_by_id.items():
            key = "objects\\" + obj_record["filename"] + ".256"
            frames = self.graphics[key]
            self.animations[oid] = self.get_object_animation(frames, obj_record)
            palette = self.graphics[key + "inner"]
            self.palettes[oid] = palette

    @staticmethod
    def get_object_animation(self, frames, obj_record):
        """
            Return frames with frame indexes, read from obj_record.
        """
        frame_ids, frame_times = [obj_record['index']], [None]
        try:
            frame_ids = obj_record["animationframe"]
            frame_times = obj_record["animationtime"]
        except KeyError:
            pass

        w, h = obj_record["width"], obj_record["height"]
        cx, cy = obj_record["centerx"], obj_record["centery"]

        frame_subset = []
        for frame_id, frame_time in zip(frame_ids, frame_times):
            duration = frame_time / 60 if frame_time else None
            frame = frames[frame_id]
            frame.anchor_x = cx + (-w + frame.width) // 2
            frame.anchor_y = cy + (-h + frame.height) // 2
            frame = pyglet.image.AnimationFrame(frames[frame_id], duration)
            frame_subset.append(frame)
        animation = pyglet.image.Animation(frame_subset)
        # animation = frame_subset
        return animation

    def init_objects(self, world):
        objects = world.objects.objects
        alm = world.alm
        for obj in objects:
            (tile_xy, oid, obj_record) = obj
            xy = alm.tile_center_at(tile_xy)
            x, y = xy
            try:
                animation = self.animations[oid]
                palette = self.palettes[oid]
                image = animation
                image = animation.frames[0].image
                sprite = PalettedSprite(animation, x, y, 0, batch=self.batch, palette_tex=palette)
                sprite.z = sprite.y / (alm.height * 32) * 256

                from src.rects import Rect
                sprite.rect = Rect(*xy, *(xy + Vec2(image.width, image.height)))

                sprite.z = 1 - sprite.y / (alm.height * 32)

                # sprite.z = 256 - tile_y * 4
                # sprite.z = tile_y * 4
                sprite.animation = animation
                sprite._frame_id = 0

                # def obj_redraw(sprite):
                #     frame_id = (self.frame_id // 16) % len(sprite.animation.frames)
                #     frame = sprite.animation.frames[frame_id]
                #     texture = frame.image
                #     sprite._set_texture(texture)
                #
                # # sprite.redraw = obj_redraw.__get__(sprite, sprite.__class__)
                #
                # self.sprites.append(sprite)
            except KeyError:
                print(f"No anim for oid {oid}")

    def draw(self):
        self.batch.draw()


class GraphicsRenderer:

    def __init__(self, game: 'Application'):
        self.game = game
        self.window = game.window
        self.world = game.game
        self.graphics = TextureRegistry()
        self.objects_renderer = ObjectsRenderer(game, self.graphics)
        self.units_renderer = UnitsRenderer(game, self.graphics)
        self.terrain_renderer = Terrain(game.game)

    def draw(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        # glDepthFunc(GL_GREATER)
        game = self.game
        camera = self.game.camera
        camera.begin()
        self.window.clear()
        self.objects_renderer.draw()
        self.units_renderer.draw()
        self.terrain_renderer.draw()

        glDisable(GL_DEPTH_TEST)

        game.gui.on_draw()

        # prototype dynamic redraw
        from src.rects import Rect, filter_rects_by_intersect
        world = game.game
        camera_rect = Rect(camera.x, camera.y, camera.x + 1024, camera.y + 768)
        drawables = world.units.units + world.objects.sprites
        drawables = filter_rects_by_intersect(camera_rect, drawables)
        world.objects.frame_id += 1

        for sp in drawables:
            sp.redraw()

        camera.end()
        game.gui.draw()
