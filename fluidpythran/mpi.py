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