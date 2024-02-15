"""Python backend
=================

Internal API
------------

.. autoclass:: SubBackendJITPython
   :members:
   :private-members:

.. autoclass:: PythonBackend
   :members:
   :private-members:

"""

from shutil import copyfile
from typing import Optional

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
    """Main class for the Python backend"""

    backend_name = "python"
    _SubBackendJIT = SubBackendJITPython

    def compile_extension(
        self,
        path_backend,
        name_ext_file=None,
        native=False,
        xsimd=False,
        openmp=False,
        str_accelerator_flags: Optional[str] = None,
        parallel=True,
        force=True,
    ):
        if name_ext_file is None:
            name_ext_file = self.name_ext_from_path_backend(path_backend)

        if not path_backend.exists():
            raise IOError("not path_backend.exists()")

        path_ext = path_backend.with_name(name_ext_file)
        if path_backend != path_ext:
            copyfile(path_backend, path_ext)
        compiling = False
        process = None
        return compiling, process
