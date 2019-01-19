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
from typing import Union, Iterable, Optional
import sysconfig
import hashlib
import sys
import os
from datetime import datetime

from .compat import open, implementation
from . import mpi
from .mpi import Path, PathSeq
from .log import logger

ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def modification_date(filename):
    """Get the modification date of a file"""
    return datetime.fromtimestamp(os.path.getmtime(str(filename)))


def has_to_build(output_file: Path, input_file: Path):
    """Check if a file has to be (re)built"""
    output_file = PathSeq(output_file)
    input_file = PathSeq(input_file)
    if not output_file.exists():
        return True
    mod_date_output = modification_date(output_file)
    if mod_date_output < modification_date(input_file):
        return True
    return False


def make_hex(src):
    """Produce a hash from a sting"""
    return hashlib.md5(src.encode("utf8")).hexdigest()


def name_ext_from_path_pythran(path_pythran):
    """Return an extension name given the path of a Pythran file"""

    name = None
    if mpi.rank == 0:
        path_pythran = PathSeq(path_pythran)
        if path_pythran.exists():
            with open(path_pythran) as file:
                src = file.read()
        else:
            src = ""

        name = path_pythran.stem + "_" + make_hex(src) + ext_suffix

    return mpi.bcast(name)


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

    def block_until_avail(self, parallel=True):

        if mpi.rank == 0:
            if parallel:
                limit = self.limit_nb_processes
            else:
                limit = 1

            while len(self.processes) >= limit:
                time.sleep(self.deltat)
                self.processes = [
                    process
                    for process in self.processes
                    if process.is_alive_root()
                ]

        mpi.barrier()

    def wait_for_all_extensions(self):
        """Wait until all compilation processes are done"""
        if mpi.rank == 0:
            while self.processes:
                time.sleep(self.deltat)
                self.processes = [
                    process
                    for process in self.processes
                    if process.is_alive_root()
                ]

        mpi.barrier()

    def compile_with_pythran(
        self,
        path: Path,
        name_ext_file: Optional[str] = None,
        native=True,
        xsimd=True,
        openmp=False,
        str_pythran_flags: Optional[str] = None,
        parallel=True,
        force=True,
    ):

        if name_ext_file is None:
            name_ext_file = name_ext_from_path_pythran(path)

        if not force:
            path_out = path.with_name(name_ext_file)
            if not has_to_build(path_out, path):
                logger.warning(
                    f"Do not pythranize {path} because it seems up-to-date "
                    "(but the compilation options may have changed). "
                    "You can force the compilation with the option -f."
                )
                return

        if mpi.rank == 0:
            logger.info(f"Schedule pythranization of file {path}")

        if str_pythran_flags is not None:
            flags = str_pythran_flags.strip().split()
        else:
            flags = []

        def update_flags(flag):
            if flag not in flags:
                flags.append(flag)

        if native:
            update_flags("-march=native")

        if xsimd:
            update_flags("-DUSE_XSIMD")

        if openmp:
            update_flags("-fopenmp")

        if logger.is_enable_for("info"):
            update_flags("-v")

        words_command = [
            sys.executable,
            "-m",
            "transonic_cl.run_pythran",
            path.name,
        ]

        words_command.extend(("-o", name_ext_file))

        words_command.extend(flags)

        cwd = path.parent
        if implementation == "PyPy":
            cwd = str(cwd)
            words_command = [str(word) for word in words_command]

        self.block_until_avail(parallel)

        process = None
        if mpi.rank == 0:
            process = subprocess.Popen(words_command, cwd=cwd)

        process = mpi.ShellProcessMPI(process)

        if mpi.rank == 0:
            self.processes.append(process)
        return process


scheduler = SchedulerPopen()


def wait_for_all_extensions():
    """Wait until all compilation processes are done"""
    scheduler.wait_for_all_extensions()


def compile_pythran_files(
    paths: Iterable[Path], str_pythran_flags: str, parallel=True, force=True
):
    for path in paths:
        scheduler.compile_with_pythran(
            path,
            str_pythran_flags=str_pythran_flags,
            parallel=parallel,
            force=force,
        )


def compile_pythran_file(
    path: Union[Path, str],
    name_ext_file: Optional[str] = None,
    native=True,
    xsimd=True,
    openmp=False,
):
    if not isinstance(path, Path):
        path = Path(path)

    # return the process
    return scheduler.compile_with_pythran(
        path, name_ext_file, native=native, xsimd=xsimd, openmp=openmp
    )
