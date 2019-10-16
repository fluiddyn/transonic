from subprocess import getoutput
from pathlib import Path

from transonic.util import timeit

statements = {
    ("cmorph", "_dilate"): "_dilate(image, selem, out, shift_x, shift_y)",
    (
        "_greyreconstruct",
        "reconstruction_loop",
    ): "reconstruction_loop(ranks, prev, next_, strides, current_idx, image_stride)",
}

import_from_skimage = {
    (
        "_greyreconstruct",
        "reconstruction_loop",
    ): "from skimage.morphology._greyreconstruct import reconstruction_loop"
}


def bench_one(name_module="cmorph", func=None, total_duration=2):

    if func is not None:
        raise NotImplementedError

    functions = [
        (mod, func_) for (mod, func_) in statements.keys() if mod == name_module
    ]

    if not functions:
        raise ValueError(f"bad name_module: {name_module}")

    name_function = functions[0][1]

    print(f"module: {name_module}")
    stmt = statements[(name_module, name_function)]
    print(stmt)

    path_setup = Path("setup_codes") / f"{name_module}_{name_function}.py"

    if not path_setup.exists():
        raise RuntimeError

    with open(path_setup) as file:
        setup = file.read()

    if (name_module, name_function) in import_from_skimage:
        setup_from_skimage = setup.replace(
            f"from future.{name_module} import {name_function}",
            import_from_skimage[(name_module, name_function)],
        )
        time = timeit(stmt, setup_from_skimage, total_duration=total_duration)
        print(f"{'from skimage':18s} {time:.2e} s")

    setup_pyx = setup.replace(
        f"from future.{name_module} import", f"from pyx.{name_module} import"
    )

    code = f"""
from transonic.util import timeit
setup = '''{setup}'''
stmt = '''{stmt}'''
print(timeit(stmt, setup, total_duration={total_duration}))
    """

    time_old = timeit(stmt, setup_pyx, total_duration=total_duration)

    print(f"cython pyx skimage {time_old:.2e} s  (= norm)")

    with open("tmp.py", "w") as file:
        file.write(code)

    for backend in ("cython", "pythran", "numba"):
        time = float(getoutput(f"TRANSONIC_BACKEND='{backend}' python tmp.py"))
        print(f"{backend:18s} {time:.2e} s  (= {time/time_old:.2f} * norm)")

    # print(getoutput("TRANSONIC_NO_REPLACE=1 python tmp.py"))

    if (name_module, name_function) not in import_from_skimage:
        return

    setup_from_skimage = setup.replace(
        f"from future.{name_module} import {name_function}",
        import_from_skimage[(name_module, name_function)],
    )
    time = timeit(stmt, setup_from_skimage, total_duration=total_duration)

    print(f"{'from skimage':18s} {time:.2e} s  (= {time/time_old:.2f} * norm)")
