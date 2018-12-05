from functools import wraps

import numpy as np

import pythran_manual

code = """

def new_method(self, inp):
    return pythran_func(self.freq, inp)

"""


class FluidPythranTemporaryMethod:
    def __init__(self, func):
        self.func = func

    def __call__(self, self_bis, *args, **kwargs):
        raise RuntimeError("Do not call this function!")


def pythran_def_method(func):
    return FluidPythranTemporaryMethod(func)


def pythran_class(cls):

    cls_name = cls.__name__

    for key, value in cls.__dict__.items():
        if not isinstance(value, FluidPythranTemporaryMethod):
            continue
        func = value.func
        func_name = func.__name__

        name_pythran_func = f"__for_method__{cls_name}__{func_name}"
        pythran_func = pythran_manual.__dict__[name_pythran_func]

        namespace = {"pythran_func": pythran_func}
        exec(code, namespace)
        setattr(cls, key, wraps(func)(namespace["new_method"]))

    return cls


@pythran_class
class Transmitter:

    freq: float

    def __init__(self, freq):
        self.freq = float(freq)

    @pythran_def_method
    def __call__(self, inp: "float[]"):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)
