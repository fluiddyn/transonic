"""Use Pythran to create extensions
===================================

User API
--------

.. autofunction:: wait_for_all_extensions

Internal API
------------

.. autofunction:: make_hex

.. autoclass:: SchedulerPopen
   :members:
   :private-members:

.. autofunction:: name_ext_from_path_pythran

.. autofunction:: compile_pythran_files

.. autofunction:: compile_pythran_file

"""

import multiprocessing
import subprocess
import time
from pathlib import Path
from typing import Union, Iterable, Optional
import sysconfig
import hashlib

from .compat import open, implementation
from . import mpi

ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"

# if pythran and pythran.__version__ <= "0.9.0":

# avoid a Pythran bug with -o option
# it is bad because then we do not support using many Python versions

ext_suffix_short = "." + ext_suffix.rsplit(".", 1)[-1]


def make_hex(src):
    """Produce a hash from a sting"""
    return hashlib.md5(src.encode("utf8")).hexdigest()


class SchedulerPopen:
    """Limit the number of Pythran compilations performed in parallel

    """

    deltat = 0.2

    def __init__(self, parallel=True):
        if mpi.rank > 0:
            return
        self.processes = []
        if parallel:
            self.limit_nb_processes = max(1, multiprocessing.cpu_count() // 2)
        else:
            self.limit_nb_processes = 1

    def launch_popen(self, words_command, cwd=None, parallel=True):
        """Launch a program (blocking if too many processes launched)"""
        if mpi.rank > 0:
            return

        if parallel:
            limit = self.limit_nb_processes
        else:
            limit = 1

        while len(self.processes) >= limit:
            time.sleep(self.deltat)
            self.processes = [
                process for process in self.processes if process.poll() is None
            ]

        if implementation == "PyPy":
            cwd = str(cwd)
            words_command = [str(word) for word in words_command]

        process = subprocess.Popen(words_command, cwd=cwd)
        self.processes.append(process)
        return process

    def wait_for_all_extensions(self):
        """Wait until all compilation processes are done"""
        if mpi.rank == 0:
            while self.processes:
                time.sleep(self.deltat)
                self.processes = [
                    process for process in self.processes if process.poll() is None
                ]

        mpi.barrier()


scheduler = SchedulerPopen()


def wait_for_all_extensions():
    """Wait until all compilation processes are done"""
    scheduler.wait_for_all_extensions()


def name_ext_from_path_pythran(path_pythran):
    """Return an extension name given the path of a Pythran file"""
    if mpi.rank == 0:
        if path_pythran.exists():
            with open(path_pythran) as file:
                src = file.read()
        else:
            src = ""

        name = path_pythran.stem + "_" + make_hex(src) + ext_suffix_short
    else:
        name = None

    if mpi.nb_proc > 1:
        name = mpi.comm.bcast(name, root=0)

    return name


def compile_pythran_files(
    paths: Iterable[Path], str_pythran_flags: str, parallel=True
):
    if mpi.rank > 0:
        return

    pythran_flags = str_pythran_flags.strip().split()

    for path in paths:
        name_ext = name_ext_from_path_pythran(path)
        words_command = ["pythran", path.name, "-o", name_ext]
        words_command.extend(pythran_flags)
        print("pythranize file", path)
        scheduler.launch_popen(
            words_command, cwd=str(path.parent), parallel=parallel
        )


def compile_pythran_file(
    path: Union[Path, str],
    name_ext_file: Optional[str] = None,
    native=True,
    xsimd=True,
    openmp=False,
):
    if mpi.rank > 0:
        return

    if not isinstance(path, Path):
        path = Path(path)

    words_command = ["pythran", "-v", path.name]

    if name_ext_file is not None:
        words_command.extend(("-o", name_ext_file))

    if native:
        words_command.append("-march=native")

    if xsimd:
        words_command.append("-DUSE_XSIMD")

    if openmp:
        words_command.append("-fopenmp")

    # return the process
    return scheduler.launch_popen(words_command, cwd=str(path.parent))
