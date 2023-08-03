from . import TestCase
from src.resources import Resources, get_resource_at_root

from src.mobj.units.units import MapUnit, DummyUnitEntry, DummyTemplate
from src.systems.tasks import RotateTask

class TestRotateTask(TestCase):

    def setUp(self):
        dummy = DummyUnitEntry()
        unit_registry = Resources.special("units.reg").content
        data_bin = Resources.special("data.bin").content
        unit = MapUnit(dummy, unit_registry, data_bin)
        self.mobj = unit

    def _test_reach_in_5(self):
        # needs speeds of 1
        self.mobj.ai.angle = 0
        task = RotateTask(self.mobj, from_angle=1, to_angle=6)
        for i in range(4):
            assert not task.tick()
        assert task.tick()




