# Make your Python code fly at *transonic* speeds!

[![Latest version](https://badge.fury.io/py/transonic.svg)](https://pypi.python.org/pypi/transonic/)
[![Code coverage](https://codecov.io/gh/fluiddyn/transonic/branch/branch%2Fdefault/graph/badge.svg)](https://codecov.io/gh/fluiddyn/transonic)
[![Documentation status](https://readthedocs.org/projects/transonic/badge/?version=latest)](http://transonic.readthedocs.org)
![Supported Python versions](https://img.shields.io/pypi/pyversions/transonic.svg)
[![Heptapod CI](https://foss.heptapod.net/fluiddyn/transonic/badges/branch/default/pipeline.svg)](https://foss.heptapod.net/fluiddyn/transonic/-/pipelines)
[![mybinder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/fluiddyn/transonic/branch/default?urlpath=lab/tree/doc/ipynb/executed)
[![sonarcloud](https://sonarcloud.io/api/project_badges/measure?project=fluiddyn_transonic&metric=alert_status)](https://sonarcloud.io/dashboard?id=fluiddyn_transonic)

<!-- [![Github Actions](https://github.com/fluiddyn/transonic/actions/workflows/ci.yml/badge.svg?branch=branch/default)](https://github.com/fluiddyn/transonic/actions) -->

**Documentation**: <https://transonic.readthedocs.io>

Transonic is a pure Python package (requiring Python >= 3.9) to easily
accelerate modern Python-Numpy code with different accelerators (currently
[Cython](https://cython.org/), [Pythran](https://github.com/serge-sans-paille/pythran) and [Numba](https://numba.pydata.org/), but potentially later [Cupy](https://cupy.chainer.org/), [PyTorch](https://pytorch.org/), [JAX](https://github.com/google/jax), [Weld](https://www.weld.rs/), [Pyccel](https://github.com/pyccel/pyccel), [Uarray](https://github.com/Quansight-Labs/uarray), etc...).

**The accelerators are not hard dependencies of Transonic:** Python codes using
Transonic run fine without any accelerators installed (of course without
speedup)!

> [!WARNING]
> Transonic is still in an active development stage (see our
> [roadmap](https://transonic.readthedocs.io/en/latest/roadmap.html)).
> Remarks and suggestions are very welcome.
>
> However, Transonic is now really usable, useful and used "in production" in
> [FluidSim](https://foss.heptapod.net/fluiddyn/fluidsim) and
> [FluidFFT](https://foss.heptapod.net/fluiddyn/fluidfft) (see examples for
> [blocks](https://foss.heptapod.net/fluiddyn/fluidsim/src/default/fluidsim/base/time_stepping/pseudo_spect.py) and
> [@boost](https://foss.heptapod.net/fluiddyn/fluidfft/src/default/fluidfft/fft3d/operators.py)).

## The long-term project

> [!NOTE]
> The context of the creation of Transonic is presented in these documents:
>
> - [Transonic Vision](https://fluiddyn.netlify.app/transonic-vision.html)
> - [Make your numerical Python code fly at transonic speed (EuroScipy 2019)](http://www.legi.grenoble-inp.fr/people/Pierre.Augier/docs/ipynbslides/20190904-euroscipy-transonic/pres.slides.html#/),
> - [Overview of the Python HPC landscape and zoom on Transonic](http://www.legi.grenoble-inp.fr/people/Pierre.Augier/docs/ipynbslides/20190319_PySciDataGre_transonic/pres_20190319_PySciDataGre_transonic.slides.html).

Transonic targets Python end-users and library developers.

It is based on the following principles:

- We'd like to write scientific / computing applications / libraries with
  pythonic, readable, modern code (Python >= 3.6).

- In some cases, Python-Numpy is too slow. However, there are tools to
  accelerate such Python-Numpy code which lead to very good performances!

- Let's try to write universal code which express what we want to compute and
  not the special hacks we want to use to make it fast. We just need nice ways
  to express that a function, a method or a block of code has to be accelerated
  (and how it has to be accelerated). We'd like to be able to do this in a
  pythonic way, with decorators and context managers.

- There are many tools to accelerate Python-Numpy code! Let's avoid writting
  code specialized for only one of these tools.

- Let's try to keep the code as it would be written without acceleration. For
  example, with Transonic, we are able to accelerate (simple) methods of
  classes even though some accelerators don't support classes.

- Let's accelerate/compile only what needs to be accelerated, i.e. only the
  bottlenecks. Python and its interpreters are good for the rest. In most
  cases, the benefice of writting big compiled extensions (with Cython or in
  other languages) is negligible.

- Adding types is sometimes necessary. In modern Python, we have nice syntaxes
  for type annotations! Let's use them.

- Ahead-of-time (AOT) and just-in-time (JIT) compilation modes are both useful.
  We'd like to have a nice, simple and unified API for these two modes.

  - AOT is useful to be able to distribute compiled packages and in some cases,
    more optimizations can be applied.
  - JIT is simpler to use (no need for type annotations) and optimizations can
    be more hardware specific.

  Note that with Transonic, AOT compilers (Pythran and Cython) can be used as
  JIT compilers (with a cache mechanism).

To summarize, a **strategy to quickly develop a very efficient scientific
application/library** with Python could be:

1. Use modern Python coding, standard Numpy/Scipy for the computations and all
   the cool libraries you want.
2. Profile your applications on real cases, detect the bottlenecks and apply
   standard optimizations with Numpy.
3. Add few lines of Transonic to compile the hot spots.

## What we have now

We start to have a good API to accelerate Python-Numpy code (functions, methods
and blocks of code). The default Transonic backend uses Pythran and works well.
[Here, we explain why Pythran is so great for Python users and why Transonic is
great for Pythran users](https://transonic.readthedocs.io/en/latest/backends/pythran.html). There are
also (more experimental) backends for Cython and Numba.

> [!NOTE]
> Transonic can be used in libraries and applications using MPI (as
> [FluidSim](https://foss.heptapod.net/fluiddyn/fluidsim)).

## Installation and configuration

```bash
pip install transonic
```

Transonic is sensible to environment variables:

- `TRANSONIC_DIR` can be set to control where the cached files are
  saved.
- `TRANSONIC_DEBUG` triggers a verbose mode.
- `TRANSONIC_COMPILE_AT_IMPORT` can be set to enable a mode for which
  Transonic compiles at import time the Pythran file associated with the
  imported module. This behavior can also be triggered programmatically
  by using the function `set_compile_at_import`.
- `TRANSONIC_NO_REPLACE` can be set to disable all code replacements.
  This is useful to compare execution times and when measuring code coverage.
- `TRANSONIC_COMPILE_JIT` can be set to false to disable the
  compilation of jited functions. This can be useful for unittests.
- `TRANSONIC_BACKEND` to choose between the supported backends. The
  default backend "pythran" is quite robust. There are now 3 other backends:
  "cython", "numba" and "python" (prototypes).
- `TRANSONIC_MPI_TIMEOUT` sets the MPI timeout (default to 5 s).

## License

Transonic is distributed under the BSD License.
