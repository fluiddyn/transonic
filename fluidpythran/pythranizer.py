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
import threading
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
        self.threads = []
        if parallel:
            self.limit_nb_processes = max(1, multiprocessing.cpu_count() // 2)
        else:
            self.limit_nb_processes = 1

    def block_until_avail(self, parallel=True):

        if parallel:
            limit = self.limit_nb_processes
        else:
            limit = 1

        while len(self.threads) >= limit:
            time.sleep(self.deltat)
            self.threads = [
                thread for thread in self.threads if thread.is_alive()
            ]

    # def launch_popen(self, words_command, cwd=None, parallel=True):
    #     """Launch a program (blocking if too many processes launched)"""

    #     if parallel:
    #         limit = self.limit_nb_processes
    #     else:
    #         limit = 1

    #     while len(self.processes) >= limit:
    #         time.sleep(self.deltat)
    #         self.processes = [
    #             process for process in self.processes if process.poll() is None
    #         ]

    #     if implementation == "PyPy":
    #         cwd = str(cwd)
    #         words_command = [str(word) for word in words_command]

    #     process = subprocess.Popen(words_command, cwd=cwd)
    #     self.processes.append(process)
    #     return process

    def wait_for_all_extensions(self):
        """Wait until all compilation processes are done"""
        if mpi.rank == 0:
            while self.threads:
                time.sleep(self.deltat)
                self.threads = [
                    thread
                    for thread in self.threads
                    if thread.is_alive()
                ]

        mpi.barrier()

    def compile_with_pythran(
        self,
        path: Path,
        native=True,
        xsimd=True,
        openmp=False,
        str_pythran_flags: Optional[str] = None,
    ):
        if str_pythran_flags is not None:
            flags = str_pythran_flags.split()
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

        def create_extension():

            words_command = [".pythran-fluid", path.name]
            words_command.extend(flags)

            cwd = path.parent
            if implementation == "PyPy":
                cwd = str(cwd)
                words_command = [str(word) for word in words_command]

            # we don't use subprocess.call on purpose
            process = subprocess.Popen(words_command, cwd=cwd)

            while process.poll() is None:
                time.sleep(0.2)

        # FIXME lock file...

        thread = None
        if mpi.rank == 0:
            thread = threading.Thread(target=create_extension, daemon=True)

        if mpi.nb_proc > 1:
            thread = mpi.ShellThreadMPI(thread)

        self.threads.append(thread)


scheduler = SchedulerPopen()


def wait_for_all_extensions():
    """Wait until all compilation processes are done"""
    scheduler.wait_for_all_extensions()


def name_ext_from_path_pythran(path_pythran):
    """Return an extension name given the path of a Pythran file"""

    name = None
    if mpi.rank == 0:
        if path_pythran.exists():
            with open(path_pythran) as file:
                src = file.read()
        else:
            src = ""

        name = path_pythran.stem + "_" + make_hex(src) + ext_suffix_short

    return mpi.bcast(name)


def compile_pythran_files(
    paths: Iterable[Path], str_pythran_flags: str, parallel=True
):
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
