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

logger = logging.getLogger("pythran_fluid")
logger.setLevel(logging.INFO)

ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def main():
    """Minimal layer above the Pythran commandline"""

    assert sys.argv[0].endswith("transonic_cl/run_pythran.py")

    args = sys.argv[1:]

    name = args[0]
    path = Path.cwd() / name
    print(f"Pythranizing {path}")

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
        # the compilation should be
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

    args.insert(0, "pythran")
    name_lock.touch()
    try:
        subprocess.call(args)
    except Exception:
        pass
    finally:
        name_lock.unlink()

    if "-o" in args and path_tmp.exists():
        path_tmp.rename(path_out)

    if path_out.exists():
        print(f"Done! File {path_out.absolute()} created")
    else:
        logger.error(
            f"Error! File {path_out.absolute()} has not been created by Pythran"
        )


if __name__ == "__main__":
    main()
