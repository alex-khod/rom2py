def __init__(self):
    verts, idxs, tcs = VertexAllocator().alloc(all_verts, all_tex_coords)
    indexed_batch = pyglet.graphics.Batch()
    count = len(verts) // 2
    indexed_batch.add_indexed(count, GL_QUADS, map_tex_group, idxs, ("v2i", verts), ("c3B", count * WHITE),
                              ("t3f", tcs))
    indexed_batch.add_indexed(count, GL_QUADS, wf_group, idxs, ("v2i", verts), ("c3B", count * WHITE))

def draw_indexed_test(self):
    all_verts = []
    all_tex_cs = []
    for i in range(3):
        for j in range(3):
            x1, y1 = i * TILE_SIZE, j * TILE_SIZE
            x2, y2 = (i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE
            vert_quads = (x1, y1, x2, y1, x2, y2, x1, y2)
            all_verts += vert_quads

            map_tex_quads = (0.015625, 0.0625, 0.0, 0.03125, 0.0625, 0.0, 0.03125, 0.125, 0.0, 0.015625, 0.125, 0.0)
            all_tex_cs += map_tex_quads

    valloc = VertexAllocator()
    verts, idxs, tex_cs = valloc.alloc(all_verts, all_tex_cs)
    n = len(verts) // 2
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, self.tiles_tex.id)
    pyglet.graphics.draw_indexed(6, GL_QUADS, (0, 1, 2, 3, 2, 3, 5, 6, 7, 8),
                                 ("v2i", (
                                     x1, y1, x2, y1, x2, y2, x1, y2, x2 + TILE_SIZE, y2 + TILE_SIZE, x2 + TILE_SIZE,
                                     y2)),
                                 ("c3B", 6 * WHITE))
    # pyglet.graphics.draw_indexed(n, GL_QUADS, idxs, ("v2i", verts), ("c3B", n * WHITE), ("t3f", tex_cs))
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    pyglet.graphics.draw_indexed(n, GL_QUADS, idxs, ("v2i", verts), ("c3B", n * WHITE))
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glDisable(GL_TEXTURE_2D)

