from enum import IntEnum


class WalkableGrid:
    class Flag(IntEnum):
        Terrain = 1
        Object = 2
        Structure = 4
        Unit = 8

    def __init__(self, game: "BattleGame"):
        self.game = game
        self.alm = game.alm
        self.grid = self.init_static_grid()

    def init_static_grid(self):
        alm = self.alm
        grid = [[0] * alm.width for _ in range(alm.width)]

        for idx, oid in enumerate(alm["objects"].body.objects):
            x = idx % alm.width
            y = idx // alm.width
            grid[y][x] |= WalkableGrid.Flag.Terrain if alm.walkable[y][x] else 0
            grid[y][x] |= WalkableGrid.Flag.Object if oid > 0 else 0

        return grid

    def on_movement_start(self, unit, from_tile_xy, to_tile_xy):
        self.block_map_at(unit.record.tilesize, from_tile_xy, WalkableGrid.Flag.Unit)

    def on_movement_end(self, unit, from_tile_xy, to_tile_xy):
        self.unblock_map_at(unit.record.tilesize, from_tile_xy, WalkableGrid.Flag.Unit)

    def on_add_unit(self, unit):
        self.block_map_at(unit.record.tilesize, unit.tile_xy, WalkableGrid.Flag.Unit)

    def on_unit_remove(self, unit):
        self.unblock_map_at(unit.record.tilesize, unit.tile_xy, WalkableGrid.Flag.Unit)

    def block_map_at(self, tilesize, tile_xy, flag):
        tx, ty = tile_xy
        for i in range(tilesize):
            for j in range(tilesize):
                tx, ty = tx + i, ty + j
                self.grid[ty][tx] |= flag

    def unblock_map_at(self, tilesize, tile_xy, flag):
        tx, ty = tile_xy
        for i in range(tilesize):
            for j in range(tilesize):
                tx, ty = tx + i, ty + j
                self.grid[ty][tx] &= ~flag
