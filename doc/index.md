# Transonic documentation

Transonic is a pure Python package (requiring Python >= 3.9) to easily
accelerate modern Python-Numpy code with different accelerators (currently
[Cython](https://cython.org/), [Pythran](https://github.com/serge-sans-paille/pythran) and [Numba](https://numba.pydata.org/), but potentially later [Cupy](https://cupy.chainer.org/), [PyTorch](https://pytorch.org/), [JAX](https://github.com/google/jax), [Weld](https://www.weld.rs/), [Pyccel](https://github.com/pyccel/pyccel), etc...).

**The accelerators are not hard dependencies of Transonic:** Python code using
Transonic run fine without any accelerators installed (of course without
speedup)!

```{toctree}
:caption: Get started
:maxdepth: 2

overview
install
backends
packaging
```

```{toctree}
:caption: Examples
:maxdepth: 2

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
```

## API Reference

Here is presented the organization of the package and the documentation of the
modules, classes and functions.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :caption: API Reference

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
```

```{toctree}
:caption: More
:maxdepth: 1

Transonic forge on Heptapod <https://foss.heptapod.net/fluiddyn/transonic>
Transonic in PyPI  <https://pypi.python.org/pypi/transonic/>
changes
roadmap
thanks
for_dev/CONTRIBUTING
Advice for FluidDyn developers <http://fluiddyn.readthedocs.io/en/latest/advice_developers.html>
for_dev
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
