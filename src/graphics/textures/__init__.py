import ctypes

import pyglet
from pyglet.image.atlas import Allocator, AllocatorException

from pyglet.gl import *
import PIL.Image

class Texture(pyglet.image.Texture):
    internalformat = None
    fmt = None

    @classmethod
    def create(cls, width, height, target=GL_TEXTURE_2D, internalformat=GL_RGBA8, min_filter=None, mag_filter=None,
               fmt=GL_RGBA):
        texture = super().create(width, height, target, internalformat, min_filter, mag_filter, fmt)
        texture.internalformat = internalformat
        texture.fmt = fmt
        return texture

    def get_image_data(self, z=0, fmt="RGBA", gl_format=GL_RGBA):
        """Get the image data of this texture.
        Changes to the returned instance will not be reflected in this
        texture.
        :Parameters:
            `z` : int
                For 3D textures, the image slice to retrieve.
        :rtype: :py:class:`~pyglet.image.ImageData`
        """
        glBindTexture(self.target, self.id)

        buf = (GLubyte * (self.width * self.height * self.images * len(fmt)))()

        if pyglet.gl.current_context.get_info().get_opengl_api() == "gles":
            fbo = ctypes.c_uint()
            glGenFramebuffers(1, fbo)
            glBindFramebuffer(GL_FRAMEBUFFER, fbo.value)
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            glCheckFramebufferStatus(GL_FRAMEBUFFER)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.id, self.level)
            glReadPixels(0, 0, self.width, self.height, gl_format, GL_UNSIGNED_BYTE, buf)
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glDeleteFramebuffers(1, fbo)
        else:
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            glGetTexImage(self.target, self.level, gl_format, GL_UNSIGNED_BYTE, buf)

        data = pyglet.image.ImageData(self.width, self.height, fmt, buf)
        if self.images > 1:
            data = data.get_region(0, z * self.height, self.width, self.height)
        return data


class TextureBin:
    """Collection of texture atlases.

    :py:class:`~pyglet.image.atlas.TextureBin` maintains a collection of texture atlases, and creates new
    ones as necessary to accommodate images added to the bin.
    """

    def __init__(self, texture_width=2048, texture_height=2048, atlas_factory: callable = None):
        """Create a texture bin for holding atlases of the given size.

        :Parameters:
            `texture_width` : int
                Width of texture atlases to create.
            `texture_height` : int
                Height of texture atlases to create.
            `border` : int
                Leaves specified pixels of blank space around
                each image added to the Atlases.

        """
        max_texture_size = pyglet.image.get_max_texture_size()
        self.texture_width = min(texture_width, max_texture_size)
        self.texture_height = min(texture_height, max_texture_size)
        if atlas_factory is None:
            atlas_factory = lambda width, height: TextureAtlas(width, height)
        self.atlas_factory = atlas_factory
        self.atlases = []

    def add(self, img, border=0):
        """Add an image into this texture bin.

        This method calls `TextureAtlas.add` for the first atlas that has room
        for the image.

        `AllocatorException` is raised if the image exceeds the dimensions of
        ``texture_width`` and ``texture_height``.

        :Parameters:
            `img` : `~pyglet.image.AbstractImage`
                The image to add.
            `border` : int
                Leaves specified pixels of blank space around
                each image added to the Atlas.

        :rtype: :py:class:`~pyglet.image.TextureRegion`
        :return: The region of an atlas containing the newly added image.
        """
        for atlas in list(self.atlases):
            try:
                return atlas.add(img, border)
            except AllocatorException:
                # Remove atlases that are no longer useful (so that their textures
                # can later be freed if the images inside them get collected).
                if img.width < 64 and img.height < 64:
                    self.atlases.remove(atlas)

        atlas = self.atlas_factory(self.texture_width, self.texture_height)
        self.atlases.append(atlas)
        return atlas.add(img, border)

    @classmethod
    def customize(cls, internalformat=GL_RGBA8, fmt=GL_RGBA):
        def texture_factory(width, height):
            tex = Texture.create(width, height, internalformat=internalformat, fmt=fmt)
            return tex

        def atlas_factory(width, height):
            return TextureAtlas(width, height, texture_factory=texture_factory)

        tex_bin = cls(atlas_factory=atlas_factory)
        return tex_bin


def r_texture_bin():
    return TextureBin.customize(GL_RED, GL_RED)


def rg_texture_bin():
    return TextureBin.customize(GL_RG, GL_RG)


class TextureAtlas:
    """Collection of images within a texture."""

    def __init__(self, width=2048, height=2048, texture_factory=None):
        """Create a texture atlas of the given size.

        :Parameters:
            `width` : int
                Width of the underlying texture.
            `height` : int
                Height of the underlying texture.

        """
        max_texture_size = pyglet.image.get_max_texture_size()
        width = min(width, max_texture_size)
        height = min(height, max_texture_size)
        if texture_factory is None:
            texture_factory = lambda width, height: Texture.create(width, height)
        self.texture = texture_factory(width, height)
        self.allocator = Allocator(width, height)

    def add(self, img, border=0):
        """Add an image to the atlas.

        This method will fail if the given image cannot be transferred
        directly to a texture (for example, if it is another texture).
        :py:class:`~pyglet.image.ImageData` is the usual image type for this method.

        `AllocatorException` will be raised if there is no room in the atlas
        for the image.

        :Parameters:
            `img` : `~pyglet.image.AbstractImage`
                The image to add.
            `border` : int
                Leaves specified pixels of blank space around
                each image added to the Atlas.

        :rtype: :py:class:`~pyglet.image.TextureRegion`
        :return: The region of the atlas containing the newly added image.
        """
        x, y = self.allocator.alloc(img.width + border * 2, img.height + border * 2)
        self.texture.blit_into(img, x + border, y + border, 0)
        return self.texture.get_region(x + border, y + border, img.width, img.height)
