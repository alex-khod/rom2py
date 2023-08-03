import os
from dataclasses import dataclass, field
from typing import Optional

from src.formats.autogenerated import rage_of_mages_1_reg

RageOfMages1Reg = rage_of_mages_1_reg.RageOfMages1Reg


class MapObjectInfo:
    fields = ['ID',
              'DescText'  # description
              'File',  # file_id
              'Index',  # index of sprite in file -> sprite_index
              'Phases',  # len of animation frames
              'Parent',  # id of parent object with actual length, height, centerx, centery
              'Width', 'Height', 'CenterX', 'CenterY', 'AnimationTime', 'AnimationFrame',
              'DeadObject',  # id of dead object
              'InMapEditor', 'IconID']


class Registry(RageOfMages1Reg):
    def walk(self, path=""):
        for item in self._walk(self.nodes.header, path):
            yield item

    def _walk(self, node_header, path=""):
        for header in node_header:
            if header.rec_type == header.rec_type.__class__.directory:
                for item in self._walk(header.value.value.header, os.path.join(path, header.name)):
                    yield item
            else:
                yield path, header

    def _load_records(self, records_raw, defaultfactory=None):
        if defaultfactory is None:
            defaultfactory = lambda: {}
            # assuming RegistryHeaderList of object properties
        records = {}
        for header_list in records_raw:
            record = defaultfactory()
            properties = header_list.value.value.header
            for prop in properties:
                field = prop.name.lower()
                record[field] = prop.value.value
            records[record['id']] = record
        return records

    def _inherit_parents(self, records: dict):
        records = {k: v.copy() for k, v in records.items()}
        for rid, record in records.items():
            parent = record
            while 'parent' in parent:
                parent = records[parent['parent']]
            for field in parent.keys():
                if field not in record:
                    record[field] = parent[field]
            records[rid] = record
        return records


class StructureRegistry(Registry):

    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io, _parent, _root)
        nodes = self.nodes.header
        global_info = next(filter(lambda x: x.name == "Global", nodes)).value.value.header
        # self.structure_count = next(filter(lambda x: x.name == "StructureCount", global_info)).value.value
        structures_raw = list(filter(lambda x: x.name != "Global", nodes))
        self._structures_by_id = self._load_records(structures_raw)
        for k, v in self._structures_by_id.items():
            self._structures_by_id[k]['filename'] = self._structures_by_id[k]['file']
        self.structures_by_id = self._inherit_parents(self._structures_by_id)
        self.structures = list(self.structures_by_id.values())


@dataclass
class UnitRecord:
    desctext: str
    id: int
    file: int
    filename: str
    index: int
    movephases: int
    movebeginphases: int
    attackphases: int
    dyingphases: int
    bonephases: int
    width: int
    height: int
    centerx: int
    centery: int
    selectionx1: int
    selectionx2: int
    selectiony1: int
    selectiony2: int
    dying: int
    palette: int
    attackdelay: int
    infopicture: str
    attackanimframe: list[int]
    attackanimtime: list[int]
    moveanimframe: list[int]
    moveanimtime: list[int]
    sound: int
    tilesize: int = 0
    z: int = 0
    shootoffset: list[int] = None
    shootdelay: list[int] = None
    projectile: int = None
    parent: Optional[int] = None
    idleanimframe: list[int] = None
    idleanimtime: list[int] = None
    idlephases: int = 0
    flip: bool = False
    inmapeditor: bool = False


class UnitRegistry(Registry):
    units_by_id: dict[int, "UnitRecord"]

    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io, _parent, _root)
        nodes = self.nodes.header
        global_info = next(filter(lambda x: x.name == "Global", nodes)).value.value.header
        self.unit_count = next(filter(lambda x: x.name == "UnitCount", global_info)).value.value
        self.file_count = next(filter(lambda x: x.name == "FileCount", global_info)).value.value
        files_raw = next(filter(lambda x: x.name == "Files", nodes)).value.value.header
        self.files = [header.value.value for header in files_raw]
        units_raw = list(filter(lambda x: x.name not in ["Global", "Files"], nodes))
        self.units_raw = units_raw
        defaults = lambda: {"bonephases": 0,
                            "dyingphases": 0}
        self._units_by_id = self._load_records(units_raw, defaults)
        for k, v in self._units_by_id.items():
            self._units_by_id[k]['filename'] = self.files[v['file']]
        self._units_by_id = self._inherit_parents(self._units_by_id)
        self.units_by_id = {k: UnitRecord(**v) for k, v in self._units_by_id.items()}
        self.units = list(self.units_by_id.values())
        assert (len(files_raw) == self.file_count)
        assert (len(units_raw) == self.unit_count)


class ObjectRegistry(Registry):

    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io, _parent, _root)
        nodes = self.nodes.header
        global_info = next(filter(lambda x: x.name == "Global", nodes)).value.value.header
        self.object_count = next(filter(lambda x: x.name == "ObjectCount", global_info)).value.value
        self.file_count = next(filter(lambda x: x.name == "FileCount", global_info)).value.value
        files_raw = next(filter(lambda x: x.name == "Files", nodes)).value.value.header
        self.files = [header.value.value for header in files_raw]
        objects_raw = list(filter(lambda x: x.name not in ["Global", "Files"], nodes))
        objects_by_id = self._load_records(objects_raw, lambda: {'index': 0})
        for k, v in objects_by_id.items():
            objects_by_id[k]['filename'] = self.files[v['file']]
        self.objects_by_id = {k: v for k, v in objects_by_id.items() if not "fire" in v["filename"]}
        self.objects_by_id = self._inherit_parents(self.objects_by_id)
        self.objects = list(self.objects_by_id.values())
        assert (len(files_raw) == self.file_count)
        assert (len(objects_raw) == self.object_count)


class ProjectileRegistry(Registry):
    def __init__(self, _io, _parent=None, _root=None):
        super().__init__(_io, _parent, _root)
        nodes = self.nodes.header
        projectiles_raw = list(filter(lambda x: x.name != "Global", nodes))
        self.projectiles_by_id = self._load_records(projectiles_raw)
