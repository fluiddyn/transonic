Defining Pythran functions with type hints
==========================================

First a minimalist example:

.. literalinclude:: type_hints_simple.py

Nice but very limited... So it possible to mix type hints and :code:`# pythran
def` commands.

.. literalinclude:: mixed_classic_type_hint.py

Moreover, if you like `C++11 template
<https://en.cppreference.com/w/cpp/language/templates>`_, you can write:

.. literalinclude:: type_hints.py

If you don't like generic templating, you can also just write

.. literalinclude:: type_hints_notemplate.py

Yes, this one is neat!

Note that one can also just write Pythran type-string in type annotations::

    @boost
    def myfunc(a: "float[3, :]", b: float):
        ...

Finally, array types with only one number of dimension can simply be
defined like this::

    from fluidpythran import Array

    A = Array[float, "3d"]

Which has actually the same effect as::

    A = "float[:, :, :]"
