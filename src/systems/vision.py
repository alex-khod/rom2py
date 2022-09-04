from src.utils import Vec2


class VisionSystem:

    def __init__(self, world):
        self.world = world
        alm = world.alm
        w, h = alm.width, alm.height
        self.tiles = [[set() for _ in range(w)] for _ in range(h)]

        for unit in world.units.units:
            self.set_vision_at(unit, unit.tile_xy, scan_range=3, value=True)
            unit.visible = self.scan_surroundings(unit, world, 3)

    def scan_surroundings(self, mobj, world, scan_range=1):
        tile_xy = mobj.tile_xy
        units = world.units.layer
        targets = set()
        for j in range(-scan_range, scan_range + 1):
            for i in range(-scan_range, scan_range + 1):
                if j == 0 and i == 0:
                    continue
                check = Vec2(tile_xy.x + i, tile_xy.y + j)
                unit = units[check]
                if unit:
                    targets.add(unit)
        return targets

    def set_vision_at(self, mobj, tile_xy, scan_range, value=True):
        x, y = tile_xy
        alm = self.world.alm
        tiles = self.tiles
        w, h = alm.width, alm.height
        for j in range(-scan_range, scan_range + 1):
            for i in range(-scan_range, scan_range + 1):
                if i == 0 and j == 0:
                    continue
                if not (-1 < x + i < w and -1 < y + i < h):
                    continue
                tile_vision = tiles[y+j][x+i]
                if value:
                    tile_vision.add(mobj)
                else:
                    if mobj in tile_vision:
                        tile_vision.remove(mobj)
