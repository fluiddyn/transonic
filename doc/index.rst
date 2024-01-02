.. Transonic documentation master file

Transonic is a pure Python package (requiring Python >= 3.9) to easily
accelerate modern Python-Numpy code with different accelerators (currently
`Cython <https://cython.org/>`_, `Pythran
<https://github.com/serge-sans-paille/pythran>`_ and `Numba
<https://numba.pydata.org/>`_, but potentially later `Cupy
<https://cupy.chainer.org/>`_, `PyTorch <https://pytorch.org/>`_, `JAX
<https://github.com/google/jax>`_, `Weld <https://www.weld.rs/>`_, `Pyccel
<https://github.com/pyccel/pyccel>`_, `Uarray
<https://github.com/Quansight-Labs/uarray>`_, etc...).

**The accelerators are not hard dependencies of Transonic:** Python codes using
Transonic run fine without any accelerators installed (of course without
speedup)!

.. |mybinder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/fluiddyn/transonic/branch/default?urlpath=lab/tree/doc/ipynb/executed
   :alt: mybinder

You can try Transonic online by clicking this button: |mybinder|.

.. toctree::
   :maxdepth: 2
   :caption: Get started

   install
   short-tour

.. toctree::
   :maxdepth: 2
   :caption: Backends

   backends

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/classic
   examples/type_hints
   examples/using_jit
   examples/blocks
   examples/methods
   ipynb/executed/demo_compile_at_import
   ipynb/executed/demo_jit
   examples/inlined/txt
   examples/writing_benchmarks/bench
   ipynb/executed/bench_fxfy


Modules Reference
-----------------

Here is presented the organization of the package and the documentation of the
modules, classes and functions.

.. autosummary::
   :toctree: generated/
   :caption: Modules Reference

    transonic.aheadoftime
    transonic.analyses
    transonic.backends
    transonic.compiler
    transonic.config
    transonic.dist
    transonic.justintime
    transonic.log
    transonic.mpi
    transonic.run
    transonic.signatures
    transonic.typing
    transonic.util

.. toctree::
   :maxdepth: 1
   :caption: More

   Transonic forge on Heptapod <https://foss.heptapod.net/fluiddyn/transonic>
   Transonic in PyPI  <https://pypi.python.org/pypi/transonic/>
   changes
   roadmap
   thanks
   for_dev/CONTRIBUTING
   Advice for FluidDyn developers <http://fluiddyn.readthedocs.io/en/latest/advice_developers.html>
   for_dev


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
