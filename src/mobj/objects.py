import pyglet.graphics
from profilehooks import timecall
from pyglet.math import Vec2

from src.formats.alm2 import Alm2
from src.mobj.layer import Layer
from src.resources import Resources

TILE_SIZE = 32


def get_object_animation(frames, obj_record):
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


class Objects:
    """
        Class that implements logical handling of map objects/obstacles.
    """

    def __init__(self, alm, renderer):
        self.alm = alm
        self.registry = Resources.special("objects.reg").content
        self.renderer = renderer
        self.animations = {}
        self.palettes = {}
        self.graphics = renderer.graphics
        self.sprites = []
        self.prepare_objects()

        w, h = alm.width, alm.height
        self.layer = Layer(w, h)
        self.load_objects(alm)

    def prepare_objects(self):
        for oid, obj_record in self.registry.objects_by_id.items():
            key = "objects\\" + obj_record["filename"] + ".256"
            frames = self.graphics[key]
            self.animations[oid] = get_object_animation(frames, obj_record)
            palette = self.graphics[key + "inner"]
            self.palettes[oid] = palette

    @timecall
    def load_objects(self, alm: Alm2):

        self.frame_id = 0

        for x, oid in enumerate(alm["objects"].body.objects):
            # Actual id is less by 1
            oid -= 1
            if oid < 0:
                continue
            tile_x = x % alm.width
            tile_y = x // alm.width
            tile_xy = Vec2(tile_x, tile_y)

            xy = alm.tile_center_at(tile_xy)
            try:
                animation = self.animations[oid]
                palette = self.palettes[oid]
                image = animation
                image = animation.frames[0].image
                sprite = self.renderer.add_sprite(*xy, animation=image, palette=palette)
                sprite.z = sprite.y / (alm.height * 32) * 256
                # sprite.z = 1 - sprite.y / (alm.height * 32)

                # sprite.z = 256 - tile_y * 4
                # sprite.z = tile_y * 4
                sprite.animation = animation
                sprite._frame_id = 0

                def obj_redraw(sprite):
                    frame_id = (self.frame_id // 16) % len(sprite.animation.frames)
                    frame = sprite.animation.frames[frame_id]
                    texture = frame.image
                    sprite._set_texture(texture)

                sprite.redraw = obj_redraw

                self.layer[tile_xy] = sprite
                self.sprites.append(sprite)
            except KeyError:
                print(f"No anim for oid {oid}")
