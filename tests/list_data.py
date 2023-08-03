from . import TestCase
from src.resources import Resources

class TestDatabin(TestCase):

    def _test_list_units_by_server_id(self):
        data_bin = Resources.special("data.bin").content
        for k, v in data_bin.units_by_server_id.items():
            print(k, v)

    def _test_list_registry_by_type_id(self):
        unit_registry = Resources.special("units.reg").content
        for k, v in unit_registry.units_by_id.items():
            print(k, v)

    def test_anim_frame_monotonic(self):
        unit_registry = Resources.special("units.reg").content
        for k, v in unit_registry.units_by_id.items():
            try:
                anim_type = "move"
                assert v.moveanimframe == list(range(len(v.moveanimframe)))
                anim_type = "attack"
                assert v.attackanimframe == list(range(len(v.attackanimframe)))
            except:
                print(k, anim_type, v.desctext, "not monotonic")
