import os

from src.formats import databin, alm2, sprites, registry, simple


# using lazy import breaks sprite loader timetests as they fiddle with name_mapping.
# either don't allow formats to have resource dependencies
# or inject dependencies in resources / main
# or load modules by string

class Selector:
    """
        Return resource instance by guessing its type using name first, extension second.

        :param resource_data: bytes or file path to pass to resource instance
        :param resource_name: ex. "units.reg"
        :param create_how: str 'from_bytes' or 'from_file'
        :return: resource instance
    """

    name_mapping = {
        "units.reg": registry.UnitRegistry,
        "structures.reg": registry.StructureRegistry,
        "objects.reg": registry.ObjectRegistry,
        "projectiles.reg": registry.ProjectileRegistry,
        "itemname.bin": simple.ItemnameBin,
        "data.bin": databin.DataBin,
    }

    ext_map = {
        # registry not covered by special
        '.reg': registry.Registry,
        '.glsl': simple.ShaderSource,
        '.txt': simple.TextLines,
        '.alm': alm2.Alm2,
        '.256': sprites.ROM256,
        '.16a': sprites.ROM16A,
        '.bmp': sprites.BmpHandler,
        '.pal': sprites.Palette,
    }

    def __new__(cls, resource_data, resource_name, create_how='from_bytes'):

        ext = os.path.splitext(resource_name)[1]

        resource_handler = None
        if resource_name in cls.name_mapping:
            resource_handler = cls.name_mapping[resource_name]
        elif ext in cls.ext_map:
            resource_handler = cls.ext_map[ext]

        if resource_handler is None:
            raise NotImplemented(f"No content handler for key: {resource_name}")

        if create_how == 'from_bytes':
            return resource_handler.from_bytes(resource_data)
        elif create_how == 'from_file':
            return resource_handler.from_file(resource_data)
