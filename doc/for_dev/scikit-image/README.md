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

## What we need now

Pieces of code to create realistic input parameters for all boosted functions (for benchmarking):

- _colormixer.py (add, multiply, brightness, sigmoid_gamma, gamma,
  py_hsv_2_rgb, py_rgb_2_hsv, hsv_add, hsv_multiply)
- _convex_hull.py (possible_hull)
- _greyreconstruct.py (reconstruction_loop)
- _hessian_det_appx.py (_hessian_matrix_det)
- _moments_cy.py (moments_hu)
- _radon_transform.py (sart_projection_update)
- _unwrap_1d.py (unwrap_1d)
- brief_cy.py (_brief_loop)
- cmorph.py (_dilate, _erode)

## Next tasks

- fix <https://bitbucket.org/fluiddyn/transonic/issues/29/default-parameters>

- good solution to easily benchmark the different backends on these examples
  with nice representation of the results

- improve the Cython backend to get codes similar to the Cython files in
  scikit-image. If there are some differences, check how they influence the
  performances.

  * `cdivision=True`
  * `nonecheck=False`
