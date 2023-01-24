__version__ = "0.0.5"

import math
import random
from dataclasses import dataclass
from typing import Tuple
from unittest.mock import Mock

import pyglet
from pyglet.gl import *
import os

from pyglet.math import Vec2, Vec4
from pyglet.window import mouse

from src import resources
from src.formats.alm2 import Alm2
from src.resources import Resources
from src.terrain import Terrain
from src.mobj import Objects, Units, Structures
from src.camera import Camera

from src.systems import ThinkSystem, UnitAi, UnitSpriteKind, AttackTask, DieTask
from src.terrain.terrain import TileObject

jn = os.path.join


def mainloop():
    class MainWindow(pyglet.window.Window):
        text = ''

        def on_key_press(self, symbol, modifiers):
            nonlocal game
            camera.handle_keypress(symbol)
            from src.camera import PKey
            if symbol == PKey.ESCAPE:
                game.gui.selection.clear()
            elif symbol == PKey.T:
                renderer.sprites.clear()
                game = load_level(alm)

        def on_key_release(self, symbol, modifiers):
            camera.handle_keyrelease(symbol)

        def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            tile_x, tile_y, _, _ = alm.world_xy_to_tile_xy(x, y)
            tile_xy = Vec2(tile_x, tile_y)

            # click indication
            hover.sprite.opacity = 255
            hover._ticks = 4

            selection = game.gui.selection

            # prototype handle select
            mobj = game.world.units.layer[tile_xy]
            if mobj is not None:
                selection.clear()
                selection.append(mobj)
            else:
                if selection:
                    mobj = selection[0]
                    print(mobj, "going to", tile_x, tile_y)
                    game.think.move_to_tile_xy(mobj, map_grid, (tile_x, tile_y))

        def on_mouse_scroll(self, mouse_x, mouse_y, scroll_x, scroll_y):
            camera.handle_scroll(scroll_y)

        def on_mouse_motion(self, mouse_x, mouse_y, dx, dy):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            # cursor_sprite.update(x=x, y=y)

            tile_x, tile_y, l, r = alm.world_xy_to_tile_xy(x, y)

            pos_txy = Vec2(tile_x, tile_y)
            hover.sprite.set_shape_from_tile_xy(alm, pos_txy)

            # prototype select hint
            if game.world.units.layer[pos_txy]:
                select.sprite.set_shape_from_tile_xy(alm, pos_txy)
                select.sprite.opacity = 127
            else:
                select.sprite.opacity = 0

            self.text = f"x{int(x)} y{int(y)} tx{tile_x} ty{tile_y} l{l} r{r}"

        def on_draw(self):
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            # glDepthFunc(GL_GREATER)
            camera.begin()
            self.clear()
            world = game.world
            world.terrain.draw()
            # rgb_renderer.draw()
            renderer.draw()
            # cursor_sprite.draw()
            glDisable(GL_DEPTH_TEST)

            hover.sprite.draw()
            if hover.ticks > 0:
                hover.ticks -= 1
            else:
                hover.sprite.opacity = 64

            select.sprite.draw()

            # prototype dynamic redraw

            from src.rects import Rect, filter_rects_by_intersect
            camera_rect = Rect(camera.x, camera.y, camera.x + 1024, camera.y + 768)
            drawables = world.units.units + world.objects.sprites

            drawables = filter_rects_by_intersect(camera_rect, drawables)

            world.objects.frame_id += 1

            for sp in drawables:
                sp.redraw()

            camera.end()
            game.gui.label.text = self.text
            game.gui.label.draw()
            game.gui.fps_display.draw()

    map_viewport_rect = (0, 0, 1024, 768)
    map_viewport_size_px = map_viewport_rect[2:]
    # double_buffer=False seems to behave naughty on win11?
    config = pyglet.gl.Config(double_buffer=True, vsync=False, depth_size=24)
    window = MainWindow(vsync=False, config=config, caption="The GL Thing", width=map_viewport_size_px[0],
                        height=map_viewport_size_px[1])

    # alm = Resources.get("scenario")["10.alm"].content
    # alm = Resources.from_file("data", "atest.alm")
    # alm = Resources.from_file("data", "atest2.alm")
    alm = Resources.from_file("data", "beach.alm")

    map_grid = [[0] * alm.width for _ in range(alm.height)]

    from src.graphics.renderers import PalettedSpriteRenderer as Renderer
    # from src.graphics.renderers import DefaultSpriteRenderer as Renderer

    from src.graphics.registry import GraphicsRegistry
    graphics = GraphicsRegistry()

    renderer = Renderer(graphics=graphics)
    camera = Camera(window)

    objects = Objects(renderer)
    units = Units(renderer)

    def load_level(alm):

        class Game:
            world: 'World'
            think: ThinkSystem
            gui: 'Gui'

        class World:
            alm: Alm2
            terrain: Terrain
            objects: Objects
            units: Units

        game = Game()

        world = World()
        world.alm = alm
        world.terrain = Terrain(alm)
        world.objects = objects
        world.objects.load_objects(alm)
        world.units = units
        world.units.load_units(alm)
        world.structures = Structures(alm, renderer)

        think = ThinkSystem()
        think.world = world

        class GameGui:
            selection: list
            label: pyglet.text.Label

        gui = GameGui()
        gui.selection = []
        gui.label = pyglet.text.Label(x=20, y=40, color=(255, 255, 255, 255), font_size=18)
        gui.fps_display = pyglet.window.FPSDisplay(window=window)

        unit = world.units.units[0]
        gui.selection.append(unit)

        game.world = world
        game.think = think
        game.gui = gui

        return game

    game = load_level(alm)

    # cursor_16a_sprite = Resources["graphics", "cursors", "arrow7", "sprites.16a"].content
    # image = cursor_16a_sprite[0].to_rgba_image_data()
    # cursor_sprite = pyglet.sprite.Sprite(image, 0, 0)
    # sprites = objects.sprites + units.sprites

    hover = TileObject(color=(255, 0, 0, 255), opacity=64, z=254)
    select = TileObject(color=(0, 255, 0, 255), z=255)

    def tick(dt):
        camera.scroll(dt)
        game.think.tick()

    pyglet.clock.schedule_interval(tick, interval=1 / 60)
    # pyglet.app.run(interval=1 / 120)
    pyglet.app.run(interval=0.0001)
