# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class RageOfMages2Alm(KaitaiStruct):

    class CheckType(Enum):
        unknown = 0
        group_unit_count = 1
        is_unit_in_a_box = 2
        is_unit_in_a_circle = 3
        get_unit_parameter = 4
        is_unit_alive = 5
        get_distance_between_units = 6
        get_distance_from_point_to_unit = 7
        how_many_units_player_have = 8
        is_unit_attacked = 9
        get_diplomacy = 10
        check_sack = 11
        get_distance_to_nearest_player_unit = 15
        get_distance_from_point_to_unit_with_item = 16
        is_item_in_sack = 17
        vip = 18
        check_variable = 19
        how_many_structures_player_have = 20
        get_structure_health = 21
        teleport = 22
        check_scenario_variable = 23
        check_sub_objective = 24
        spell_in_area = 25
        spell_on_unit = 26
        is_unit_in_point = 27
        constant = 65538

    class SectionKindE(Enum):
        general = 0
        tiles = 1
        heights = 2
        objects = 3
        structures = 4
        players = 5
        units = 6
        triggers = 7
        sacks = 8
        effects = 9

    class CheckOperator(Enum):
        equals = 0
        not_equals = 1
        greater_than = 2
        lower_than = 3
        greater_than_equals = 4
        lower_than_equals = 5

    class ArgumentType(Enum):
        number = 1
        group = 2
        player = 3
        unit = 4
        x = 5
        y = 6
        constant = 7
        item = 8
        structure = 9

    class InstanceType(Enum):
        unknown = 0
        increment_mission_stage = 1
        send_message = 2
        set_variable_value = 3
        force_mission_complete = 4
        force_mission_failed = 5
        command = 6
        keep_formation = 7
        increment_variable = 8
        set_diplomacy = 10
        give_item = 11
        add_item_in_units_sack = 12
        remove_item_from_units_sack = 13
        hide_unit = 16
        show_unit = 17
        metamorph_unit = 18
        change_units_owner = 19
        drop_all = 20
        magic_on_area = 21
        change_groups_owner = 22
        give_money_to_player = 23
        magic_on_unit = 24
        create_magic_trigger = 25
        set_structure_health = 26
        move_unit_immediate = 27
        give_all_items_from_unit_to_unit = 28
        timed_spell_on_ground = 30
        change_respawn_time = 31
        hide_group = 32
        show_group = 33
        set_units_parameter = 34
        set_scenario_variable = 35
        set_sub_objective = 36
        set_music_order = 37
        remove_item_from_all = 38
        stop_group = 39
        start_here = 65538
        respawn_group = 65539
        change_music_to = 65540
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_alm_header = self._io.read_bytes(20)
        _io__raw_alm_header = KaitaiStream(BytesIO(self._raw_alm_header))
        self.alm_header = RageOfMages2Alm.AlmHeader(_io__raw_alm_header, self, self._root)
        self._raw_header = self._io.read_bytes(20)
        _io__raw_header = KaitaiStream(BytesIO(self._raw_header))
        self.header = RageOfMages2Alm.SectionHeader(_io__raw_header, self, self._root)
        self.general = RageOfMages2Alm.GeneralSec(self._io, self, self._root)
        self.sections = [None] * ((self.alm_header.section_count - 1))
        for i in range((self.alm_header.section_count - 1)):
            self.sections[i] = RageOfMages2Alm.AlmSection(self._io, self, self._root)


    class ObjectsSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.objects = [None] * ((self._root.general.width * self._root.general.height))
            for i in range((self._root.general.width * self._root.general.height)):
                self.objects[i] = self._io.read_u1()



    class AlmSection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_header = self._io.read_bytes(20)
            _io__raw_header = KaitaiStream(BytesIO(self._raw_header))
            self.header = RageOfMages2Alm.SectionHeader(_io__raw_header, self, self._root)
            _on = self.header.section_kind
            if _on == RageOfMages2Alm.SectionKindE.structures:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.StructuresSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.objects:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.ObjectsSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.units:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.UnitsSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.tiles:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.TilesSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.players:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.PlayersSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.effects:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.EffectsSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.sacks:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.SacksSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.triggers:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.TriggersSec(_io__raw_body, self, self._root)
            elif _on == RageOfMages2Alm.SectionKindE.heights:
                self._raw_body = self._io.read_bytes(self.header.data_size)
                _io__raw_body = KaitaiStream(BytesIO(self._raw_body))
                self.body = RageOfMages2Alm.HeightsSec(_io__raw_body, self, self._root)
            else:
                self.body = self._io.read_bytes(self.header.data_size)


    class TriggerEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(128), 0, False)).decode(u"ASCII")
            self.check_ids = [None] * (6)
            for i in range(6):
                self.check_ids[i] = self._io.read_u4le()

            self.instance_ids = [None] * (4)
            for i in range(4):
                self.instance_ids[i] = self._io.read_u4le()

            self.check_operators = [None] * (3)
            for i in range(3):
                self.check_operators[i] = self._io.read_u4le()

            self.run_once_flag = self._io.read_u4le()


    class InstanceEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ASCII")
            self.type = KaitaiStream.resolve_enum(RageOfMages2Alm.InstanceType, self._io.read_u4le())
            self.id = self._io.read_u4le()
            self.run_once_flag = self._io.read_u4le()
            self.argument_values = [None] * (10)
            for i in range(10):
                self.argument_values[i] = self._io.read_u4le()

            self.argument_types = [None] * (10)
            for i in range(10):
                self.argument_types[i] = KaitaiStream.resolve_enum(RageOfMages2Alm.ArgumentType, self._io.read_u4le())

            self.argument_names = [None] * (10)
            for i in range(10):
                self.argument_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ASCII")



    class StructuresSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.structures = [None] * (self._root.general.structure_count)
            for i in range(self._root.general.structure_count):
                self.structures[i] = RageOfMages2Alm.StructureEntry(self._io, self, self._root)



    class SacksSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sacks = [None] * (self._root.general.sack_count)
            for i in range(self._root.general.sack_count):
                self.sacks[i] = RageOfMages2Alm.SackEntry(self._io, self, self._root)



    class GeneralSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()
            self.negative_sun_angle = self._io.read_f4le()
            self.time_in_minutes = self._io.read_u4le()
            self.darkness = self._io.read_u4le()
            self.contrast = self._io.read_u4le()
            self.use_tiles = self._io.read_u4le()
            self.player_count = self._io.read_u4le()
            self.structure_count = self._io.read_u4le()
            self.unit_count = self._io.read_u4le()
            self.logic_count = self._io.read_u4le()
            self.sack_count = self._io.read_u4le()
            self.group_count = self._io.read_u4le()
            self.tavern_count = self._io.read_u4le()
            self.store_count = self._io.read_u4le()
            self.pointer_count = self._io.read_u4le()
            self.music_count = self._io.read_u4le()
            self.map_name = self._io.read_bytes(64)
            self.rec_player_count = self._io.read_u4le()
            self.map_level = self._io.read_u4le()
            self.junk = self._io.read_bytes(8)
            self.author = self._io.read_bytes(512)


    class EffectModifier(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.modifier_type = self._io.read_u2le()
            self.modifier_value = self._io.read_u4le()


    class BridgeInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.width = self._io.read_u4le()
            self.height = self._io.read_u4le()


    class SectionHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.some_number = self._io.read_u4le()
            self.header_size = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            self.section_kind = KaitaiStream.resolve_enum(RageOfMages2Alm.SectionKindE, self._io.read_u4le())
            self.random_seed = self._io.read_u4le()


    class CheckEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ASCII")
            self.type = KaitaiStream.resolve_enum(RageOfMages2Alm.CheckType, self._io.read_u4le())
            self.id = self._io.read_u4le()
            self.run_once_flag = self._io.read_u4le()
            self.argument_values = [None] * (10)
            for i in range(10):
                self.argument_values[i] = self._io.read_u4le()

            self.argument_types = [None] * (10)
            for i in range(10):
                self.argument_types[i] = KaitaiStream.resolve_enum(RageOfMages2Alm.ArgumentType, self._io.read_u4le())

            self.argument_names = [None] * (10)
            for i in range(10):
                self.argument_names[i] = (KaitaiStream.bytes_terminate(self._io.read_bytes(64), 0, False)).decode(u"ASCII")



    class AlmHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not self.magic == b"\x4D\x37\x52\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x4D\x37\x52\x00", self.magic, self._io, u"/types/alm_header/seq/0")
            self.header_size = self._io.read_u4le()
            self.mysterious_size = self._io.read_u4le()
            self.section_count = self._io.read_u4le()
            self.random_seed = self._io.read_u4le()


    class TriggersSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.instance_count = self._io.read_u4le()
            self.instances = [None] * (self.instance_count)
            for i in range(self.instance_count):
                self.instances[i] = RageOfMages2Alm.InstanceEntry(self._io, self, self._root)

            self.check_count = self._io.read_u4le()
            self.checks = [None] * (self.check_count)
            for i in range(self.check_count):
                self.checks[i] = RageOfMages2Alm.CheckEntry(self._io, self, self._root)

            self.trigger_count = self._io.read_u4le()
            self.triggers = [None] * (self.trigger_count)
            for i in range(self.trigger_count):
                self.triggers[i] = RageOfMages2Alm.TriggerEntry(self._io, self, self._root)



    class StructureEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u4le()
            self.y = self._io.read_u4le()
            self.type_id = self._io.read_u4le()
            self.health = self._io.read_u2le()
            self.player_id = self._io.read_u4le()
            self.id = self._io.read_u2le()
            if self.type_id == 33:
                self.bridge_details = RageOfMages2Alm.BridgeInfo(self._io, self, self._root)



    class PlayerEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.color_id = self._io.read_u4le()
            self.flags = self._io.read_u4le()
            self.money = self._io.read_u4le()
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(32), 0, False)).decode(u"ASCII")
            self.diplomacy_states = [None] * (16)
            for i in range(16):
                self.diplomacy_states[i] = self._io.read_u2le()



    class UnitEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u4le()
            self.y = self._io.read_u4le()
            self.type_id = self._io.read_u2le()
            self.face_id = self._io.read_u2le()
            self.flags = self._io.read_u4le()
            self.flags2 = self._io.read_u4le()
            self.server_id = self._io.read_u4le()
            self.player_id = self._io.read_u4le()
            self.sack_id = self._io.read_u4le()
            self.direction = self._io.read_u4le()
            self.hp = self._io.read_s2le()
            self.max_hp = self._io.read_s2le()
            self.unit_id = self._io.read_u4le()
            self.group_id = self._io.read_u4le()


    class TilesSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_tiles = [None] * ((self._root.general.width * self._root.general.height))
            self.tiles = [None] * ((self._root.general.width * self._root.general.height))
            for i in range((self._root.general.width * self._root.general.height)):
                self._raw_tiles[i] = self._io.read_bytes(2)
                _io__raw_tiles = KaitaiStream(BytesIO(self._raw_tiles[i]))
                self.tiles[i] = RageOfMages2Alm.TileEntry(_io__raw_tiles, self, self._root)



    class ItemEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.item_id = self._io.read_u4le()
            self.wielded = self._io.read_u2le()
            self.effect_id = self._io.read_u4le()


    class SackEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.item_count = self._io.read_u4le()
            self.unit_id = self._io.read_u4le()
            self.x = self._io.read_u4le()
            self.y = self._io.read_u4le()
            self.money = self._io.read_u4le()
            self.items = [None] * (self.item_count)
            for i in range(self.item_count):
                self.items[i] = RageOfMages2Alm.ItemEntry(self._io, self, self._root)



    class EffectsSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.effect_count = self._io.read_u4le()
            self.entries = [None] * (self.effect_count)
            for i in range(self.effect_count):
                self.entries[i] = RageOfMages2Alm.EffectEntry(self._io, self, self._root)



    class EffectEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.corrupt_effect_id = self._io.read_u4le()
            self.trap_x = self._io.read_u4le()
            self.trap_y = self._io.read_u4le()
            self.flags_or_magic_sphere = self._io.read_u2le()
            self.service_data = self._io.read_u8le()
            self.modifier_count = self._io.read_u4le()
            self.modifiers = [None] * (self.modifier_count)
            for i in range(self.modifier_count):
                self.modifiers[i] = RageOfMages2Alm.EffectModifier(self._io, self, self._root)



    class UnitsSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.units = [None] * (self._root.general.unit_count)
            for i in range(self._root.general.unit_count):
                self.units[i] = RageOfMages2Alm.UnitEntry(self._io, self, self._root)



    class PlayersSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.players = [None] * (self._root.general.player_count)
            for i in range(self._root.general.player_count):
                self.players[i] = RageOfMages2Alm.PlayerEntry(self._io, self, self._root)



    class HeightsSec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.heights = [None] * ((self._root.general.width * self._root.general.height))
            for i in range((self._root.general.width * self._root.general.height)):
                self.heights[i] = self._io.read_u1()



    class TileEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tile_id = self._io.read_u2le()



