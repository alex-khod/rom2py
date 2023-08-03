import pyglet.graphics
from profilehooks import timecall
from pyglet.math import Vec2

from src.formats.alm2 import Alm2
from src.mobj.layer import Layer
from src.resources import Resources

class Objects:

    def __init__(self):
        self.registry = Resources.special("objects.reg").content
        self.animations = {}
        self.palettes = {}
        self.layer = None
        self.sprites = None
        self.objects = []

    def load_objects(self, alm: Alm2):
        self.sprites = []
        self.layer = Layer(alm.width, alm.height)
        self.frame_id = 0
        for x, oid in enumerate(alm["objects"].body.objects):
            # Actual id is less by 1
            oid -= 1
            if oid < 0:
                continue
            tile_x = x % alm.width
            tile_y = x // alm.width
            tile_xy = Vec2(tile_x, tile_y)
            try:
                obj_record = self.registry.objects_by_id[oid]
            except:
                print(f"no object {oid}")
                continue
            object = (tile_xy, oid, obj_record)
            self.layer[tile_xy] = object
            self.objects.append(object)
