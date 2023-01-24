__version__ = "0.0.5"

from unittest.mock import Mock

import pyglet
from profilehooks import profile, timecall
from pyglet.gl import *
import os

from src import resources
from src.resources import Resources
from src.terrain import Terrain
from src.mobj import Objects, Units, Structures
from src.camera import Camera
from src import content

from src.systems import MovementSystem, ThinkSystem

# resources.get_selector = lambda : content.Selector
from src.terrain.renderers.base import TileSprite

jn = os.path.join

TILE_SIZE = 32
MAP_PADDING = 8


def render_text(text, x=0, y=0):
    pyglet.text.Label(text, x=x, y=y)


def animate(sprites):
    for sprite in sprites:
        sprite._frame_index += 1
        sprite._frame_index = sprite._frame_index % len(sprite.animation.frames)
        frame = sprite.animation.frames[sprite._frame_index]
        sprite._set_texture(frame.image.get_texture())
        sprite._update_position()


def mainloop():
    class MainWindow(pyglet.window.Window):
        text = ''

        def on_key_press(self, symbol, modifiers):
            camera.handle_keypress(symbol)

        def on_key_release(self, symbol, modifiers):
            camera.handle_keyrelease(symbol)

        def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            tile_x, tile_y = alm.world_xy_to_tile_xy(x, y)

            # prototype handle select
            # mobj = units.unit_map[tile_y][tile_x] or objects.object_map[tile_y][tile_x]
            mobj = world.units.unit_map[tile_y][tile_x]
            if mobj is not None:
                selection.clear()
                selection.append(mobj)
            else:
                if selection:
                    mobj = selection[0]
                    print(mobj, "going to", tile_x, tile_y)
                    think.move_to_tile_xy(mobj, map_grid, (tile_x, tile_y))

            # click indication
            hover.sprite.opacity = 255
            hover._ticks = 4

        def on_mouse_scroll(self, mouse_x, mouse_y, scroll_x, scroll_y):
            camera.handle_scroll(scroll_y)

        def on_mouse_motion(self, mouse_x, mouse_y, dx, dy):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            # cursor_sprite.update(x=x, y=y)

            tile_x, tile_y = alm.world_xy_to_tile_xy(x, y)
            x1, y1 = tile_x * TILE_SIZE, tile_y * TILE_SIZE
            hover.sprite._vertex_list.translate[:] = (x1, y1, 0) * 4
            hover.sprite.heights = alm.tile_corner_heights_at(tile_x=tile_x, tile_y=tile_y)

            self.text = f"x{int(x)} y{int(y)} tx{tile_x} ty{tile_y} l{1} r{2}"

        def on_draw(self):
            camera.begin()
            self.clear()
            world.terrain.draw()
            renderer.draw()
            # cursor_sprite.draw()

            hover.sprite.draw()
            if hover._ticks > 0:
                hover._ticks -= 1
            else:
                hover.sprite.opacity = 64

            # prototype dynamic redraw

            tx1, ty1, tx2, ty2 = visible_rect(camera, alm)
            tx1 = max(0, tx1)
            tx2 = min(alm.width, tx2)
            ty1 = max(0, ty1)
            ty2 = min(alm.height, ty2)

            world.objects.frame_id += 1

            for j in range(ty2, ty1):
                for i in range(tx1, tx2):
                    sp = world.objects.object_map[j][i]
                    if sp:
                        sp.redraw(sp)
                    sp = world.units.unit_map[j][i]
                    if sp:
                        sp.redraw(sp)

            camera.end()
            label.text = self.text
            label.draw()
            fps_display.draw()

    def visible_rect(camera, alm):
        xy = camera.screen_xy_to_world_xy(0, 0)
        tx1, ty1 = alm.world_xy_to_tile_xy(*xy)
        w, h = 1024, 768
        end_xy = camera.screen_xy_to_world_xy(w, h)
        tx2, ty2 = alm.world_xy_to_tile_xy(*end_xy)
        return tx1, ty1, tx2, ty2

    map_viewport_rect = (0, 0, 1024, 768)
    map_viewport_size_px = map_viewport_rect[2:]
    # double_buffer=False seems to behave naughty on win11?
    config = pyglet.gl.Config(double_buffer=True, vsync=False)
    window = MainWindow(vsync=False, config=config, caption="The GL Thing", width=map_viewport_size_px[0],
                        height=map_viewport_size_px[1])

    selection = []

    # window.view = window.view.scale((1, -1, 1))
    # window.view = window.view.translate((0, window.size[1], 0))
    # window.projection = window.projection.orthogonal_projection(0, 1024, 0, 768, z_near=0, z_far=1)
    # window.projection = window.projection.perspective_projection(1024 / 768, -255, 255, 45)

    label = pyglet.text.Label(x=20, y=40, color=(255, 255, 255, 255), font_size=18)
    # alm = Resources.get("scenario")["10.alm"].content
    # alm = Resources.from_file("data", "atest.alm")
    alm = Resources.from_file("data", "atest2.alm")
    # alm = Resources.from_file("data", "beach.alm")

    map_grid = [[0] * alm.width for _ in range(alm.height)]

    from src.graphics.renderers import PalettedSpriteRenderer as Renderer
    # from src.graphics.renderers import DefaultSpriteRenderer as Renderer

    from src.graphics.registry import GraphicsRegistry

    graphics = GraphicsRegistry()
    movement = MovementSystem(alm)
    think = ThinkSystem()
    think.movement = movement
    renderer = Renderer(graphics=graphics)
    camera = Camera(window)

    def setup():
        world = Mock()
        world.renderer = renderer
        world.terrain = Terrain(alm)
        world.objects = Objects(alm, renderer)
        world.units = Units(alm, renderer)
        world.structures = Structures(alm, renderer)
        return world

    world = setup()
    unit = world.units.units[0]
    # think.move_to_tile_xy(unit, map_grid, (0, 0))
    alm.unit_map = world.units.unit_map

    # cursor_16a_sprite = Resources["graphics", "cursors", "arrow7", "sprites.16a"].content
    # image = cursor_16a_sprite[0].to_rgba_image_data()
    # cursor_sprite = pyglet.sprite.Sprite(image, 0, 0)
    # sprites = objects.sprites + units.sprites

    def make_hover_tile():
        hover = Mock()
        reds = (255,) * 32 * 32
        image = pyglet.image.ImageData(32, 32, "R", bytes(reds))

        hover.sprite = TileSprite(image)
        hover.sprite.opacity = 64
        hover._ticks = 0
        return hover

    def make_selection_tile():
        selection = Mock()
        greens = (255,) * 32 * 32
        image = pyglet.image.ImageData(32, 32, "R", bytes(greens))
        selection.sprite = TileSprite(image)
        selection.sprite.opacity = 64
        return selection

    hover = make_hover_tile()

    fps_display = pyglet.window.FPSDisplay(window=window)

    def tick(dt):
        camera.scroll(dt)
        think.tick()
        movement.tick()

    # animate(sprites)
    # for sprite in sprites:
    #     sprite._frame_index += 1
    #     sprite._frame_index = sprite._frame_index % len(sprite.animation.frames)
    #     frame = sprite.animation.frames[sprite._frame_index]
    #     sprite._set_texture(frame.image.get_texture())
    #     sprite._update_position()
    pyglet.clock.schedule_interval(tick, interval=1 / 60)
    # pyglet.clock.schedule_interval(tick, )
    pyglet.app.run(interval=1 / 120)
    # pyglet.app.run(interval=0.0001)
