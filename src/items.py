from typing import Tuple, List

from src.resources import Resources
import re

databin = Resources.special("data.bin").content

slot_id_to_category = {
    1: databin.weapons,
    2: databin.shields,
    3: databin.armors,
    14: databin.magic_items,
}


def parse_item_string(item_string):
    item_string = re.sub("\s+", " ", item_string)
    result = re.split("{(.*)}", item_string)
    return result


class IID:
    def __init__(self, material_id=0, slot_id=0, rarity_id=0, item_no=0, value=None):
        self.material_id = material_id
        self.slot_id = slot_id
        self.rarity_id = rarity_id
        self.item_no = item_no
        self.value = value

        if value is None:
            low = item_no + (rarity_id << 5)
            high = slot_id + (material_id << 4)
            value = low + (high << 8)
            self.value = value

    @classmethod
    def from_value(cls, value):
        iid = cls(value=value)
        high, low = value >> 8, value & 0xFF

        iid.material_id = (high >> 4) & 0b1111
        iid.slot_id = high & 0b1111

        iid.rarity_id = (low >> 5) & 0b111

        if iid.slot_id == 14:
            iid.item_no = low & 0b1111111
        else:
            iid.item_no = low & 0b11111
        return iid

    def __repr__(self):
        return f"IID {hex(self.value)}: rarity {self.rarity_id} mat {self.material_id} slot {self.slot_id} id {self.item_no}"


def hardcoded_items() -> List[Tuple[str, 'IID']]:
    data = [("BareHands", 0),
            ("Sonic Beam", 23),
            ("Flame Thrower", 24),
            ("Boulder Thrower", 25),
            ("Plasma Sword", 26)]
    data = [(item_name, IID(slot_id=1, item_no=item_no)) for item_name, item_no in data]
    return data


class ItemLookup:

    def __init__(self):
        item_names = Resources.special("itemserv.txt").content
        item_bin = Resources.special("itemname.bin").content
        lookup_table = {}
        for item_name, iid_value in zip(item_names, item_bin.items):
            iid = IID.from_value(iid_value)
            lookup_table[item_name] = iid
            if item_name.startswith("Common"):
                item_name = item_name.replace("Common ", "")
                lookup_table[item_name] = iid
            if "None" in item_name:
                item_name = item_name.replace("None ", "")
                lookup_table[item_name] = iid

        for item_name, iid in hardcoded_items():
            lookup_table[item_name] = iid
        # crutch to load this one item with a typo
        lookup_table["Leather Gauntless"] = lookup_table["Leather Gauntlets"]

        self.table = lookup_table


item_lookup = ItemLookup()


class ItemTemplate:

    @classmethod
    def from_iid(cls, iid: 'IID'):
        slot_id = iid.slot_id
        item_no = iid.item_no

        lookup_slot_id = slot_id
        if 2 < slot_id < 14:
            lookup_slot_id = 3

        item_category_list = slot_id_to_category[lookup_slot_id]
        template = item_category_list[item_no - 1]
        return template


class Item:

    @classmethod
    def from_string(cls, item_string: str):
        self = cls()
        parsed = parse_item_string(item_string)
        item_string = parsed[0]
        # trim spaces
        item_string = item_string.strip()
        iid = item_lookup.table[item_string]
        self.template = ItemTemplate.from_iid(iid)
        return self
