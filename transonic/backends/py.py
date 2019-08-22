from shutil import copyfile

from .base import BackendJIT
from .base_jit import SubBackendJIT


class SubBackendJITPython(SubBackendJIT):
    def make_new_header(self, func, arg_types):
        return ""

    def merge_old_and_new_header(self, path_backend_header, header, func):
        return ""

    def write_new_header(self, path_backend_header, header, arg_types):
        pass


class PythonBackend(BackendJIT):
    backend_name = "python"
    _SubBackendJIT = SubBackendJITPython

    def compile_extension(
        self, path_backend, name_ext_file, native=False, xsimd=False, openmp=False
    ):
        copyfile(path_backend, path_backend.with_name(name_ext_file))
        compiling = False
        process = None
        return compiling, process
