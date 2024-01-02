# How to contribute to Transonic

Thank you for considering contributing to Transonic. Transonic is a
community-driven project. It's people like you that make Transonic useful and
successful. There are many ways to contribute, from writing tutorials or
examples, improvements to the documentation, submitting bug reports and feature
requests, or even writing code which can be incorporated into Transonic for
everyone to use. (Paragraph shamelessly taken and adapted from the MetPy
project!)

## Reporting Issues

When opening an issue to report a problem
(<https://foss.heptapod.net/fluiddyn/transonic/issues>), please try to provide
a minimal code example that reproduces the issue along with details of the
system you are using. You can copy-paste the output of the command `fluidinfo
-v` provided by the Python package
[fluiddyn](https://pypi.org/project/fluiddyn/) ([Github
gists](https://gist.github.com/) are good for that!).

## Development process

Transonic is part of the wider project FluidDyn. For FluidDyn, we use the
revision control software Mercurial and our main repositories are hosted here:
<https://foss.heptapod.net/fluiddyn>.

Please read our documentation on [developer
essentials](https://fluiddyn.readthedocs.io/en/latest/advice_developers.html),
and especially on [setting up
Mercurial](https://fluiddyn.readthedocs.io/en/latest/mercurial_heptapod.html).

## Setup a development environment and use it

We use [PDM](https://pdm-project.org) so the first step is to [install this
tool](https://pdm-project.org/latest/#installation). Then, in the root
directory of the repository, you can create and activate a local virtual environment with:

```sh
pdm install
source .venv/bin/activate
```

There is a Makefile with few useful commands. For example, one can run some tests with

```sh
make tests_python
make tests_pythran
```

To build the documentation:

```sh
cd doc
make cleanall
make
```

## Release

For now, we push on PyPI manually:

```sh
hg pull
hg up default
hg tag 0.5.3
hg push
pdm publish
```
