# Transonic documentation

```{include} ../README.md
---
start-after: <!-- start short description -->
end-before: <!-- end short description -->
---
```

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

[cupy]: https://cupy.chainer.org/
[cython]: https://cython.org/
[jax]: https://github.com/google/jax
[numba]: https://numba.pydata.org/
[pyccel]: https://github.com/pyccel/pyccel
[pythran]: https://github.com/serge-sans-paille/pythran
[pytorch]: https://pytorch.org/
[weld]: https://github.com/weld-project/weld
