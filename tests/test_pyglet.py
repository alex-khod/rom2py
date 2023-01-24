from . import TestCase
import pyglet
from src.resources import get_resource_at_root

class PygletTest(TestCase):

    def test_sprite_draw_raises_gl_exception_if_created_before_window(self):
        path = get_resource_at_root("data", "lamp.jpg")
        image = pyglet.image.load(path)
        sprite = pyglet.sprite.Sprite(image)
        window = pyglet.window.Window()
        with self.assertRaises(pyglet.gl.lib.GLException):
            sprite.draw()

    def test_sprite_draw_raises_no_exception_if_created_after_window(self):
        path = get_resource_at_root("data", "lamp.jpg")
        image = pyglet.image.load(path)
        window = pyglet.window.Window()
        sprite = pyglet.sprite.Sprite(image)
        sprite.draw()
