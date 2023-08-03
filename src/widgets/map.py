import pyglet
from pyglet.gui import WidgetBase
from pyglet.math import Vec2

from src.graphics.registry import TextureRegistry
from src.graphics.renderers.paletted import PalettedSprite
from src.systems.animations.units import EAnimType, AnimationRegistry
from src.terrain.renderers import TileSprite
from src.mobj.unit_handler import UnitHandler, Palettes
from src.widgets.terrain import TerrainGraphics


class GameAreaWidget(WidgetBase):

    def __init__(self, x, y, width, height, app, game, camera):
        super().__init__(x, y, width, height)
        self.app = app
        self.game = game
        self.camera = camera
        self.selection = [game.units.units[0]]
        self.terrain_gfx = TerrainGraphics(game.alm)
        self.unit_handler = UnitHandler(game)
        game.events.push_handlers(self.unit_handler)

        self.debug_label = pyglet.text.Label(x=20, y=40, color=(255, 255, 255, 255), font_size=18)
        self.debug_text = ""
        self.fps_display = pyglet.window.FPSDisplay(app.window)
        self.hover = hover = TileSprite.from_color(color=(255, 0, 0, 64))
        hover.z = 254
        hover._ticks = 0
        self.select = select = TileSprite.from_color(color=(0, 255, 0, 255))
        select.z = 255

    def add_events(self):
        events = self.game.events

    def click(self):
        self.hover.opacity = 255
        self.hover._ticks = 4

    def draw(self):
        self.camera.scroll(1 / 100)
        with self.camera:
            self.terrain_gfx.draw()

            hover = self.hover
            if hover._ticks > 0:
                hover._ticks -= 1
            else:
                hover.opacity = 64

            self.unit_handler.draw(self.camera)
            hover.draw()
            self.select.draw()
        self.unit_handler.draw_unit_animations(self.selection[0])
        # self.unit_handler.draw_unit_frames(self.selection[0])
        self.debug_label.text = self.debug_text
        self.debug_label.draw()
        self.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        camera = self.camera
        camera.handle_keypress(symbol)

        # if symbol == pyglet.window.key.R:
        #     self.game.load_map(self.game.alm)

        # from src.camera import PKey
        # game = self.game
        # if symbol == PKey.ESCAPE:
        #     self.selection.clear()
        # elif symbol == PKey.T:
        #     game.renderer.sprites.clear()
        #     game.load_world(alm)

    def on_key_release(self, symbol, modifiers):
        self.camera.handle_keyrelease(symbol)

    def on_mouse_press(self, mouse_x, mouse_y, button, modifiers):
        alm = self.game.alm
        camera = self.camera
        x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
        tile_x, tile_y, _, _ = alm.world_xy_to_tile_xy(x, y)
        tile_xy = Vec2(tile_x, tile_y)

        game = self.game
        # click indication
        self.click()
        selection = self.selection

        # prototype handle select
        mobj = game.units.layer[tile_xy]
        if mobj is not None:
            selection.clear()
            selection.append(mobj)
        else:
            if selection:
                mobj = selection[0]
                print(mobj, "going to", tile_x, tile_y)
                game.think.move_to_tile_xy(mobj, (tile_x, tile_y))

    def on_mouse_scroll(self, mouse_x, mouse_y, scroll_x, scroll_y):
        self.camera.handle_scroll(scroll_y)

    def on_mouse_motion(self, mouse_x, mouse_y, dx, dy):
        alm = self.game.alm
        camera = self.camera
        game = self.game
        x, y = camera.screen_xy_to_world_xy(mouse_x, mouse_y)
        # cursor_sprite.update(x=x, y=y)

        tile_x, tile_y, l, r = alm.world_xy_to_tile_xy(x, y)

        pos_txy = Vec2(tile_x, tile_y)
        self.hover.set_shape_from_tile_xy(alm, pos_txy)

        select = self.select

        # # prototype select hint
        if game.units.layer[pos_txy]:
            select.set_shape_from_tile_xy(alm, pos_txy)
            select.opacity = 127
        else:
            select.opacity = 0

        self.debug_text = f"x{int(x)} y{int(y)} tx{tile_x} ty{tile_y} l{l} r{r}"
