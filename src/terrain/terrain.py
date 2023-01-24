# from .renderers.base import TerrainSpriteRenderer as Renderer
from .renderers.shader import TerrainShaderRenderer as Renderer
import pyglet

TILE_SIZE = 32


class Terrain:

    def __init__(self, alm):
        self.alm = alm
        self.renderer = Renderer(alm)

    def draw_origin(self):
        alm = self.alm
        WHITE = (255, 255, 255, 255)
        RED = (255, 0, 0, 255)
        colors = WHITE * 4 + RED * 4

        vertices = (0, 0, 0,
                    0, alm.height * TILE_SIZE, 0,
                    0, 0, 0,
                    alm.width * TILE_SIZE, 0, 0,
                    0, alm.height * TILE_SIZE, 0,
                    0, alm.height * TILE_SIZE + 32, 0,
                    alm.width * TILE_SIZE, 0, 0,
                    alm.width * TILE_SIZE + 32, 0, 0)

        pyglet.graphics.draw(8, pyglet.gl.GL_LINES, position=('i', vertices), colors=("f", colors))

    def render(self):
        self.draw_origin()
        self.renderer.draw()
