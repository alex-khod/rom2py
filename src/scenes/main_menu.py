import pyglet
from pyglet.gl import *

from src.resources import Resources
from src.scenes.base import BaseScene


class FixedResolution:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height

        self._target_area = 0, 0, 0, 0, 0

        self.framebuffer = pyglet.image.Framebuffer()
        self.texture = pyglet.image.Texture.create(width, height, min_filter=GL_LINEAR, mag_filter=GL_LINEAR)
        self.framebuffer.attach_texture(self.texture)

        self.window.push_handlers(self)

    def on_resize(self, width, height):
        self._target_area = self._calculate_area(*self.window.get_framebuffer_size())

    def _calculate_area(self, new_screen_width, new_screen_height):
        aspect_ratio = self.width / self.height
        aspect_width = new_screen_width
        aspect_height = aspect_width / aspect_ratio + 0.5
        if aspect_height > new_screen_height:
            aspect_height = new_screen_height
            aspect_width = aspect_height * aspect_ratio + 0.5

        return (int((new_screen_width / 2) - (aspect_width / 2)),  # x
                int((new_screen_height / 2) - (aspect_height / 2)),  # y
                0,  # z
                int(aspect_width),  # width
                int(aspect_height))  # height

    def __enter__(self):
        self.framebuffer.bind()
        self.window.clear()

    def __exit__(self, *unused):
        self.framebuffer.unbind()
        self.texture.blit(*self._target_area)

    def begin(self):
        self.__enter__()

    def end(self):
        self.__exit__()


class HoverPushButton(pyglet.gui.PushButton):

    def __init__(self, *args, **kwargs):
        self._hover = False
        on_hover = kwargs.pop('on_hover')
        self.on_hover = on_hover.__get__(self, self.__class__)
        on_unhover = kwargs.pop('on_unhover')
        self.on_unhover = on_unhover.__get__(self, self.__class__)
        super().__init__(*args, **kwargs)

    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        hit = self._check_hit(x, y)
        if not self._hover and hit:
            self.on_hover(x, y, dx, dy)
        elif self._hover and not hit:
            self.on_unhover(x, y, dx, dy)
        self._hover = hit


def get_adjusted_coords(x, y, scale, image):
    # basic resolution
    width, height = 640, 480
    scale_x, scale_y = scale
    x = x * scale_x
    y = (height - y - image.height) * scale_y
    return x, y


class MainMenuScene(BaseScene):

    def __init__(self, app):
        super().__init__()
        self.batch = pyglet.graphics.Batch()
        self.textures = pyglet.image.atlas.TextureBin()

        self.fixed_res = FixedResolution(app.window, 640, 480)
        scale_x, scale_y = 1, 1
        # scale_x = app.window.width / 640
        # scale_y = app.window.height / 480
        self.scale = scale_x, scale_y

        self.background = self.create_background()
        self.action_sprite = self.create_action_sprite()

        button_data = {"new_game": {"id": 1, "base_xy": (204, 52)},
                       "multiplayer": {"id": 2, "base_xy": (124, 156)},
                       "video": {"id": 3, "base_xy": (124, 252)},
                       "credits": {"id": 4, "base_xy": (208, 340)},
                       "load": {"id": 5, "base_xy": (340, 52)},
                       "hat": {"id": 6, "base_xy": (424, 152)},
                       "hallfame": {"id": 7, "base_xy": (412, 260)},
                       "exit": {"id": 8, "base_xy": (344, 348)}}

        for key, value in button_data.items():
            self.add_widget(self.create_button(**value))

    def create_action_sprite(self):
        image = pyglet.image.SolidColorImagePattern((255, 0, 0, 0)).create_image(180, 80)
        sprite = pyglet.sprite.Sprite(image, *get_adjusted_coords(232, 200, self.scale, image), batch=self.batch)
        scale_x, scale_y = self.scale
        sprite.scale_x = scale_x
        sprite.scale_y = scale_y
        return sprite

    def create_background(self):
        image = Resources["main", "graphics", "mainmenu", "menu_.bmp"].content.get_image_data()
        sprite = pyglet.sprite.Sprite(image)
        scale_x, scale_y = self.scale
        sprite.scale_x = scale_x
        sprite.scale_y = scale_y
        return sprite

    def create_button(self, id, base_xy):
        def get_on_hover(text):
            def on_hover(button, x, y, dx, dy):
                self.action_sprite.visible = True
                self.action_sprite.image = text

            return on_hover

        def on_unhover(button, x, y, dx, dy):
            self.action_sprite.visible = False

        def rescale_image(image):
            tex = image.get_texture()
            scale_x, scale_y = self.scale
            tex.width = image.width * scale_x
            tex.height = image.height * scale_y

        hover = Resources["main", "graphics", "mainmenu", "button%d.bmp" % id].content.get_image_data()
        pressed = Resources["main", "graphics", "mainmenu", "button%dp.bmp" % id].content.get_image_data()
        depressed = pyglet.image.SolidColorImagePattern((255, 0, 0, 0)).create_image(pressed.width, pressed.height)
        x, y = get_adjusted_coords(*base_xy, self.scale, pressed)
        hover, pressed, depressed = [self.textures.add(x, border=8) for x in [hover, pressed, depressed]]
        for image in [hover, pressed, depressed]:
            rescale_image(image)
        text = Resources["main", "graphics", "mainmenu", "text%d.bmp" % id].content.get_image_data()
        button = HoverPushButton(x, y, pressed=pressed, depressed=depressed,
                                 hover=hover,
                                 on_hover=get_on_hover(text),
                                 on_unhover=on_unhover,
                                 batch=self.batch)
        return button

    def draw(self):
        with self.fixed_res:
            self.background.draw()
            self.batch.draw()
        # self.background.draw()

        # pyglet.image.SolidColorImagePattern((255, 0, 0, 255)).create_image(32, 32).blit(32, 32)
