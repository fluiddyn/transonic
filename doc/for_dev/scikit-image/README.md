# Scikit-image kernels

See

- an issue on using Pythran in scikit-image:
  https://github.com/scikit-image/scikit-image/issues/2956

- a PR by Serge with Pythran kernels:
  https://github.com/scikit-image/scikit-image/pull/3226

- The corresponding Cython files (taken from the scikit-image repository) are
  in the `cython` directory:

  - skimage/io/_plugins/_colormixer.pyx
  - skimage/morphology/_convex_hull.pyx
  - skimage/morphology/_greyreconstruct.pyx
  - skimage/feature/_hessian_det_appx.pyx
  - skimage/measure/_moments_cy.pyx
  - skimage/transform/_radon_transform.pyx
  - skimage/restoration/_unwrap_1d.pyx
  - skimage/feature/brief_cy.pyx
  - skimage/morphology/cmorph.pyx

## Compile and run the benchmarks

```
make clean_all
make
# or CXX=clang++-6.0 CC=clang-6.0 make
python bench.py
```

Note: clang (or recent versions of GCC?) can give much better results than
gcc<=6.3.0. To compile Pythran files with clang: `CXX=clang++-6.0 CC=clang-6.0
python setup.py`.

Running `python3 -m pyperf system tune` before the benchmarks could also help
to get better stability.


## What we need now

Pieces of code to create realistic input parameters for all boosted functions
(for benchmarking, see the directory `setup_codes`):

- [ ] _colormixer.py
  - [ ] add
  - [ ] multiply
  - [ ] brightness
  - [ ] sigmoid_gamma
  - [ ] gamma
  - [ ] py_hsv_2_rgb
  - [ ] py_rgb_2_hsv
  - [ ] hsv_add
  - [ ] hsv_multiply

- [ ] _convex_hull.py (possible_hull)
- [x] _greyreconstruct.py (reconstruction_loop)
- [ ] _hessian_det_appx.py (_hessian_matrix_det)
- [ ] _moments_cy.py (moments_hu)
- [ ] _radon_transform.py (sart_projection_update)
- [ ] _unwrap_1d.py (unwrap_1d)
- [ ] brief_cy.py (_brief_loop)
- [ ] cmorph.py
  - [x] _dilate
  - [ ] _erode

## Next tasks

- [x] Fix <https://foss.heptapod.net/fluiddyn/transonic/issues/29>

- Good solution to easily benchmark the different backends on these examples
  with nice representation of the results

- Improve the Cython backend to get codes similar to the Cython files in
  scikit-image. If there are some differences, check how they influence the performances.

  Low hanging fruits:

  - [x] `cdivision=True` and `nonecheck=False`
  - [x] negative_indices in `np.ndarray[dtype=np.uint32_t, ndim=1, negative_indices=False, mode='c']`
  - [x] `void` type

  And more complicated things!

  - [ ] `with nogil:` (for example for _convex_hull.py)
  - [ ] `from libc.math cimport exp, pow` (how?)
  - [ ] casting: `<np.uint8_t> op_result`, which in Cython is different from
    `np.uint8(op_result)` :-(
  - [ ] `cdef void foo(int[:] a) nogil:` (bugs Cython)

  Questions:

  - Do we have to support C array creation (`cdef cnp.uint8_t lut[256]` or
    `cdef float HSV[3]`)? Is it *really* more efficient than standard Numpy
    array?

  - Would it be ok to have all function defined with `cpdef` ?

## About the Transonic code

- [ ] _colormixer.py

  It is a difficult case, with advanced Cython code (`with nogil:`, `cdef`, C
  arrays, `<cnp.int16_t>`, `from libc.math cimport exp, pow`).

  - [ ] add
  - [ ] multiply
  - [ ] brightness
  - [ ] sigmoid_gamma
  - [ ] gamma
  - [ ] py_hsv_2_rgb
  - [ ] py_rgb_2_hsv
  - [ ] hsv_add
  - [ ] hsv_multiply

- [x] _convex_hull.py (possible_hull)

  Done (`cython -a` white) except one (important) `with nogil:`.

- [x] _greyreconstruct.py (reconstruction_loop)

  Done (`cython -a` white) except one (important) `with nogil:`. The 3
  Transonic backends produce codes faster than the old .pyx (for Cython, it
  should be related to the missing `with nogil:`).

- [ ] _hessian_det_appx.py (_hessian_matrix_det)

  Not an easy one (`cdef ... nogil`, `with nogil`).

- [x] _moments_cy.py (moments_hu)

  This one is easy!

- [ ] _radon_transform.py (sart_projection_update)

  Needs cast, `with nogil` and `from libc.math cimport ...`.

- [ ] _unwrap_1d.py (unwrap_1d)

  Needs cast and `from libc.math cimport ...`.

- [ ] brief_cy.py (_brief_loop)

  Needs `with nogil`.

- [x] cmorph.py
  - [x] _dilate
  - [x] _erode

  `from libc.stdlib cimport malloc, free` is used in the .pyx file! Thus the
  Transonic code and the generated Cython code is simpler (using `np.empty`).

  The generated Cython seems to be ~10% slower but the generated Pythran is
  faster than the .pyx from skimage.
