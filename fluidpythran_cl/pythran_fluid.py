"""Command line _pythran-fluid
==============================

Internal API
------------

.. autofunction:: main

"""

import subprocess
import sys
import logging
from pathlib import Path
import sysconfig

logger = logging.getLogger("pythran_fluid")
logger.setLevel(logging.INFO)

ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"


def main():
    """Minimal layer above the Pythran commandline"""

    assert sys.argv[0].endswith("_pythran-fluid")

    args = sys.argv[1:]

    path = Path.cwd() / args[0]
    logger.info(f"Pythranize {path}")

    if "-o" in args:
        index_output = args.index("-o") + 1
        name_out = args[index_output]
        name_out_base = name_out.split(".", 1)[0]
        name_tmp = name_out_base + ".tmp"
        args[index_output] = name_tmp

    args.insert(0, "pythran")
    subprocess.call(args)

    path_tmp = Path(name_tmp)
    if path_tmp.exists():
        path_out = path_tmp.with_suffix(ext_suffix)
        path_tmp.rename(path_out)
        logger.info(f"file {Path.cwd() / path_out.name} created")
    else:
        logger.error(
            f"file {Path.cwd() / path_tmp.name} has not been created by Pythran"
        )
