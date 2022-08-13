import numba
import numpy as np
from tests import TestCase

targets = np.zeros(4096, dtype='uint8')


def simple_search(_targets: numba.uint8[:]):
    """ Emulate looking through 41x41 table for 4096 units"""
    x = 20
    y = 20
    for i in range(4096):
        for j in range(41):
            for k in range(41):
                if x > j and y > k:
                    _targets[i] = 1


numba_search = numba.njit(simple_search)

# pre-fire jit
numba_search(targets)


class TestSearch(TestCase):

    def test_simple_search(self):
        simple_search(targets)

    def test_numba_simple_search(self):
        # seems too fast, is loop optimized out of execution?
        numba_search(targets)
