"""Command line fluidpythran
============================

Internal API
------------

.. autofunction:: run

.. autofunction:: parse_args

"""

import argparse
from pathlib import Path
from glob import glob

from . import __version__
from .transpiler import make_pythran_files
from .log import logger, set_log_level

doc = """
fluidpythran: easily speedup your Python code with Pythran

"""


def run():
    """Run the fluidpythran commandline

    See :code:`fluidpythran -h`
    """
    args = parse_args()

    if args.version:
        print(__version__)
        return

    if args.verbose is None:
        set_log_level("info")
    elif args.verbose > 0:
        set_log_level("debug")
        logger.debug(args)

    path = args.path

    if isinstance(path, list) and len(path) == 1:
        path = path[0]

    if isinstance(path, list):
        paths = path
    else:
        path = Path(path)
        if path.is_file():
            paths = (path,)
        elif path.is_dir():
            paths = path.glob("*.py")
        else:
            paths = glob(str(path))

    make_pythran_files(paths, force=args.force)


def parse_args():
    """Parse the arguments"""
    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", help="Path file or directory.", nargs="*")

    parser.add_argument(
        "-f",
        "--force",
        help="write the file even if it is up-to-date",
        action="store_true",
    )

    parser.add_argument(
        "-V", "--version", help="print version and exit", action="store_true"
    )

    parser.add_argument("-v", "--verbose", help="verbose mode", action="count")

    return parser.parse_args()
