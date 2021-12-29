from transonic import jit
from . import base


identity_jit = jit(native=True)(base.identity)
