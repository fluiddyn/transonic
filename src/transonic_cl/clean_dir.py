import argparse
import sys
from pathlib import Path
from shutil import rmtree

from transonic.backends import backends

cmd = "transonic-clean-dir"


names = set(f"__{backend}__" for backend in backends)


def clean_dir(path_dir):
    """Delete backend files from a directory (recursive)"""
    subdirs_all = sorted(path for path in path_dir.glob("*") if path.is_dir())
    subdirs = []
    for subdir in subdirs_all:
        if subdir.name in names:
            rmtree(subdir, ignore_errors=True)
            continue
        subdirs.append(subdir)
    for subdir in subdirs:
        clean_dir(subdir)


def main():

    parser = argparse.ArgumentParser(
        prog="transonic-clean-dir",
        description="Delete files related to Transonic in a directory",
    )
    parser.add_argument("path", help="Path directory.")

    args = parser.parse_args()

    path_dir = Path(args.path)

    if not path_dir.is_dir():
        print("Path given is not a directory", file=sys.stderr)
        sys.exit(1)

    clean_dir(path_dir)
