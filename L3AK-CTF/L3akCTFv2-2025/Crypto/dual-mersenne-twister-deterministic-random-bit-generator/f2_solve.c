#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <m4ri/m4ri.h>
#include <Python.h>
#include <numpy/arrayobject.h>


static PyObject* solve_right(PyObject* self, PyObject* args) {
    PyArrayObject *np_A, *np_b;

    // Parse the input NumPy array
    if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &np_A, &PyArray_Type, &np_b)) {
        return NULL;
    }

    // Ensure it's a contiguous NumPy array of type double
    np_A = (PyArrayObject*) PyArray_FROM_OTF((PyObject*) np_A, NPY_BOOL, NPY_ARRAY_IN_ARRAY);
    np_b = (PyArrayObject*) PyArray_FROM_OTF((PyObject*) np_b, NPY_BOOL, NPY_ARRAY_IN_ARRAY);
    if (!np_A || !np_b) {
        Py_XDECREF(np_A);
        Py_XDECREF(np_b);
        return NULL;
    }

    if (PyArray_NDIM(np_A) != 2 || PyArray_NDIM(np_b) != 1) {
        PyErr_SetString(PyExc_ValueError, "Inputs must be a 2d matrix and a vector.");
        Py_DECREF(np_A);
        Py_DECREF(np_b);
        return NULL;
    }
    if (!PyArray_ISCARRAY(np_A) || !PyArray_ISCARRAY(np_b)) {
        PyErr_SetString(PyExc_ValueError, "Data must be C contiguous.");
        Py_DECREF(np_A);
        Py_DECREF(np_b);
        return NULL;
    }
    npy_intp* dims_A = PyArray_DIMS(np_A);
    if (PyArray_DIM(np_b, 0) != dims_A[0]) {
        PyErr_SetString(PyExc_ValueError, "Number of rows in matrix must match length of vector.");
        Py_DECREF(np_A);
        Py_DECREF(np_b);
        return NULL;
    }
    if (dims_A[0] < dims_A[1]) {
        PyErr_SetString(PyExc_ValueError, "Number of rows must be at least number of columns.");
        Py_DECREF(np_A);
        Py_DECREF(np_b);
        return NULL;
    }
    
    npy_intp out_dims[1] = {dims_A[1]};
    PyArrayObject* result = (PyArrayObject*) PyArray_SimpleNew(1, out_dims, NPY_BOOL);
    
    npy_bool* A_data = (npy_bool*) PyArray_DATA(np_A);
    npy_bool* b_data = (npy_bool*) PyArray_DATA(np_b);
    npy_bool* result_data = (npy_bool*) PyArray_DATA(result);
    
    // Use m4ri to solve
    mzd_t *A = mzd_init(dims_A[0], dims_A[1]);
    mzd_t *b = mzd_init(dims_A[0], 1);
    for (int i = 0; i < dims_A[0]; i++) {
        for (int j = 0; j < dims_A[1]; j++) {
            mzd_write_bit(A, i, j, A_data[i * dims_A[1] + j] != 0);
        }
        mzd_write_bit(b, i, 0, b_data[i] != 0);
    }
    if (mzd_solve_left(A, b, 0, 1) != 0) {
        PyErr_SetString(PyExc_ValueError, "Matrix equation has no solutions.");
        Py_DECREF(np_A);
        Py_DECREF(np_b);
        mzd_free(A);
        mzd_free(b);
        return NULL;
    }
    
    for (int i = 0; i < dims_A[1]; i++) {
        result_data[i] = mzd_read_bit(b, i, 0);
    }

    Py_DECREF(np_A);
    Py_DECREF(np_b);
    mzd_free(A);
    mzd_free(b);
    return (PyObject*) result;
}

static PyObject* matmul(PyObject* self, PyObject* args) {
    PyArrayObject *np_A, *np_B;

    // Parse the input NumPy array
    if (!PyArg_ParseTuple(args, "O!O!", &PyArray_Type, &np_A, &PyArray_Type, &np_B)) {
        return NULL;
    }

    // Ensure it's a contiguous NumPy array of type double
    np_A = (PyArrayObject*) PyArray_FROM_OTF((PyObject*) np_A, NPY_BOOL, NPY_ARRAY_IN_ARRAY);
    np_B = (PyArrayObject*) PyArray_FROM_OTF((PyObject*) np_B, NPY_BOOL, NPY_ARRAY_IN_ARRAY);
    if (!np_A || !np_B) {
        Py_XDECREF(np_A);
        Py_XDECREF(np_B);
        return NULL;
    }

    if (PyArray_NDIM(np_A) != 2 || PyArray_NDIM(np_B) != 2) {
        PyErr_SetString(PyExc_ValueError, "Inputs must be 2d matrices.");
        Py_DECREF(np_A);
        Py_DECREF(np_B);
        return NULL;
    }
    if (!PyArray_ISCARRAY(np_A) || !PyArray_ISCARRAY(np_B)) {
        PyErr_SetString(PyExc_ValueError, "Data must be C contiguous.");
        Py_DECREF(np_A);
        Py_DECREF(np_B);
        return NULL;
    }
    npy_intp* dims_A = PyArray_DIMS(np_A);
    npy_intp* dims_B = PyArray_DIMS(np_B);
    
    npy_intp out_dims[2] = {dims_A[0], dims_B[1]};
    PyArrayObject* result = (PyArrayObject*) PyArray_SimpleNew(1, out_dims, NPY_BOOL);
    
    npy_bool* A_data = (npy_bool*) PyArray_DATA(np_A);
    npy_bool* B_data = (npy_bool*) PyArray_DATA(np_B);
    npy_bool* result_data = (npy_bool*) PyArray_DATA(result);
    
    // Use m4ri to solve
    mzd_t *A = mzd_init(dims_A[0], dims_A[1]);
    mzd_t *B = mzd_init(dims_B[0], dims_B[1]);
    mzd_t *C = mzd_init(dims_A[0], dims_B[1]);
    for (int i = 0; i < dims_A[0]; i++) {
        for (int j = 0; j < dims_A[1]; j++) {
            mzd_write_bit(A, i, j, A_data[i * dims_A[1] + j] != 0);
        }
    }
    for (int i = 0; i < dims_B[0]; i++) {
        for (int j = 0; j < dims_B[1]; j++) {
            mzd_write_bit(B, i, j, B_data[i * dims_B[1] + j] != 0);
        }
    }
    
    mzd_mul(C, A, B, 0);
    
    for (int i = 0; i < dims_A[0]; i++) {
        for (int j = 0; j < dims_B[1]; j++) {
            result_data[i * dims_B[1] + j] = mzd_read_bit(C, i, j);
        }
    }

    Py_DECREF(np_A);
    Py_DECREF(np_B);
    mzd_free(A);
    mzd_free(B);
    mzd_free(C);
    return (PyObject*) result;
}

static PyMethodDef f2SolveMethods[] = {
    {"solve_right", solve_right, METH_VARARGS, "Solve system Ax=b in GF(2)"},
    {"matmul", matmul, METH_VARARGS, "Matrix multiply in GF(2)"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef f2solvemodule = {
    PyModuleDef_HEAD_INIT,
    "f2_solve",     // name of module
    NULL,          // module documentation
    -1,            // size of per-interpreter state of the module
    f2SolveMethods
};

PyMODINIT_FUNC PyInit_f2_solve(void) {
    import_array();  // initialize NumPy C API
    return PyModule_Create(&f2solvemodule);
}
