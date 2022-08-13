# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RageOfMages2DataBin(KaitaiStruct):

    class EStat(Enum):
        body = 0
        reaction = 1
        mind = 2
        spirit = 3

    class EMagic(Enum):
        fire = 0
        water = 1
        air = 2
        earth = 3
        astral = 4

    class EPhysical(Enum):
        blade = 0
        axe = 1
        bludgeon = 2
        pike = 3
        shooting = 4

    class ETreasure(Enum):
        gold = 0
        goldmin = 1
        goldmax = 2
        item = 3
        itemmin = 4
        itemmax = 5
        itemmask = 6
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.item_class_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.item_class_count = self._io.read_u4le()
        self.item_classes = [None] * (self.item_class_count)
        for i in range(self.item_class_count):
            self.item_classes[i] = RageOfMages2DataBin.TItemClass(self._io, self, self._root)

        self.material_count = self._io.read_u4le()
        self.materials = [None] * (self.material_count)
        for i in range(self.material_count):
            self.materials[i] = RageOfMages2DataBin.TItemClass(self._io, self, self._root)

        self.modifier_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.modifier_count = self._io.read_u4le()
        self.modifiers = [None] * (self.modifier_count)
        for i in range(self.modifier_count):
            self.modifiers[i] = RageOfMages2DataBin.TModifier(self._io, self, self._root)

        self.equipment_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.armor_count = self._io.read_u4le()
        self.armors = [None] * ((self.armor_count - 1))
        for i in range((self.armor_count - 1)):
            self.armors[i] = RageOfMages2DataBin.TEquipment(self._io, self, self._root)

        self.shield_count = self._io.read_u4le()
        self.shields = [None] * ((self.shield_count - 1))
        for i in range((self.shield_count - 1)):
            self.shields[i] = RageOfMages2DataBin.TEquipment(self._io, self, self._root)

        self.weapon_count = self._io.read_u4le()
        self.weapons = [None] * ((self.weapon_count - 1))
        for i in range((self.weapon_count - 1)):
            self.weapons[i] = RageOfMages2DataBin.TEquipment(self._io, self, self._root)

        self.magic_item_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.magic_item_count = self._io.read_u4le()
        self.magic_items = [None] * ((self.magic_item_count - 1))
        for i in range((self.magic_item_count - 1)):
            self.magic_items[i] = RageOfMages2DataBin.TMagicItem(self._io, self, self._root)

        self.monster_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.monster_count = self._io.read_u4le()
        self.monster_headers = [None] * ((self.monster_count - 1))
        for i in range((self.monster_count - 1)):
            self.monster_headers[i] = RageOfMages2DataBin.TMonsterHeader(self._io, self, self._root)

        self.human_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.human_count = self._io.read_u4le()
        self.human_headers = [None] * ((self.human_count - 1))
        for i in range((self.human_count - 1)):
            self.human_headers[i] = RageOfMages2DataBin.THumanHeader(self._io, self, self._root)

        self.structure_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.structure_count = self._io.read_u4le()
        self.structures = [None] * ((self.structure_count - 1))
        for i in range((self.structure_count - 1)):
            self.structures[i] = RageOfMages2DataBin.TStructure(self._io, self, self._root)

        self.spell_attrnames = RageOfMages2DataBin.Attrnames(self._io, self, self._root)
        self.spell_count = self._io.read_u4le()
        self.spell_headers = [None] * ((self.spell_count - 2))
        for i in range((self.spell_count - 2)):
            self.spell_headers[i] = RageOfMages2DataBin.TSpellHeader(self._io, self, self._root)


    class TMonster(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.stats = [None] * (4)
            for i in range(4):
                self.stats[i] = self._io.read_s4le()

            self.health_max = self._io.read_s4le()
            self.health_regeneration = self._io.read_s4le()
            self.mana_max = self._io.read_s4le()
            self.mana_regeneration = self._io.read_s4le()
            self.speed = self._io.read_s4le()
            self.rotation_speed = self._io.read_s4le()
            self.scan_range = self._io.read_s4le()
            self.physical_min = self._io.read_s4le()
            self.physical_max = self._io.read_s4le()
            self.attack_type = self._io.read_s4le()
            self.to_hit = self._io.read_s4le()
            self.defence = self._io.read_s4le()
            self.absorption = self._io.read_s4le()
            self.charge = self._io.read_s4le()
            self.relax = self._io.read_s4le()
            self.protection_magic = [None] * (5)
            for i in range(5):
                self.protection_magic[i] = self._io.read_s4le()

            self.protection_physical = [None] * (5)
            for i in range(5):
                self.protection_physical[i] = self._io.read_s4le()

            self.type_id = self._io.read_s4le()
            self.face = self._io.read_s4le()
            self.token_size = self._io.read_s4le()
            self.movement_type = self._io.read_s4le()
            self.dying_time = self._io.read_s4le()
            self.withdraw = self._io.read_s4le()
            self.wimpy = self._io.read_s4le()
            self.see_invisible = self._io.read_s4le()
            self.experience = self._io.read_s4le()
            self.treasure = [None] * (7)
            for i in range(7):
                self.treasure[i] = self._io.read_s4le()

            self.junk2 = self._io.read_bytes(8)
            self.power = self._io.read_s4le()
            self.spells = [None] * (7)
            for i in range(7):
                self.spells[i] = self._io.read_s4le()

            self.server_ud = self._io.read_s4le()
            self.known_spells = self._io.read_u4le()
            self.spell_skill = [None] * (5)
            for i in range(5):
                self.spell_skill[i] = self._io.read_u4le()

            self.equipped_item1 = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.equipped_item2 = RageOfMages2DataBin.U1str(self._io, self, self._root)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name if hasattr(self, '_m_name') else None

            self._m_name = self._parent.name
            return self._m_name if hasattr(self, '_m_name') else None


    class U1str(KaitaiStruct):

        def __new__(cls, *args, **kwargs):
            print(cls)
            print(super(RageOfMages2DataBin.U1str, RageOfMages2DataBin.U1str))
            return super().__new__(cls)

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()
            self = self.value

        def _read(self):
            self.length = self._io.read_u1()
            self.value = (self._io.read_bytes(self.length)).decode(u"866")


    class TModifier(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            self.mana_cost = self._io.read_s4le()
            self.affect_min = self._io.read_s4le()
            self.affect_max = self._io.read_s4le()
            self.usable_by = self._io.read_s4le()
            self.slots_fighter = [None] * (12)
            for i in range(12):
                self.slots_fighter[i] = self._io.read_s4le()

            self.slots_mage = [None] * (12)
            for i in range(12):
                self.slots_mage[i] = self._io.read_s4le()



    class THumanHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            if self.field_count == 0:
                self.junk = self._io.read_bytes(10)

            if self.field_count != 0:
                self.body = RageOfMages2DataBin.THuman(self._io, self, self._root)



    class TMonsterHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            if self.field_count == 0:
                self.junk = self._io.read_bytes(2)

            if self.field_count != 0:
                self.body = RageOfMages2DataBin.TMonster(self._io, self, self._root)



    class Attrnames(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header_count = self._io.read_u2le()
            self.attrnames = [None] * (self.header_count)
            for i in range(self.header_count):
                self.attrnames[i] = RageOfMages2DataBin.U1str(self._io, self, self._root)



    class TStructure(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            self.width = self._io.read_s4le()
            self.height = self._io.read_s4le()
            self.scan_range = self._io.read_s4le()
            self.health_max = self._io.read_s4le()
            self.can_pass = self._io.read_u4le()
            self.cant_pass = self._io.read_u4le()


    class TItemClass(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.abbreviate_and_materials = self._io.read_bytes(16)
            self.price = self._io.read_f8le()
            self.weight = self._io.read_f8le()
            self.damage = self._io.read_f8le()
            self.to_hit = self._io.read_f8le()
            self.defence = self._io.read_f8le()
            self.absorption = self._io.read_f8le()
            self.mag_cap = self._io.read_f8le()


    class TMagicItem(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            self.price = self._io.read_s4le()
            self.weight = self._io.read_s4le()
            self.has_effect = self._io.read_u1()
            if self.has_effect != 0:
                self.effect = RageOfMages2DataBin.U1str(self._io, self, self._root)



    class TSpell(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.level = self._io.read_s4le()
            self.mana_cost = self._io.read_s4le()
            self.sphere = self._io.read_s4le()
            self.item = self._io.read_s4le()
            self.spell_target = self._io.read_s4le()
            self.delivery_system = self._io.read_s4le()
            self.max_range = self._io.read_s4le()
            self.effect_speed = self._io.read_s4le()
            self.distribution = self._io.read_s4le()
            self.radius = self._io.read_s4le()
            self.area_effect = self._io.read_s4le()
            self.area_duration = self._io.read_s4le()
            self.area_frequency = self._io.read_s4le()
            self.apply_method = self._io.read_s4le()
            self.duration = self._io.read_s4le()
            self.frequency = self._io.read_s4le()
            self.min_damage = self._io.read_s4le()
            self.max_damage = self._io.read_s4le()
            self.defensive = self._io.read_s4le()
            self.skill_offset = self._io.read_s4le()
            self.scroll_cost = self._io.read_s4le()
            self.book_cost = self._io.read_s4le()
            self.effects = RageOfMages2DataBin.U1str(self._io, self, self._root)

        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name if hasattr(self, '_m_name') else None

            self._m_name = self._parent.name
            return self._m_name if hasattr(self, '_m_name') else None


    class TEquipment(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            self.shape = self._io.read_s4le()
            self.material = self._io.read_s4le()
            self.price = self._io.read_s4le()
            self.weight = self._io.read_s4le()
            self.slot = self._io.read_s4le()
            self.attack_type = self._io.read_s4le()
            self.physical_min = self._io.read_s4le()
            self.physical_max = self._io.read_s4le()
            self.to_hit = self._io.read_s4le()
            self.defence = self._io.read_s4le()
            self.absorption = self._io.read_s4le()
            self.range = self._io.read_s4le()
            self.charge = self._io.read_s4le()
            self.relax = self._io.read_s4le()
            self.two_handed = self._io.read_s4le()
            self.suitable_for = self._io.read_s4le()
            self.other_parameter = self._io.read_s4le()
            self.usable_by_class = [None] * (8)
            for i in range(8):
                self.usable_by_class[i] = self._io.read_u2le()



    class THuman(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.stats = [None] * (4)
            for i in range(4):
                self.stats[i] = self._io.read_s4le()

            self.health_max = self._io.read_s4le()
            self.mana_max = self._io.read_s4le()
            self.speed = self._io.read_s4le()
            self.rotation_speed = self._io.read_s4le()
            self.scan_range = self._io.read_s4le()
            self.defence = self._io.read_s4le()
            self.skill0 = self._io.read_s4le()
            self.skills = [None] * (5)
            for i in range(5):
                self.skills[i] = self._io.read_s4le()

            self.type_id = self._io.read_s4le()
            self.face = self._io.read_s4le()
            self.gender = self._io.read_s4le()
            self.charge = self._io.read_s4le()
            self.relax = self._io.read_s4le()
            self.token_size = self._io.read_s4le()
            self.movement_type = self._io.read_s4le()
            self.dying_time = self._io.read_s4le()
            self.server_id = self._io.read_s4le()
            self.known_spells = self._io.read_u4le()
            self.equipped_items = [None] * (10)
            for i in range(10):
                self.equipped_items[i] = RageOfMages2DataBin.U1str(self._io, self, self._root)


        @property
        def name(self):
            if hasattr(self, '_m_name'):
                return self._m_name if hasattr(self, '_m_name') else None

            self._m_name = self._parent.name
            return self._m_name if hasattr(self, '_m_name') else None


    class TSpellHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = RageOfMages2DataBin.U1str(self._io, self, self._root)
            self.field_count = self._io.read_u2le()
            if self.field_count == 0:
                self.junk = self._io.read_bytes(2)

            if self.field_count != 0:
                self.body = RageOfMages2DataBin.TSpell(self._io, self, self._root)




