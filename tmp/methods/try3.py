from functools import wraps

import numpy as np

import pythran_manual


class FluidPythranTemporaryMethod:
    def __init__(self, func):
        self.func = func

    def __call__(self, self_bis, *args, **kwargs):
        raise RuntimeError("Do not call this function!")


def trans_def_method(func):
    return FluidPythranTemporaryMethod(func)


def boost(cls):

    cls_name = cls.__name__

    for key, value in cls.__dict__.items():
        if not isinstance(value, FluidPythranTemporaryMethod):
            continue
        func = value.func
        func_name = func.__name__

        name_backend_func = f"__for_method__{cls_name}__{func_name}"
        backend_func = pythran_manual.__dict__[name_backend_func]

        name_var_code_new_method = f"__code_new_method__{cls_name}__{func_name}"
        code_new_method = pythran_manual.__dict__[name_var_code_new_method]

        namespace = {"backend_func": backend_func}
        exec(code_new_method, namespace)
        setattr(cls, key, wraps(func)(namespace["new_method"]))

    return cls


@boost
class Transmitter:

    freq: float

    def __init__(self, freq):
        self.freq = float(freq)

    @trans_def_method
    def __call__(self, inp: "float[]"):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)


if __name__ == "__main__":
    inp = np.ones(2)
    trans = Transmitter(1.)
    trans(inp)
