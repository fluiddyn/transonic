
from runpy import run_module

import numpy as np

inp = np.ones(2)


def check(module_name, should_return=None):
    mod = run_module(module_name)
    trans = mod["Transmitter"](1.)
    assert trans.__call__.__doc__ == "My docstring", trans.__call__.__doc__
    assert trans.__call__.__name__ == "__call__"

    result = trans(inp)

    if should_return is not None:
        assert np.allclose(result, should_return)

    return result


original = check("transmitter")
check("try0", original)
check("try1", original)
check("try2", original)
check("try3", original)
