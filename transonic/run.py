"""Command line transonic
============================

Internal API
------------

.. autofunction:: run

.. autofunction:: parse_args

"""

import argparse
from pathlib import Path
from glob import glob
import sys

from . import __version__
from .transpiler import make_backend_files
from .log import logger
from .pythranizer import compile_extensions, ext_suffix
from .util import has_to_build, clear_cached_extensions
from .compat import fspath

try:
    import pythran
except ImportError:
    pythran = False


doc = """
transonic: easily speedup your Python code with Pythran

"""


def run():
    """Run the transonic commandline

    See :code:`transonic -h`
    """
    args = parse_args()

    if args.version:
        print(__version__)
        return

    if not args.path and not args.clear_cache:
        logger.warning("No python files given. Nothing to do! ✨ 🍰 ✨.")
        return

    if args.clear_cache:
        clear_cached_extensions(args.clear_cache, force=args.force)
        return

    if args.verbose is None:
        logger.set_level(None)
    elif args.verbose == 1:
        logger.set_level("info")
    elif args.verbose > 1:
        logger.set_level("debug")
    logger.info(args)

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
            paths = glob(fspath(path))

    if not paths:
        logger.error(f"No input file found (args.path = {args.path})")
        sys.exit(1)

    make_backend_files(paths, force=args.force)

    if not pythran or args.no_pythran:
        return

    # find pythran files not already compiled
    pythran_paths = []
    for path in paths:
        path = Path(path)
        pythran_path = path.parent / "__pythran__" / path.name
        ext_path = pythran_path.with_suffix(ext_suffix)
        if pythran_path.exists() and has_to_build(ext_path, pythran_path):
            pythran_paths.append(pythran_path)

    compile_extensions(
        pythran_paths, args.pythran_flags, parallel=True, force=args.force
    )


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

    parser.add_argument(
        "-np",
        "--no-pythran",
        help="do not compile the Pythran files with Pythran",
        action="store_true",
    )

    parser.add_argument(
        "-pf",
        "--pythran-flags",
        help=(
            "Flags sent to Pythran. "
            'Default is "-march=native -DUSE_XSIMD". '
            "There has to be atleast one space in the passed string! "
            'Example: transonic toto.py -pf "-march=native "\n'
        ),
        type=str,
        default="",
    )

    parser.add_argument(
        "-cc",
        "--clear-cache",
        help=("Clear the cached extensions for a module"),
        type=str,
        # default="",
    )

    return parser.parse_args()


if __name__ == "__main__":
    run()
