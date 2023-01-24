import os
from setuptools import setup
from Cython.Build import cythonize
import numpy as np


def sprites_module(name):
    return os.path.join("src", "formats", "sprites", name)


modules = [sprites_module(name) for name in ["_sprites_cy_func.pyx"]]

setup(
    ext_modules=cythonize(modules), include_dirs=[np.get_include()]
)

from distutils.core import setup, Extension


def c_module(name):
    return os.path.join("src", "_c_extensions", name)


c_modules = [Extension("src._c_extensions.routines", [c_module("routines.c")])]

setup(
    ext_modules=c_modules
)
