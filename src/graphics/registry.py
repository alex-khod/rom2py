import os.path
import json

import pyglet.image
from profilehooks import timecall, profile

from src.graphics.textures import Texture, TextureAtlas, rg_texture_bin, r_texture_bin
from src.formats import codecs
from pyglet.gl import *
from src.resources import Resources

class GraphicsRegistry:
    tex_encoder = codecs.RawTextureEncoder
    tex_decoder = codecs.RawTextureDecoder

    def __init__(self):
        self.rom16a_bin = rg_texture_bin()
        self.rom256_bin = r_texture_bin()
        self.palette_atlas = TextureAtlas(width=2048, height=2048)
        self._items = {}
        # self.load_all_graphics()
        # self.save("textures_raw")
        self.open("textures_raw")

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
                store_action(content, path.lower())
            except Exception as e:
                print(e)
            # import traceback
            # traceback.print_exc()
            # print(f"Error loading: graphics.res @ {path}")

    def __getitem__(self, item):
        return self._items[item]

    def __setitem__(self, key, value):
        self._items[key] = value

    def prepare_palette(self, palette, palette_key):
        palette_data = palette.to_rgb_image_data()
        self._items[palette_key] = [self.palette_atlas.add(palette_data)]

    def prepare_rom256(self, rom256, sprite_key):
        if rom256.has_palette:
            self.prepare_palette(rom256.palette, sprite_key + "inner")
        textures = []
        for image in rom256:
            texture = image.to_r_image_data()
            texture_region = self.rom256_bin.add(texture)
            textures.append(texture_region)
        self._items[sprite_key] = textures

    def prepare_rom16a(self, rom16a, sprite_key):
        if rom16a.has_palette:
            self.prepare_palette(rom16a.palette, sprite_key + "inner")
        textures = []
        for image in rom16a:
            texture = image.to_rg_image_data()
            texture_region = self.rom16a_bin.add(texture)
            textures.append(texture_region)
        self._items[sprite_key] = textures

    def prepare_png(self, png, sprite_key):
        w, h = png.width, png.height
        data = png.convert("RGBA").tobytes()
        imdata = pyglet.image.ImageData(width=w, height=h, fmt="RGBA", data=data)
        texture = imdata.create_texture(pyglet.image.Texture)
        self._items[sprite_key] = texture

    def save(self, output_path):
        def get_textures():
            textures = {tex.owner.id: tex.owner for tex_list in self._items.values() for tex in tex_list}
            return textures

        def save_textures(textures):
            for tex_id, tex in textures.items():
                tex.save(os.path.join(output_path, "%d.bmp" % tex_id), encoder=self.tex_encoder)

        def get_texture_regions():
            regions = {key: [(tex.x, tex.y, tex.z, tex.width, tex.height, tex.owner.id) for tex in tex_list]
                       for key, tex_list in self._items.items()}
            return regions

        os.makedirs(output_path, exist_ok=True)
        textures = get_textures()
        save_textures(textures)
        texture_regions = get_texture_regions()

        registry_dict = {
            "texture_ids": list(textures.keys()),
            "texture_regions": texture_regions
        }

        registry_path = os.path.join(output_path, "registry.txt")
        with open(registry_path, "w") as f:
            json.dump(registry_dict, f)

    @timecall
    def open(self, path):
        @timecall
        def load_textures(registry):
            textures = {
                int(tex_id): pyglet.image.load(os.path.join(path, "%d.bmp" % tex_id), decoder=self.tex_decoder)
                for tex_id in registry["texture_ids"]
            }
            return textures

        @timecall
        def load_texture_regions(registry, textures):
            texture_regions = {
                key: [pyglet.image.TextureRegion(x, y, z, width, height, owner=textures[tex_id])
                      for (x, y, z, width, height, tex_id) in tex_list]
                for key, tex_list in registry["texture_regions"].items()
            }
            return texture_regions

        registry_path = os.path.join(path, "registry.txt")
        with open(registry_path, "r") as f:
            registry = json.load(f)

        textures = load_textures(registry)
        self.palette_atlas.texture = textures[1]
        registry_items = load_texture_regions(registry, textures)
        self._items = registry_items
