Object oriented programming!
============================

OOP is not natively supported by Pythran so it is not a pleasure to use Pythran
in Python classes. One needs to rewrite functions in another modules and call
these functions in the methods: boring, bad in terms of readability and good to
introduce bugs...

With Transonic, one can easily use Pythran for methods:

.. literalinclude:: methods.py

.. warning ::

    For implementation reasons, we *need* to decorate the methods (with
    :code:`@boost` or :code:`@jit`) and the classes (with
    :code:`@boost`)...

.. warning ::

    One has to be very careful with assignments in methods. For example,
    :code:`self.attr = 1` does not work but :code:`self.myarray[:] = 1` should
    work (because it is not a real assignment).

.. warning ::

    Calling another method in a transonified method is *not yet* supported!

Function calls in methods are supported!

.. literalinclude:: methods_using_function.py

We can also use the :code:`jit` decorator for methods!

.. literalinclude:: methods_jit.py
