import os
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

modules = [os.path.join("src", "formats", "sprites", "_sprites_cy_func.pyx"),
           os.path.join("src", "rects.pyx")]

c_modules = [Extension("src.formats.sprites._sprites_cext_func",
                       [os.path.join("src", "formats", "sprites", "_sprites_cext_func.c")])]

setup(
    ext_modules=cythonize(modules) + c_modules, include_dirs=[np.get_include()]
)
