# Packaging when using Transonic

We still support Setuptools (examples
[here](https://foss.heptapod.net/fluiddyn/transonic/-/tree/branch/default/doc/examples/packages))
but we now recommend using the [Meson] build system as in
[one of our test package](https://foss.heptapod.net/fluiddyn/transonic/-/tree/branch/default/data_tests/package_for_test_meson).
For a clean and quite simple real case (also using [PDM] and [Nox]), see what is
done for the package [Fluidsim](https://foss.heptapod.net/fluiddyn/fluidsim)
(related documentation
[here](https://fluidsim.readthedocs.io/en/latest/build-from-source.html)).

[Meson] is a high quality open source build system used in particular for Scipy
and Scikit-image. The data necessary to build the package is staggered in
`meson.build` files in the different directories of the packages.

- There is also a file `meson.options` describing few specific build options
  ([this file in Fluidsim](https://foss.heptapod.net/fluiddyn/fluidsim/-/blob/branch/default/meson.options)).

- In the main `meson.build` file, few variables related to Transonic and Pythran
  are defined
  ([this file in Fluidsim](https://foss.heptapod.net/fluiddyn/fluidsim/-/blob/branch/default/meson.build)).

- In other `meson.build` files, we can add
  [a call to Transonic](https://foss.heptapod.net/fluiddyn/fluidsim/-/blob/branch/default/fluidsim/operators/meson.build)
  to automatically create backends directories with their `meson.build` file.

Note that Transonic can use for this step more that one backend with something
like

```sh
transonic --meson --backend python,pythran,numba operators2d.py operators3d.py
```

so that one can then choose one of these backend at runtime.

[meson]: https://mesonbuild.com
[nox]: https://nox.thea.codes
[pdm]: https://pdm-project.org
