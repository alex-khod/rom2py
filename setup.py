import os
from setuptools import setup
from Cython.Build import cythonize
import numpy as np


def sprites_module(name):
    return os.path.join("src", "formats", "sprites", name)


modules = [sprites_module(name) for name in ["_sprites_cy_func.pyx"]]

setup(
    ext_modules=cythonize(modules), include_dirs=[np.get_include()], language_level=3
)
