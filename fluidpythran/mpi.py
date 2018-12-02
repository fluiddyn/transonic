"""Minimalist MPI module
========================

"""

import os
from pathlib import Path

if "FLUIDPYTHRAN_NO_MPI" in os.environ:
    nb_proc = 1
    rank = 0
else:
    try:
        from fluiddyn.util import mpi as _mpi
    except ImportError:
        try:
            from mpi4py import MPI
        except ImportError:
            nb_proc = 1
            rank = 0
        else:
            comm = MPI.COMM_WORLD
            nb_proc = comm.size
            rank = comm.Get_rank()
    else:
        rank = _mpi.rank
        nb_proc = _mpi.nb_proc
        if nb_proc > 1:
            comm = _mpi.comm


def barrier():
    if nb_proc > 1:
        comm.barrier()


def bcast(value, root=0):
    if nb_proc > 1:
        value = comm.bcast(value, root=root)
    return value


class ShellProcessMPI:
    def __init__(self, process, root=0):

        if rank != root:
            assert process is None

        self.process = process
        self.root = root

    def is_alive(self):
        if rank == self.root:
            is_alive = self.is_alive_root()
        else:
            is_alive = None
        return bcast(is_alive, self.root)

    def is_alive_root(self):
        return self.process.poll() is None

PathSeq = Path

if nb_proc > 1:
    class PathMPI(type(Path())):
        def exists(self):
            respons = None
            if rank == 0:
                respons = super().exists()
            return comm.bcast(respons)

        def unlink(self):
            if rank == 0:
                super().unlink()
            comm.barrier()

        def mkdir(self, *args, **kwargs):
            if rank == 0:
                super().mkdir(*args, **kwargs)
            comm.barrier()


    Path = PathMPI

    def has_to_build(output_file: Path, input_file: Path):
        from . import util
        ret = None
        if rank == 0:
            ret = util.has_to_build(output_file, input_file)
        return comm.bcast(ret)

    def modification_date(filename):
        from . import util
        ret = None
        if rank == 0:
            ret = util.modification_date(filename)
        return comm.bcast(ret)


if __name__ == "__main__":
    p = Path.home() / "Dev"
    print(p.exists(), type(p))
    p = PathSeq(p)
    print(p, type(p))
