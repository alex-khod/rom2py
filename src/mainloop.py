__version__ = "0.0.3"

import pyglet
from pyglet.gl import *
import os

from src.resources import Resources
from src.terrain import Terrain
from src.objects import Objects
from src.units import Units
from src.camera import Camera

jn = os.path.join

TILE_SIZE = 32
MAP_PADDING = 8


def render_text(text, x=0, y=0):
    pyglet.text.Label(text, x=x, y=y)


def mainloop():
    class MainWindow(pyglet.window.Window):

        def on_key_press(self, symbol, modifiers):
            camera.handle_keypress(symbol)

        def on_key_release(self, symbol, modifiers):
            camera.handle_keyrelease(symbol)

        def on_mouse_scroll(self, mouse_x, mouse_y, scroll_x, scroll_y):
            camera.handle_scroll(scroll_y)

        def on_mouse_motion(self, mouse_x, mouse_y, dx, dy):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            cursor_sprite.update(x=x, y=y)

        def on_draw(self):
            camera.begin()
            self.clear()
            terrain.draw()
            renderer.draw()
            cursor_sprite.draw()
            camera.end()
            # fps_display.draw()

    map_viewport_rect = (0, 0, 1024, 768)
    map_viewport_size_px = map_viewport_rect[2:]
    config = pyglet.gl.Config(double_buffer=False, vsync=False)
    window = MainWindow(vsync=False, config=config, caption="The GL Thing", width=map_viewport_size_px[0],
                        height=map_viewport_size_px[1])

    # window.view = window.view.scale((1, -1, 1))
    # window.view = window.view.translate((0, window.size[1], 0))
    # window.projection = window.projection.orthogonal_projection(0, 1024, 0, 768, z_near=0, z_far=1)

    alm = Resources.get("scenario")["10.alm"].content
    # alm = Resources.from_file("data", "atest.alm")

    from src.renderers import PalettedSpriteRenderer as Renderer
    # from src.renderers import DefaultSpriteRenderer as Renderer

    renderer = Renderer()
    terrain = Terrain(alm)
    objects = Objects(alm, renderer)
    # units = Units(alm, renderer)
    camera = Camera(window)

    cursor_a16_sprite = Resources["graphics", "cursors", "arrow7", "sprites.16a"].content
    image = cursor_a16_sprite[0].to_rgba_image_data()
    cursor_sprite = pyglet.sprite.Sprite(image, 0, 0)

    def tick(dt):
        camera.scroll(dt)

    fps_display = pyglet.window.FPSDisplay(window=window)
    # pyglet.clock.schedule_interval(tick, interval=0.01)
    pyglet.clock.schedule(tick)
    pyglet.app.run(interval=1 / 120)
    # pyglet.app.run(interval=0.0001)
