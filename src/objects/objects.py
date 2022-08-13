import pyglet.graphics

from src.resources import Resources

TILE_SIZE = 32


def get_default_animation(a256_frames, obj_record):
    """
        Return frames with frame indexes, read from obj_record.
    """
    frame_ids, frame_times = [obj_record['index']], [None]
    try:
        frame_ids = obj_record["animationframe"]
        frame_times = obj_record["animationtime"]
    except KeyError:
        pass

    frames = []
    for frame_id, frame_time in zip(frame_ids, frame_times):
        duration = frame_time / 60 if frame_time else None
        frame = pyglet.image.AnimationFrame(a256_frames[frame_id], duration)
        frames.append(frame)
    animation = pyglet.image.Animation(frames)
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
        self.sprites = []
        self.prepare_objects()
        self.load_objects(alm)

    def prepare_objects(self):
        for oid, obj_record in self.registry.objects_by_id.items():
            a256 = Resources["graphics", "objects", obj_record["filename"] + ".256"].content
            a256_frames = self.renderer.a256_to_frames(a256=a256, record=obj_record, sprite_key="objects")
            self.renderer.prepare_palette(a256.palette, palette_key=oid)
            self.animations[oid] = get_default_animation(a256_frames, obj_record)

    def load_objects(self, alm):
        for x, oid in enumerate(alm["objects"].body.objects):
            # Actual id is less by 1
            oid -= 1
            if oid < 0:
                continue
            tile_x = x % alm.width
            tile_y = x // alm.width
            x = tile_x * TILE_SIZE + TILE_SIZE // 2
            y = tile_y * TILE_SIZE + TILE_SIZE // 2
            try:
                animation = self.animations[oid]
                sprite = self.renderer.add_sprite(animation, x, y, palette_key=oid)
                self.sprites.append(sprite)
            except KeyError:
                print(f"No anim for oid {oid}")

    def render(self):
        self.renderer.draw()
