"""
We want to check JAX import without failing.

Used in noxfile.py to avoid these kinds of failures:

  File "/builds/fluiddyn/transonic/.nox/test-with_pythran-1-with_cython-1/lib/python3.10/site-packages/jax/_src/lib/__init__.py", line 84, in <module>
    cpu_feature_guard.check_cpu_features()
RuntimeError: This version of jaxlib was built using AVX instructions, which your CPU and/or operating system do not support. You may be able work around this issue by building jaxlib from source.

"""

try:
    import jax.numpy
except (AttributeError, RuntimeError):
    print("jax NOT usable")
else:
    print("jax usable")
