#define PY_SSIZE_T_CLEAN
#include <Python.h>
typedef unsigned char uint8_t;
typedef unsigned int  uint32_t;

void ROM256_to_color_indexes_impl (uint8_t* data, uint8_t * output, uint32_t data_size, uint32_t w, uint32_t h)
{
    uint32_t x = 0;
    uint32_t y = 0;
    uint32_t offset = 0;
    while (offset < data_size)
    {
        uint8_t _byte = data[offset];
        uint8_t val = _byte & 0x3F;
        uint8_t code = _byte & 0xC0;
        offset += 1;

        if (code > 0) {
            if (code == 0x40) y += val; else x += val;
            continue;
        }

        for (int i = 0; i < val; i++) {
            y += x / w;
            x = x % w;
            uint32_t _xy = y * w + x;
            output[_xy] = data[offset];
            offset += 1;
            x += 1;
        }
    }
}

PyObject* ROM256_to_color_indexes (PyObject* self /* module */, PyObject* args)
{
    Py_buffer data;
    Py_buffer output;
    uint32_t data_size, w, h;

    if(!PyArg_ParseTuple(args, "yy*iii", &data, &output, &data_size, &w, &h)) {
        return NULL;
    }

    //printf("(%d) ds%d w%d h%d\n", output.len, data_size, w, h);
    ROM256_to_color_indexes_impl((uint8_t *)  data.buf, (uint8_t *) output.buf, data_size, w, h);
    Py_INCREF(Py_None);
    return Py_None;
}

void ROM16A_to_color_indexes_impl (uint8_t * data, uint8_t * output, uint32_t data_size, uint32_t w, uint32_t h)
{
    uint32_t x = 0;
    uint32_t y = 0;
    uint32_t offset = 0;
    while (offset < data_size)
    {
        uint8_t val = data[offset];
        uint8_t code = data[offset+1];
        offset += 2;

        if (code > 0) {
            if (code == 0x40) y += val; else x += val;
            continue;
        }

        for (uint32_t i = 0; i < val; i++) {
            y += x / w;
            x = x % w;
            uint32_t _xy = y * w + x;

            uint32_t raw = data[offset] + (data[offset + 1] << 8);
            uint8_t idx = (raw >> 1) & 0xFF;
            uint8_t alpha = ((raw >> 9) & 0x0F) * 0x11;
            output[_xy * 2] = idx;
            output[_xy * 2 + 1] = alpha;
            offset += 2;
            x += 1;
        }
    }
}

PyObject* ROM16A_to_color_indexes (PyObject* self /* module */, PyObject* args)
{
//    uint8_t* data;
    Py_buffer data;
    Py_buffer output;
    uint32_t data_size, w, h;

    if(!PyArg_ParseTuple(args, "y*y*iii", &data, &output, &data_size, &w, &h)) {
        return NULL;
    }

//    printf("(%d) ds%d w%d h%d\n", output.len, data_size, w, h);
    ROM16A_to_color_indexes_impl((uint8_t *) data.buf, (uint8_t *) output.buf, data_size, w, h);
    Py_INCREF(Py_None);
    return Py_None;
}

PyMethodDef module_methods[] =
{
    {"ROM256_to_color_indexes", ROM256_to_color_indexes, METH_VARARGS, "Method description"},
    {"ROM16A_to_color_indexes", ROM16A_to_color_indexes, METH_VARARGS, "Method description"},
    {NULL, NULL, 0, NULL} // this struct signals the end of the array
};

// struct representing the module
static struct PyModuleDef routines =
{
    PyModuleDef_HEAD_INIT, // Always initialize this member to PyModuleDef_HEAD_INIT
    "src._c_extensions.routines", // module name
    "Module description", // module description
    -1, // module size (more on this later)
    module_methods // methods associated with the module
};

// function that initializes the module
PyMODINIT_FUNC PyInit_routines()
{
    return PyModule_Create(&routines);
}