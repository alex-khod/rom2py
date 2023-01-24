#define PY_SSIZE_T_CLEAN
#include <Python.h>
typedef unsigned char uint8_t;
typedef unsigned int  uint32_t;

void ROM256_to_color_indexes_impl(uint8_t* data, uint8_t * output, uint32_t data_size, uint32_t w, uint32_t h)
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

PyObject* ROM256_to_color_indexes(PyObject* self /* module */, PyObject* args)
{
uint8_t* data;
Py_buffer output;
uint32_t data_size, w, h;

if(!PyArg_ParseTuple(args, "yy*iii", &data, &output, &data_size, &w, &h)) {
    return NULL;
}

uint8_t* _output = (uint8_t *)output.buf;
//printf("(%d) ds%d w%d h%d\n", output.len, data_size, w, h);
ROM256_to_color_indexes_impl(data, _output, data_size, w, h);
Py_INCREF(Py_None);
return Py_None;
}

PyMethodDef module_methods[] =
{
    {"ROM256_to_color_indexes", ROM256_to_color_indexes, METH_VARARGS, "Method description"},
    {NULL} // this struct signals the end of the array
};

// struct representing the module
struct PyModuleDef routines =
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