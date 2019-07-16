from transonic.backends.cython import CythonBackend



paths = ["/home/users/blancfat8p/work/transonic/tmp/for_test_cython.py", ]
BE = CythonBackend(paths)
BE.make_backend_files()