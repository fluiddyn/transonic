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

.. autofunction:: compile_extension

"""

import multiprocessing
import subprocess
import time
from typing import Union, Optional
import sysconfig
import hashlib
import sys
import os
from datetime import datetime

from transonic import mpi
from transonic.mpi import Path, PathSeq
from transonic.log import logger
from transonic.progress import track, Progress

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


class SchedulerPopen:
    """Limit the number of compilations performed in parallel"""

    deltat = 0.2

    def __init__(self, parallel=True):
        if mpi.rank > 0:
            return
        self.processes = []
        self.progress = Progress(redirect_stdout=False, redirect_stderr=False)
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

            while (
                len(
                    self.processes,
                )
                >= limit
            ):
                time.sleep(self.deltat)
                self.processes = [
                    process
                    for process in self.processes
                    if process.is_alive_root()
                ]

        mpi.barrier(timeout=None)

    def wait_for_all_extensions(self):
        """Wait until all compilation processes are done"""
        if mpi.rank == 0:
            total = len(scheduler.processes)
            task = self.progress.add_task("Wait for all extensions", total=total)

            while self.processes:
                time.sleep(self.deltat)
                self.processes = [
                    process
                    for process in self.processes
                    if process.is_alive_root()
                ]
                self.progress.update(task, advance=total - len(self.processes))

        mpi.barrier(timeout=None)

    def compile_extension(
        self,
        path: Path,
        backend: str,
        name_ext_file: str,
        native=False,
        xsimd=False,
        openmp=False,
        str_accelerator_flags: Optional[str] = None,
        parallel=True,
        force=True,
    ):
        if not force:
            path_out = path.with_name(name_ext_file)
            if not has_to_build(path_out, path):
                logger.warning(
                    f"Do not {backend}ize {path} because it seems up-to-date "
                    "(but the compilation options may have changed). "
                    "You can force the compilation with the option -f."
                )
                return

        if mpi.rank == 0:
            task = self.progress.add_task(
                f"Schedule {backend}ization: {path.name}"  # .rjust(60)[:60]
            )

        def advance(value):
            if mpi.rank == 0:
                self.progress.update(task, advance=value)

        if str_accelerator_flags is not None:
            flags = str_accelerator_flags.strip().split()
        else:
            flags = []

        def update_flags(flag):
            if flag not in flags:
                flags.append(flag)

        if native and os.name != "nt":
            update_flags("-march=native")

        if xsimd:
            update_flags("-DUSE_XSIMD")

        if openmp:
            update_flags("-fopenmp")

        if logger.is_enable_for("debug"):
            update_flags("-v")

        words_command = [
            sys.executable,
            "-m",
            "transonic_cl.run_backend",
            path.name,
            "-b",
            backend,
        ]

        words_command.extend(("-o", name_ext_file))

        words_command.extend(flags)

        cwd = path.parent

        advance(10)
        self.block_until_avail(parallel)
        advance(20)

        process = None
        if mpi.rank == 0:
            stdout = stderr = subprocess.PIPE
            process = subprocess.Popen(
                words_command,
                cwd=cwd,
                stdout=stdout,
                stderr=stderr,
                universal_newlines=True,
            )

        process = mpi.ShellProcessMPI(process)

        if mpi.rank == 0:
            self.processes.append(process)

        advance(70)
        time.sleep(0.5)
        # FIXME: If we don't remove the task, duplicate progress bars appear
        self.progress.remove_task(task)

        return process


scheduler = SchedulerPopen()


def wait_for_all_extensions():
    """Wait until all compilation processes are done"""
    with scheduler.progress:
        scheduler.wait_for_all_extensions()


def compile_extension(
    path: Union[Path, str],
    backend: str,
    name_ext_file: str,
    native=False,
    xsimd=False,
    openmp=False,
    str_accelerator_flags: Optional[str] = None,
    parallel=False,
    force=False,
):
    if not isinstance(path, Path):
        path = Path(path)

    # return the process
    with scheduler.progress:
        return scheduler.compile_extension(
            path,
            backend,
            name_ext_file,
            native=native,
            xsimd=xsimd,
            openmp=openmp,
            str_accelerator_flags=str_accelerator_flags,
            parallel=parallel,
            force=force,
        )
