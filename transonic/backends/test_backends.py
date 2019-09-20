from transonic.config import backend_default

from transonic.justintime import modules_backends


def test_set_backend_for_this_module():
    from .for_test_set_backend import ts, func

    assert ts.backend.name == "python"
    assert func() == 0

    module_name = "transonic.backends.for_test_set_backend"

    assert module_name in modules_backends["python"]

    if backend_default == "python":
        return

    assert module_name not in modules_backends[backend_default]
