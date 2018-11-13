Defining Pythran functions with type hints
==========================================

First a minimalist example:

.. literalinclude:: type_hints_simple.py

Nice but very limited... So it possible to mix type hints and :code:`# pythran
def` commands.

.. literalinclude:: mixed_classic_type_hint.py

Moreover, if you like C++11 :code:`template`, you can write:

.. literalinclude:: type_hints.py

If you don't like generic templating, you can also just write

.. literalinclude:: type_hints_notemplate.py
