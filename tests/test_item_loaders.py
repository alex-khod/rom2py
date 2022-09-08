from src import items
from . import TestCase
from src.resources import Resources


class TestItemLoaders(TestCase):

    def test_can_load_every_unit_item(self):
        databin = Resources.special("data.bin").content
        monster_items = [x for m in databin.monsters for x in [m.equipped_item1, m.equipped_item2]]
        human_items = [x for m in databin.humans for x in m.equipped_items]
        all_unit_items = set(monster_items + human_items)
        all_unit_items.remove("")
        for item_string in all_unit_items:
            item = items.Item.from_string(item_string)
            assert isinstance(item.template, databin.TEquipment)