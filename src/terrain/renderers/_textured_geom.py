def blit_terrain_to_texture(self):
    alm = self.alm
    map_tex = pyglet.image.Texture.create(alm.width * TILE_SIZE, alm.height * TILE_SIZE)
    map_tex_tiles = [[None] * alm.width for _ in range(alm.height)]
    self.map_tex = map_tex
    self.map_tex_tiles = map_tex_tiles
    return
    border = 0
    for j in range(alm.height):
        for i in range(alm.width):
            stripe_id, row_id = alm.tilecoords[j][i]
            stripe = self.stripes[stripe_id]
            tile_image = stripe.get_region(border, border + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            x, y = i * TILE_SIZE, j * TILE_SIZE
            map_tex.blit_into(tile_image, x, y, 0)
            map_tex_tiles[j][i] = map_tex.get_region(x, y, TILE_SIZE, TILE_SIZE)


        map_tex_group = pyglet.graphics.TextureGroup(self.map_tex)