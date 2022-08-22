# cython: language_level=3
# cython: infer_types=True

import numpy as np

def ROM256_to_color_indexes(char* data, int data_size, int w, int h):
    output = np.zeros((h, w), dtype=np.uint8)
    cdef Py_ssize_t offset = 0
    cdef Py_ssize_t  x = 0
    cdef Py_ssize_t  y = 0

    while offset < data_size:
        _byte = data[offset]
        val, code = _byte & 0x3f, _byte & 0xc0
        offset += 1
        if code > 0:
            # skip transparent bytes
            if code == 0x40:
                y += val
            else:
                x += val
            continue

        for _ in range(val):
            y += x // w
            x = x % w
            idx = data[offset]
            # check if there is non-zero data byte. if there is at least one, there will be errors on paletting..
            # assert idx > 0
            output[y, x] = idx
            offset += 1
            x += 1
    return output
