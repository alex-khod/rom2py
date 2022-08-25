__version__ = "0.0.5"

import math
import random
from dataclasses import dataclass
from unittest.mock import Mock

import pyglet
from profilehooks import profile, timecall
from pyglet.gl import *
import os

from pyglet.image import Texture
from pyglet.math import Vec2
from pyglet.window import mouse

from src import resources
from src.resources import Resources
from src.terrain import Terrain
from src.mobj import Objects, Units, Structures
from src.camera import Camera
from src import content

from src.systems import MovementSystem, ThinkSystem, UnitAi, UnitAiStates, AttackTask, DieTask

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


pid = 0

def mainloop():

    last_fireball = None
    class Tank:
        _tick = 0
        duration = 60

        def __init__(self, from_xy, to_xy):
            pos_x = random.randint(0, 512)
            pos_y = random.randint(0, 368)

            self.from_xy = Vec2(*camera.screen_xy_to_world_xy(pos_x, 768))
            self.to_xy = Vec2(*camera.screen_xy_to_world_xy(pos_x, 768 - pos_y))


            image = graphics["tank.png"]
            self.sprite = rgb_renderer.add_sprite(image, *from_xy)
            random.choice([forward, navalis, ready, hmm, smotri, sdelano]).play()

        def redraw(self):
            self._tick += 1
            factor = min(self._tick / self.duration, 1)
            new_pos = self.from_xy.lerp(self.to_xy, factor)
            self.sprite.x = new_pos.x
            self.sprite.y = new_pos.y

    class Fireball:
        from_xy: Vec2
        to_xy: Vec2
        texture = None
        dead = False

        traversed = 0
        distance = 0

        dead_frame = 0
        exploded = False

        def __init__(self, from_xy, to_xy):
            self.from_xy = from_xy
            self.to_xy = to_xy

            last_fireball = to_xy

            ai = UnitAi()
            ai.angle = 0
            walk_ai = ai.walk_ai

            self.speed = 20.0

            walk_ai.rotation_phases = 0
            walk_ai.move_begin_phases = 0
            walk_ai.move_phases = 4
            walk_ai.tile_xy = from_xy
            walk_ai.xy = from_xy.scale(TILE_SIZE) + Vec2(16, 16)
            avg_height = alm.tile_avg_heights_at(*from_xy)
            walk_ai.height = avg_height
            walk_ai.frame_id = 0

            global pid
            self.ai = ai
            self.move_frame_id = 0
            self.EID = "p%d" % pid
            pid += 1

            think.move_to_tile_xy(self, map_grid, to_xy)

            self.textures = graphics["fireball"]
            # self.sprite = renderer.add_sprite(self.texture, 0, 0, palette=graphics["graphics", "projectiles", "projectile_.pal"])
            # self.sprite = renderer.add_sprite(self.texture, 0, 0, palette=graphics["graphics", "projectiles", "projectiles.pal"])

            self.sprite = renderer.add_sprite(0, 0, self.textures[0], palette=graphics["fireballinner"])

            self.expl_tex = graphics["explosion"]
            for tex in self.textures + self.expl_tex:
                tex.anchor_x = 128 - tex.width // 2
                tex.anchor_y = 128 - tex.height // 2
            fireball.play()

        def redraw(self):
            height = self.ai.walk_ai.height
            sprite_xy = self.ai.walk_ai.xy
            sprite = self.sprite

            angle = self.ai.angle
            flip_x = 0
            if self.ai.state != UnitAiStates.idle:
                angle = angle * 2
            if (angle > 8):
                angle = 16 - angle
                flip_x = 1
            if angle == 3:
                angle += 1

            if not self.ai.walk_ai.path and not self.ai.tasks:
                if not self.exploded:
                    explosion.play()
                    self.exploded = True
                if self.dead_frame < len(self.expl_tex) * 16:
                    texture = self.expl_tex[self.dead_frame // 16]
                    self.sprite._palette_tex = graphics["explosioninner"]
                    self.sprite._create_vertex_list()
                    self.dead_frame += 1
                else:
                    angle = 3
                    texture = self.textures[angle * 4 + (self.move_frame_id % self.ai.walk_ai.move_phases)]
            else:
                texture = self.textures[angle * 4 + (self.move_frame_id % self.ai.walk_ai.move_phases)]
            if flip_x:
                texture = texture.get_transform(flip_x=True)
            sprite._set_texture(texture)
            sprite.x = sprite_xy.x
            sprite.y = sprite_xy.y - height
            sprite._update_position()

            renderer.redraw_shadow(sprite)

    class Lighting:
        from_xy: Vec2
        to_xy: Vec2
        texture = None
        _tick = 0

        def __init__(self, from_xy, to_xy):
            self.from_xy = from_xy
            self.to_xy = to_xy
            self.textures = graphics["lighting"]
            pal = graphics["lightinginner"]
            self.duration = 60
            self.time = 0
            self.sprites = []

            from_h = alm.tile_avg_heights_at(*from_xy)
            to_h = alm.tile_avg_heights_at(*to_xy)

            from_xy = Vec2(*from_xy) * Vec2(TILE_SIZE, TILE_SIZE) + Vec2(TILE_SIZE // 2, TILE_SIZE // 2 - from_h)
            to_xy = Vec2(*to_xy) * Vec2(TILE_SIZE, TILE_SIZE) + Vec2(TILE_SIZE // 2, TILE_SIZE // 2 - to_h)
            dxdy = to_xy - from_xy
            r = math.hypot(*dxdy)

            self.base_xy = from_xy
            self.dxdy = dxdy
            self.r = r

            self.sprites = []
            dist = 0
            while dist < 1.0:
                dist += 32 / 5 / r
                texture = random.choice(self.textures)
                sprite = renderer.add_sprite(0, 0, texture, pal)
                self.sprites.append(sprite)
            self.redraw()
            lighting.play()

        def redraw(self):
            self._tick += 1
            if self._tick % 4 != 0:
                return
            dist = 0
            from_xy = self.base_xy
            dxdy = self.dxdy

            ortho = dxdy.rotate(math.pi / 2).normalize().scale(48)
            phi_scale = random.randint(1, 3)

            opacity = min(math.sin(self._tick / self.duration * math.pi) * 255, 255)
            if self._tick > self.duration:
                opacity = 0

            def asinine(x):
                return x
                # return math.asin(2 * x - 1) / math.pi + 1/2
                # return math.sqrt(x ** 2 + math.sin(x) ** 2)
                a = math.sqrt(1 - x ** 2)
                return 1 / a / math.pi if a else 0

            # time = self._tick + random.randint(0, 16)
            for i, sprite in enumerate(self.sprites):
                xy = from_xy + dxdy.scale(dist) + ortho.scale(math.sin(asinine(dist) * math.pi * phi_scale))
                dist = i / len(self.sprites)
                # texture = random.choice(self.textures)
                sprite.x, sprite.y = xy
                sprite.opacity = opacity
                texture = random.choice(self.textures)
                sprite._set_texture(texture)
                sprite.shadow.opacity = opacity

                renderer.redraw_shadow(sprite)

    class Teleport:
        from_xy: Vec2
        to_xy: Vec2
        texture = None
        mobj = None
        _tick = 0
        cleared = True

        def __init__(self, from_xy, to_xy):
            self.from_xy = from_xy
            avg_height = alm.tile_avg_heights_at(*from_xy)
            to_txy = Vec2(*to_xy)
            self.to_xy = Vec2(*to_xy).scale(TILE_SIZE) + Vec2(16, 16 - avg_height)
            self.textures = graphics["teleport"]
            self._tick = 0
            self.cleared = False

            for tex in self.textures:
                tex.anchor_x = 96 - tex.width // 2
                tex.anchor_y = 96 - tex.height // 2

            self.duration = len(self.textures) * 4

            self.sprite = renderer.add_sprite(*self.to_xy, self.textures[0], graphics["teleportinner"])

            teleport.play()
            mage = world.units.mage
            mage.hp = 10
            angle = 4
            task = AttackTask(Vec2(0,0), Vec2(0,0), angle)
            mage.dead = False
            mage.ai.tasks.clear()
            mage.ai.tasks.append(task)
            mage.move_frame_id = 0
            mage.ai.walk_ai.xy = to_txy.scale(TILE_SIZE) + Vec2(16, 16)
            mage.ai.walk_ai.height = avg_height
            mage.ai.walk_ai.tile_xy = to_txy
            world.units.unit_map[to_txy.y][to_txy.x] = mage
            movement.moving_stuff[mage.EID] = mage
            self.mage = mage
            selection.clear()
            selection.append(mage)
        def redraw(self):
            mage = self.mage
            if mage.hp <= 0 and not mage.dead:
                mage.dead = True
                mage.ai.tasks.clear()
                task = DieTask(4)
                dead.play()
                mage.move_frame_id = 0
                mage.ai.tasks.append(task)
                movement.moving_stuff[mage.EID] = mage

            self._tick += 1
            if self._tick % 4 == 0:
                return
            frame_id = self._tick // 4
            if frame_id >= len(self.textures):
                if not self.cleared:
                    self.cleared = True
                    self.mage.ai.tasks.clear()
                    self.mage.move_frame_id = 0
                self.sprite.opacity = 0
                self.sprite.shadow.opacity = 0
                return
            texture = self.textures[frame_id]
            self.sprite._set_texture(texture)
            self.sprite._update_position()
            renderer.redraw_shadow(self.sprite)


    class MainWindow(pyglet.window.Window):
        text = ''
        todo = Lighting
        projectiles = []

        def on_key_press(self, symbol, modifiers):
            camera.handle_keypress(symbol)
            from src.camera import PKey
            if symbol == PKey._1:
                self.todo = Fireball
            elif symbol == PKey._2:
                self.todo = Lighting
            elif symbol == PKey._3:
                self.todo = Teleport
            elif symbol == PKey._4:
                self.todo = Tank
            elif symbol == PKey.ESCAPE:
                selection.clear()

        def on_key_release(self, symbol, modifiers):
            camera.handle_keyrelease(symbol)

        def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            tile_x, tile_y = alm.world_xy_to_tile_xy(x, y)

            def spawn(from_xy, to_xy):
                pclass = self.todo
                mobj = pclass(from_xy, to_xy)
                self.projectiles.append(mobj)

            # click indication
            hover.sprite.opacity = 255
            hover._ticks = 4

            if button == mouse.RIGHT and selection:
                mobj = selection[0]
                from_xy = mobj.ai.walk_ai.tile_xy
                spawn(from_xy, (tile_x, tile_y))
                return

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

        def on_mouse_scroll(self, mouse_x, mouse_y, scroll_x, scroll_y):
            camera.handle_scroll(scroll_y)

        def on_mouse_motion(self, mouse_x, mouse_y, dx, dy):
            x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
            # cursor_sprite.update(x=x, y=y)

            tile_x, tile_y = alm.world_xy_to_tile_xy(x, y)
            x1, y1 = tile_x * TILE_SIZE, tile_y * TILE_SIZE
            hover.sprite._vertex_list.translate[:] = (x1, y1, 0) * 4
            hover.sprite.heights = alm.tile_corner_heights_at(tile_x=tile_x, tile_y=tile_y)

            # prototype select hint
            if world.units.unit_map[tile_y][tile_x]:
                select.sprite._vertex_list.translate[:] = (x1, y1, 0) * 4
                select.sprite.heights = alm.tile_corner_heights_at(tile_x=tile_x, tile_y=tile_y)
                select.sprite.opacity = 127
            else:
                select.sprite.opacity = 0

            self.text = f"x{int(x)} y{int(y)} tx{tile_x} ty{tile_y} l{1} r{2}"

        def on_draw(self):
            camera.begin()
            self.clear()
            world.terrain.draw()
            rgb_renderer.draw()
            renderer.draw()
            # cursor_sprite.draw()

            hover.sprite.draw()
            if hover._ticks > 0:
                hover._ticks -= 1
            else:
                hover.sprite.opacity = 64

            select.sprite.draw()

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
                        if not isinstance(sp, Fireball):
                            sp.redraw(sp)
            for spd in self.projectiles:
                spd.redraw()

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

    lighting = Resources["sfx", "magic", "lightning.wav"].content
    teleport = Resources["sfx", "magic", "teleport.wav"].content
    fireball = Resources["sfx", "magic", "fireball.wav"].content
    explosion = Resources["sfx", "magic", "explosion.wav"].content
    pike = Resources["sfx", "units", "pike.wav"].content
    sword = Resources["sfx", "units", "sword.wav"].content
    soft = Resources["sfx", "units", "soft3.wav"].content
    easy = Resources["sfx", "characters", "hildarius", "easy.wav"].content
    hard = Resources["sfx", "characters", "hildarius", "hard.wav"].content
    dead = Resources["sfx", "characters", "hildarius", "dead.wav"].content
    gobo = Resources["sfx", "monsters", "goblin", "hard.wav"].content

    forward = Resources["sfx", "characters", "aldor", "attack", "1.wav"].content
    navalis = Resources["sfx", "characters", "aldor", "attack", "2.wav"].content
    ready = Resources["sfx", "characters", "aldor", "defend", "1.wav"].content
    hmm = Resources["sfx", "characters", "aldor", "pickup", "1.wav"].content
    smotri = Resources["sfx", "characters", "aldor", "swarm", "1.wav"].content
    sdelano = Resources["sfx", "characters", "aldor", "swarm", "2.wav"].content

    bgm = Resources["music", "b02.wav"].content

    player = pyglet.media.Player()
    player.volume = 15

    pl = bgm.play()
    pl.volume = 1

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
    selection.append(unit)
    alm.unit_map = world.units.unit_map

    from src.graphics.renderers.default import DefaultSpriteRenderer
    rgb_renderer = DefaultSpriteRenderer()
    image = graphics["tank.png"]
    rgb_renderer.add_sprite(image, 50, 50)

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
        image = pyglet.image.SolidColorImagePattern((0, 255, 0, 255)).create_image(32, 32)
        selection.sprite = TileSprite(image)
        return selection

    hover = make_hover_tile()
    select = make_selection_tile()

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
    pyglet.app.run(interval=1 / 120)
    # pyglet.app.run(interval=0.0001)
