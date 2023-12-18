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

from transonic import __version__

from transonic.compiler import wait_for_all_extensions, scheduler

from .backends import backends
from transonic.config import backend_default
from transonic.log import logger
from transonic.util import (
    has_to_build,
    clear_cached_extensions,
    can_import_accelerator,
)

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
        clear_cached_extensions(args.clear_cache, args.force, args.backend)
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
            paths = glob(str(path))

    if not paths:
        logger.error(f"No input file found (args.path = {args.path})")
        sys.exit(1)

    backend = backends[args.backend]
    paths_out = backend.make_backend_files(paths, force=args.force)

    if args.meson:
        # TODO: create the necessary meson.build files
        with open(path.parent / str(f"__{backend.name}__") / "meson.build", "w") as f:
            f.writelines(
                [
                    "backend = get_option('deps_backend')\n",
                    "if backend == 'pythran'\n",
                    "  pythran = find_program('pythran', native: true)\n",
                    "  run_command(\n",
                    "    ['pythran', '-E', 'pseudo_spect.py'],\n"
                    "  )\n",
                    "  _pseudo_spect = library(\n",
                    "    'pseudo_spect',\n",
                    "    'pseudo_spect.cpp',\n", # TODO dynamic
                    "    include_directories: incdir_pythran\n",
                    "  )\n",
                    "  _pseudo_spect_pythran = py3.extension_module(\n",
                    "    'pseudo_spect',\n",
                    "    _pseudo_spect,\n",
                    "    subdir: 'fluidsim/base/time_stepping/__pythran__',\n",  # TODO: dynamic
                    "  )\n",
                    "endif\n"
                ]
            )

    if args.no_compile:
        return

    if not can_import_accelerator(backend.name):
        logger.warning(
            f"Since {backend.name_capitalized} is not importable, "
            "Transonic cannot properly compile a file."
        )
        return

    # find pythran files not already compiled
    backends_paths = []

    for path in paths:
        path = Path(path)
        backend_path = path.parent / str(f"__{backend.name}__") / path.name
        ext_path = backend_path.with_name(
            backend.name_ext_from_path_backend(backend_path)
        )
        if backend_path.exists() and has_to_build(ext_path, backend_path):
            backends_paths.append(backend_path)

    with scheduler.progress:
        backend.compile_extensions(
            backends_paths,
            str_accelerator_flags=args.accelerator_flags,
            parallel=True,
            force=args.force,
        )

        if not args.no_blocking:
            wait_for_all_extensions()


def parse_args():
    """Parse the arguments"""
    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", help="Path file or directory.", nargs="*")

    parser.add_argument(
        "-f",
        "--force",
        help="proceed even if the files seem up-to-date",
        action="store_true",
    )

    parser.add_argument(
        "-V", "--version", help="print version and exit", action="store_true"
    )

    parser.add_argument("-v", "--verbose", help="verbose mode", action="count")

    parser.add_argument(
        "-b",
        "--backend",
        help=("Backend (pythran, cython, numba or python)"),
        type=str,
        default=backend_default,
    )

    parser.add_argument(
        "-nc",
        "--no-compile",
        help="do not compile the Pythran/Cython/... files",
        action="store_true",
    )

    parser.add_argument(
        "-nb",
        "--no-blocking",
        help="launch the compilation in the background and return",
        action="store_true",
    )

    parser.add_argument(
        "-pf",
        "--pythran-flags",
        help=("Depreciated: use -af"),
        type=str,
        default="",
    )

    parser.add_argument(
        "-af",
        "--accelerator-flags",
        help=(
            "Flags sent to the accelerator. "
            'Default is "". '
            "There has to be atleast one space in the passed string! "
            "Examples:\n"
            '`transonic foo.py -af "-march=native "` or\n'
            '`transonic foo.py -af "-march=native -DUSE_XSIMD -Ofast"`\n'
        ),
        type=str,
        default="",
    )

    parser.add_argument(
        "-cc",
        "--clear-cache",
        help=("clear the cached extensions for a module"),
        type=str,
        # default="",
    )

    parser.add_argument(
        "--meson",
        help="Only prepare the backend directory for Meson",
        action="store_true",
    )

    args = parser.parse_args()
    if args.pythran_flags != "":
        raise DeprecationWarning("-pf is deprecated. Use -af instead!")

    if args.meson:
        args.no_compile = True

    return args


if __name__ == "__main__":
    run()
