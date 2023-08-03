from src.utils import Vec2


class VisionSystem:

    def __init__(self, game):
        self.game = game
        alm = game.alm
        w, h = alm.width, alm.height
        self.tiles = [[set() for _ in range(w)] for _ in range(h)]

    def on_add_unit(self, unit):
        self.set_mobj_vision_at(unit, unit.tile_xy, scan_range=3, value=True)
        unit.visible = self.scan_surroundings(unit, 3)
    def on_remove_unit(self, unit):
        pass

    def scan_surroundings(self, mobj, scan_range=1):
        tile_xy = mobj.tile_xy
        game = self.game
        units = game.units.layer
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

    def set_mobj_vision_at(self, mobj, tile_xy, scan_range, value=True):
        x, y = tile_xy
        alm = self.game.alm
        tiles = self.tiles
        w, h = alm.width, alm.height
        for j in range(-scan_range, scan_range + 1):
            for i in range(-scan_range, scan_range + 1):
                if i == 0 and j == 0:
                    continue
                if not (-1 < x + i < w and -1 < y + i < h):
                    continue
                tile_vision = tiles[y + j][x + i]
                if value:
                    tile_vision.add(mobj)
                else:
                    if mobj in tile_vision:
                        tile_vision.remove(mobj)
    def on_movement_end(self, mobj, from_xy, to_tile_xy):
        mobj.ai.visible_targets = self.scan_surroundings(mobj, 3)
    def check_visible_things_at(self, x, y):
        game = self.game
        for other_mobj in game.vision.tiles[y][x]:
            if other_mobj.ai.state:
                continue
            state_class = other_mobj.ai.new_vision_state
            other_mobj.ai.state = state_class(other_mobj, game, other_mobj.tile_xy)
            game.think.add(other_mobj)
