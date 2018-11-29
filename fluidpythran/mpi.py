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


class ShellThreadMPI:
    def __init__(self, thread, root=0):

        if rank != root:
            assert thread is None

        self.thread = thread
        self.root = root

    def is_alive(self):
        if rank == self.root:
            is_alive = self.thread.is_alive()
        else:
            is_alive = None
        return bcast(is_alive, self.root)
