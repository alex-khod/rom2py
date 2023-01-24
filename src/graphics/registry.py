import os.path

from profilehooks import timecall

from src.graphics.textures import TextureAtlas, TextureBin, Texture
from pyglet.gl import *
from src.resources import Resources


def rom256_atlas():
    def texture_factory(width, height):
        tex = Texture.create(width, height, internalformat=1, fmt=GL_RED)
        return tex

    acount = 0

    def atlas_factory(width, height):
        nonlocal acount
        acount += 1
        return TextureAtlas(width, height, texture_factory=texture_factory)

    atlas = TextureBin(atlas_factory=atlas_factory)
    return atlas


def rom16a_atlas():
    def texture_factory(width, height):
        tex = Texture.create(width, height, internalformat=2, fmt=GL_RED)
        return tex

    def atlas_factory(width, height):
        return TextureAtlas(width, height, texture_factory=texture_factory)

    atlas = TextureBin(atlas_factory=atlas_factory)
    return atlas


class GraphicsRegistry:

    def __init__(self):
        self.rom16a_atlas = rom16a_atlas()
        self.rom256_atlas = rom256_atlas()
        self.palette_atlas = TextureAtlas(width=2048, height=2048)
        self._items = {}
        self.load_all_graphics()

    @timecall
    def load_all_graphics(self):
        graphics_res = Resources["graphics"]
        files = graphics_res.list_files()
        whitelist = ["objects", "units", "structures"]
        files = filter(lambda x: x.startswith("objects") or x.startswith("units") or x.startswith("structures"), files)
        files = filter(lambda x: not x.endswith("spritesb.256"), files)
        # files = filter(lambda x: x.startswith("objects"), files)

        ext_mapping = {
            ".256": self.prepare_rom256,
            # ".16a": self.prepare_rom16a,
            ".pal": self.prepare_palette,
        }

        for path in files:
            ext = os.path.splitext(path)[1]
            if not ext in ext_mapping:
                continue
            store_action = ext_mapping[ext]

            if len(graphics_res[path].bytes) == 0:
                print(f"Zero-length sprite: {path}")
                continue
            content = graphics_res[path].content

            store_action(content, path.lower())
            # import traceback
            # traceback.print_exc()
            # print(f"Error loading: graphics.res @ {path}")

    def __getitem__(self, item):
        return self._items[item]

    def __setitem__(self, key, value):
        self._items[key] = value

    def prepare_palette(self, palette, palette_key):
        palette_data = palette.to_rgb_image_data()
        self._items[palette_key] = self.palette_atlas.add(palette_data)

    def prepare_rom256(self, rom256, sprite_key):
        if rom256.has_palette:
            self.prepare_palette(rom256.palette, sprite_key + "inner")
        textures = []
        for image in rom256:
            texture = image.to_r_image_data()
            texture_region = self.rom256_atlas.add(texture)
            textures.append(texture_region)
        self._items[sprite_key] = textures

    def prepare_rom16a(self, rom16a, sprite_key):
        textures = []
        for image in rom16a:
            texture = image.to_rg_image_data()
            texture_region = self.rom16a_atlas.add(texture)
            textures.append(texture_region)
        self._items[sprite_key] = textures
