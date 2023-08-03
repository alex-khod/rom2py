import pyglet
from pyglet.math import Mat4, Vec3


class Application:
    window: 'pyglet.window.Window'

    def __init__(self, window):
        self.window = window
        self.window.push_handlers(self)
        self._scenes = []

    def push_scene(self, scene):
        self._scenes.append(scene)
        self.window.push_handlers(scene)

    def pop_scene(self):
        current_scene = self._scenes[-1]
        self.window.remove_handlers(current_scene)
        self._scenes.pop()
        self.window.pop_handlers()

    def clear_scenes(self):
        self._scenes = []

    def on_draw(self):
        self.window.clear()
        for scene in self._scenes:
            scene.draw()