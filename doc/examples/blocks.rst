Define accelerated blocks
=========================

.. warning ::

   I'm not satisfied by the syntax for Pythran blocks so I (PA) proposed an
   alternative syntax in `issue #29
   <https://bitbucket.org/fluiddyn/fluidpythran/issues/29>`_.


Transonic blocks can be used with classes and more generally in functions
with lines that cannot be compiled by Pythran.

.. literalinclude:: blocks.py

For blocks, we need a little bit more of Python.

- At import time, we have :code:`ts = Transonic()`, which detects which
  Pythran module should be used and imports it. This is done at import time
  since we want to be very fast at run time.

- In the function, we define a block with three lines of Python and special
  Pythran annotations (:code:`# transonic block`). The 3 lines of Python are used
  (i) at run time to choose between the two branches (:code:`is_transpiled` or
  not) and (ii) at compile time to detect the blocks.

Note that the annotations in the command :code:`# transonic block` are different
(and somehow easier to write) than in the standard command :code:`# pythran
export`.

.. warning ::

    The two branches of the :code:`if ts.is_transpiled` are not equivalent! The
    user has to be careful because it is not difficult to write such buggy code:

    .. code :: python

        c = 0
        if ts.is_transpiled:
            a, b = ts.use_block("buggy_block")
        else:
            # transonic block ()
            a = b = c = 1

        assert c == 1

.. note ::

    The Pythran keyword :code:`or` cannot be used in block annotations (not yet
    implemented, see `issue #2
    <https://bitbucket.org/fluiddyn/fluidpythran/issues/2/implement-keyword-or-in-block-annotation>`_).

Blocks can now also be defined with type hints!

.. literalinclude:: blocks_type_hints.py
