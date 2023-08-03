import pyglet

from src import systems, gui
from src.camera import Camera
from src.mobj import Objects, MapUnits
from src.systems import ThinkSystem, VisionSystem
from src.systems.grid import WalkableGrid
from src.terrain import Terrain


class EventTracker(pyglet.event.EventDispatcher):
    pass

EventTracker.register_event_type("on_movement_start")
EventTracker.register_event_type("on_movement")
EventTracker.register_event_type("on_movement_end")

EventTracker.register_event_type("on_add_unit")
EventTracker.register_event_type("on_remove_unit")


class BattleGame:
    units: "MapUnits"

    def __init__(self, alm, state=None):
        self.alm = alm
        self.load_map(alm)

    def load_map(self, alm):
        self.last_dt = 0
        self.frame_id = 0
        self.terrain = Terrain(alm)
        self.objects = Objects()
        self.objects.load_objects(self.alm)
        self.units = MapUnits()
        self.units.load_units(self.alm)
        self.think = ThinkSystem(self)
        self.grid = WalkableGrid(self)
        self.vision = VisionSystem(self)
        self.events = EventTracker()
        self.events.push_handlers(self.units)
        self.events.push_handlers(self.grid)

    def tick(self, dt):
        try:
            self.frame_id += 1
            self.think.tick()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.load_map(self.alm)
