from .backend import Backend


class NumbaBackend(Backend):
    def __init__(self, paths_py):
        super.__init__(paths_py)
