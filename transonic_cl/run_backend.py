"""Command line
===============

Internal API
------------

.. autofunction:: main

"""

import subprocess
import sys
import logging
from pathlib import Path
import sysconfig
from time import time, sleep
import os

logger = logging.getLogger("pythran_fluid")
logger.setLevel(logging.INFO)

ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def main():
    """Minimal layer above the Pythran commandline"""

    if "-b" in sys.argv:
        if sys.argv[sys.argv.index("-b") + 1]:
            index = sys.argv.index("-b")
            backend = sys.argv[index + 1]
            del sys.argv[index]
            del sys.argv[index]
        else:
            raise ValueError("No backend is specified afert -b")
    else:
        raise ValueError("No backend is specified")

    compiling_name = backend.capitalize() + "izing"

    assert sys.argv[0].endswith(
        os.path.sep.join(("transonic_cl", "run_backend.py"))
    )

    args = sys.argv[1:]
    print(args)
    name = args[0]
    path = Path.cwd() / name

    if "-o" in args:
        index_output = args.index("-o") + 1
        name_out = args[index_output]
    else:
        name_out = Path(name).with_suffix(ext_suffix).name

    name_out_base = name_out.split(".", 1)[0]

    if "-o" in args:
        name_tmp = name_out_base + ".tmp"
        args[index_output] = name_tmp
        path_tmp = Path(name_tmp)
        path_out = path_tmp.with_suffix(ext_suffix)
    else:
        path_out = Path(name_out)

    name_lock = Path(name_out_base + ".lock")

    if name_lock.exists():
        print(
            f"lock file {name_lock.absolute()} present: "
            "waiting for completion of the compilation",
            flush=True,
        )
        time_out_lock = 3600  # (s) let's hope it's enough
        time_start = time()
        while name_lock.exists() and time() - time_start < time_out_lock:
            sleep(1)
        if time() - time_start >= time_out_lock:
            logger.error(f"Remove lock file {name_lock.absolute()}")
            name_lock.unlink()
            raise TimeoutError(
                f"Stop waiting for a lock file to be deleted {name_lock.absolute()}"
            )

        assert not name_lock.exists()
        sleep(1)
        if not path_out.exists():
            raise RuntimeError(
                f"After lock file were deleted, {path_out.absolute()} not created"
            )

        return

    if "-v" in args:
        # no capture_output
        stdout = stderr = None
    else:
        stdout = stderr = subprocess.PIPE

    print(f"{compiling_name} {path}", flush=True)
    if backend == "pythran":
        args.insert(0, "pythran")
    elif backend == "cython":
        args = ["cythonize", "-i", "-3", str(path)]
    name_lock.touch()
    try:
        completed_process = subprocess.run(
            args, stdout=stdout, stderr=stderr, universal_newlines=True
        )
    except Exception:
        pass
    finally:
        name_lock.unlink()

    if "-o" in args and path_tmp.exists():
        path_tmp.rename(path_out)

    if path_out.exists():
        print(f"File {path_out.absolute()} created by {backend}")
    else:
        logger.error(
            f"Error! File {path_out.absolute()} has not been created by {backend}"
        )
        try:
            completed_process
        except NameError:
            pass
        else:
            if completed_process.stdout:
                print(
                    f"{backend.capitalize()} stdout:\n{completed_process.stdout}"
                )
            if completed_process.stderr:
                logger.error(
                    f"{backend.capitalize()}stderr:\n{completed_process.stderr}"
                )


if __name__ == "__main__":
    main()
