import pyglet

from src.camera import Camera
from src.systems.battle_game import BattleGame
from .base import BaseScene
from ..widgets import InventoryWidget
from ..widgets.map import GameAreaWidget


class BattleScene(BaseScene):

    def __init__(self, app, alm, state=None):
        super().__init__()
        self.app = app
        self.game = BattleGame(alm, state=None)
        window = app.window
        self.camera = Camera(window)
        self.game_area_widget = GameAreaWidget(0, 0, window.width, window.height, self.app, self.game, self.camera)
        self.inventory_widget = InventoryWidget(self.app, self.game)
        self.add_widget(self.game_area_widget)
        # self.spells_widget
        # self inventory widget
        for unit in self.game.units.units:
            self.game.events.dispatch_event("on_add_unit", unit)

        pyglet.clock.schedule_interval(self.game.tick, interval=1 / 10)

    def draw(self):
        self.game_area_widget.draw()