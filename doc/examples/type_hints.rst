Accelerated functions with type hints
=====================================

First a minimalist example:

.. literalinclude:: type_hints_simple.py

Nice but very limited... So it possible to mix type hints and :code:`# pythran
def` commands.

.. literalinclude:: mixed_classic_type_hint.py

Moreover, you can write:

.. literalinclude:: type_hints_notemplate.py

Yes, this one is neat!

.. note::

    Note that the array types ``A`` and ``A1`` are bound. When ``A.ndim == 1``,
    then ``A1.ndim == 2``, and when ``A.ndim == 3``, then ``A1.ndim == 4``. No
    signatures are produced for ``A.ndim == 1``, ``A1.ndim == 4``.

Note that one can also just write Pythran type-string in type annotations::

    @boost
    def myfunc(a: "float[3, :]", b: float):
        ...

Array types with only one number of dimension can simply be
defined like this::

    from transonic import Array

    A = Array[float, "3d"]

Which has actually the same effect as::

    A = "float[:, :, :]"

But, one can also specify the memory layout, for example for a C-order array
and a strided array::

    A = Array[float, "3d", "C"]
    A_strided = Array[float, "3d", "strided"]

Oh, and you can also write::

    import numpy as np
    from transonic import str2type, typeof

    T = str2type("(int, float)")  # a tuple
    A = typeof(np.empty((2, 2)))

There is also an ``Union`` "type" that can be used similarly as `typing.Union
<https://docs.python.org/3/library/typing.html#typing.Union>`__::

    from transonic import Array, Union

    U = Union[float, Array[float, "3d"]]


All Transonic types are defined in the module :mod:`transonic.typing`.
