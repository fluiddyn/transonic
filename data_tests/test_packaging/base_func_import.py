from transonic import jit
# from .base import identity
# FIXME: The above import works but creating an alias does not
from .base import identity as base_identity


identity_jit = jit(native=True)(base_identity)
