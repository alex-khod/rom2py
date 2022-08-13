from .base import *
from .base import A256, A256Frame

loaded = False
try:
    from ._sprites_cpp import A256Cpp
    A256 = A256Cpp
    A256._record_class.load_dll()
    loaded = True
except:
    import traceback
    traceback.print_exc()
    print("Can't load cpp, fallback to numba")

# try:
#     from ._sprites_numba import A256Numba
#     A256 = A256Numba
#     loaded = True
# except:
#     import traceback
#     traceback.print_exc()
#     print("Can't load numba, fallback to python")
