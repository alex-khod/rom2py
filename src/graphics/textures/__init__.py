import pyglet
from pyglet.image.atlas import Allocator, AllocatorException

from pyglet.image import Texture


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
            texture_factory = lambda width, height: pyglet.image.Texture.create(width, height)
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
