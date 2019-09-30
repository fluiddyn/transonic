# Scikit-image kernels

See

- an issue on using Pythran in scikit-image:
  https://github.com/scikit-image/scikit-image/issues/2956

- a PR by Serge with Pythran kernels:
  https://github.com/scikit-image/scikit-image/pull/3226

- The corresponding Cython files are in the scikit-image repository, for example:

  - skimage/io/_plugins/_colormixer.pyx
  - ...

## Next tasks

- fix https://bitbucket.org/fluiddyn/transonic/issues/29/default-parameters

- good solution to easily benchmark the different backends on these examples
  with nice presentation of the results

- improve Cython backend to get correct results and compare with Cython code in
  scikit-image
