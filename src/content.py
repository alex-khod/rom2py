import os


def init_mappings():
    # lazy import to not create import loop for formats that access resources:
    # formats -> resources -> content -> formats...
    from src.formats import databin, alm2, sprites, registry, simple

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
        '.256': sprites.A256,
        '.16a': sprites.A16,
        '.bmp': sprites.BmpHandler,
        '.pal': sprites.Palette,
    }

    return name_mapping, ext_map


class Selector:
    """
        Return resource instance by guessing its type using name first, extension second.

        :param resource_data: bytes or file path to pass to resource instance
        :param resource_name: ex. "units.reg"
        :param create_how: str 'from_bytes' or 'from_file'
        :return: resource instance
    """

    name_mapping = None
    ext_map = None

    def __new__(cls, resource_data, resource_name, create_how='from_bytes'):
        if not cls.name_mapping:
            cls.name_mapping, cls.ext_map = init_mappings()

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
