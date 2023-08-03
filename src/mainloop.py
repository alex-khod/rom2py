__version__ = "0.2.0"

import pyglet
from profilehooks import timecall
from pyglet.gl import *
import os

from src.resources import Resources

from src import systems
from src import scenes

jn = os.path.join


def mainloop():
    # double_buffer=False seems to behave naughty on win11?
    config = pyglet.gl.Config(double_buffer=True, vsync=False, depth_size=24)
    window = pyglet.window.Window(vsync=False, config=config, caption="The GL Thing", width=1024, height=768)
    app = systems.Application(window)

    # main_menu = scenes.MainMenuScene(app)
    # app.push_scene(main_menu)

    # alm = Resources.get("scenario")["10.alm"].content
    # alm = Resources.from_file("data", "atest.alm")
    # alm = Resources.from_file("data", "atest2.alm")
    alm = Resources.from_file("data", "beach.alm")

    battle = scenes.BattleScene(app, alm, None)
    app.push_scene(battle)

    # game.load_world(alm)
    # camera = game.camera

    # cursor_16a_sprite = Resources["graphics", "cursors", "arrow7", "sprites.16a"].content
    # image = cursor_16a_sprite[0].to_rgba_image_data()
    # cursor_sprite = pyglet.sprite.Sprite(image, 0, 0)
    # sprites = objects.sprites + units.sprites
    pyglet.app.run(interval=1/120)
    # pyglet.app.run(interval=0.0001)
