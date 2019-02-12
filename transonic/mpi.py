"""Minimalist MPI module
========================

"""

import os
from pathlib import Path
from time import time, sleep

if "TRANSONIC_NO_MPI" in os.environ:
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

if nb_proc > 1:
    comm = comm.Clone()


if nb_proc == 1:

    def bcast(value, root=0):
        return value

    def barrier(timeout=None):
        pass


else:

    _tag = 3 * 7 * 9 * sum(ord(letter) for letter in "mpi transonic")

    def bcast(value, root=0, timeout=5.0, tag=_tag):
        """MPI broadcast

        Should do something similar to::

          value = comm.bcast(value, root=root)

        but with a timeout

        """

        time_comm = time()

        requests = []
        if rank == root:
            for irank in range(nb_proc):
                if irank == rank:
                    continue
                requests.append(comm.isend(value, dest=irank, tag=tag))
        else:
            requests.append(comm.irecv(source=root, tag=tag))

        for request in requests:
            while True:
                ready, received = request.test()
                if ready:
                    break
                if time() - time_comm > timeout:
                    raise TimeoutError(f"rank = {rank}, value = {value}")
                sleep(0.1)

        if rank != root:
            value = received

        # send back something small to say that we received the value
        requests = []
        if rank == root:
            for irank in range(nb_proc):
                if irank == rank:
                    continue
                requests.append(comm.irecv(source=irank, tag=tag + 100))
        else:
            requests.append(comm.isend("ok", dest=0, tag=tag + 100))

        for request in requests:
            while True:
                ready, received = request.test()
                if ready:
                    break
                if time() - time_comm > timeout:
                    raise TimeoutError(f"rank = {rank}, value = {value}")
                sleep(0.1)

        return value

    def barrier(timeout=5):
        if timeout is not None:
            bcast("barrier", timeout=timeout, tag=_tag + 4)
        comm.barrier()


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
            answer = None
            if rank == 0:
                answer = super().exists()

            ret = bcast(("exists", answer), tag=_tag + 1)

            if len(ret) != 2 and ret[0] != "exists":
                print(rank, "bug!!!!", ret, flush=1)
                raise RuntimeError

            kind, answer = ret

            return answer

        def unlink(self):
            if rank == 0:
                super().unlink()
            comm.barrier()

    Path = PathMPI

    def has_to_build(output_file: Path, input_file: Path):
        from . import util

        ret = None
        if rank == 0:
            ret = util.has_to_build(output_file, input_file)
        return bcast(ret, tag=_tag + 2)

    def modification_date(filename):
        from . import util

        ret = None
        if rank == 0:
            ret = util.modification_date(filename)
        return bcast(ret, tag=_tag + 3)


if __name__ == "__main__":
    p = Path.home() / "Dev"
    print(p.exists(), type(p))
    p = PathSeq(p)
    print(p, type(p))
