import pyglet
from src.resources import Resources


class ObjectRegistry:
    """
        Fetches framedata for every map object.
    """

    def __init__(self):
        graphics_res = Resources["graphics"]
        objects_registry = graphics_res['objects', 'objects.reg'].content
        self.objects_by_id = objects_registry.objects_by_id

    def add_unit(self):
        graphics_res = Resources["graphics"]
        for oid, obj_record in self.obstacles_by_id.items():
            a256 = graphics_res["objects", obj_record["filename"] + '.256'].content
            frames = []
            try:
                animationframes = obj_record["animationframe"]
                animationtimes = obj_record["animationtime"]
            except KeyError:
                animationframes, animationtimes = [obj_record['index']], [None]
            for frame_no, duration in zip(animationframes, animationtimes):
                w, h = obj_record["width"], obj_record["height"]
                image = a256[frame_no]
                cx, cy = obj_record["centerx"], obj_record["centery"]
                image.anchor_x = cx
                image.anchor_y = cy
                duration = duration / 60 if duration else None
                frame = pyglet.image.AnimationFrame(image, duration)
                frames.append(frame)
            assert len(animationtimes) == len(animationframes)
            obj_record["framedata"] = frames
