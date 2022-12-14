import os.path

import pyglet.image
from profilehooks import timecall, profile

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

    @property
    def ext_mapping(self):
        ext_mapping = {
            ".256": self.prepare_rom256,
            # ".16a": self.prepare_rom16a,
            ".pal": self.prepare_palette,
        }
        return ext_mapping

    @timecall
    def load_all_graphics(self):
        graphics_res = Resources["graphics"]
        files = graphics_res.list_files()
        whitelist = ["objects", "units", "structures"]
        blacklist = ["spritesb.256", "houseb.256"]
        files = filter(lambda x: any([x.startswith(word) for word in whitelist]), files)
        files = filter(lambda x: not any([x.endswith(word) for word in blacklist]), files)
        ext_keys = list(self.ext_mapping.keys())
        files = filter(lambda x: any([x.endswith(ext) for ext in ext_keys]), files)

        for path in files:
            ext = os.path.splitext(path)[1]
            store_action = self.ext_mapping[ext]
            if len(graphics_res[path].bytes) == 0:
                print(f"Zero-length sprite: {path}")
                continue
            try:
                content = graphics_res[path].content
            except Exception as e:
                print(e)
            store_action(content, path.lower())
            # import traceback
            # traceback.print_exc()
            # print(f"Error loading: graphics.res @ {path}")
        png = Resources.from_file("data", "RAR_Heavy_Tank_Ingame0.png")
        self.prepare_png(png, "tank.png")
        light = Resources["graphics", "projectiles", "lightnin", "sprites.16a"].content
        self.prepare_rom16a(light, "lighting")
        fireball = Resources["graphics", "projectiles", "fireball", "sprites.16a"].content
        self.prepare_rom16a(fireball, "fireball")
        teleport = Resources["graphics", "projectiles", "teleport", "sprites.16a"].content
        self.prepare_rom16a(teleport, "teleport")
        explosion = Resources["graphics", "projectiles", "fireexpl", "sprites.16a"].content
        self.prepare_rom16a(explosion, "explosion")

        proj1 = Resources["graphics", "projectiles", "projectiles.pal"].content
        self.prepare_palette(proj1, "projpal")
        proj2 = Resources["graphics", "projectiles", "projectile_.pal"].content
        self.prepare_palette(proj2, "projpal2")

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
        if rom16a.has_palette:
            self.prepare_palette(rom16a.palette, sprite_key + "inner")
        textures = []
        for image in rom16a:
            texture = image.to_rg_image_data()
            texture_region = self.rom16a_atlas.add(texture)
            textures.append(texture_region)
        self._items[sprite_key] = textures

    def prepare_png(self, png, sprite_key):
        w, h = png.width, png.height
        data = png.convert("RGBA").tobytes()
        imdata = pyglet.image.ImageData(width=w, height=h, fmt="RGBA", data=data)
        texture = imdata.create_texture(pyglet.image.Texture)
        self._items[sprite_key] = texture
