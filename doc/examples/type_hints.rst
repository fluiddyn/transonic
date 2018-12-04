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

    @pythran_def
    def myfunc(a: "float[3, :]", b: float):
        ...

Note that if you only need one dimension, array types can be defined like
this::

    from fluidpythran import array

    A = Array[float, "2d"]
