"""Minimalist MPI module
========================

"""

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
