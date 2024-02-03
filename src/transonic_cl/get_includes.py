import argparse
import sys
from pathlib import Path

from importlib import import_module


def main():
    parser = argparse.ArgumentParser(
        prog="transonic-get-include",
        description="Get include directory for packages",
    )

    parser.add_argument("package", type=str, help="Package name")

    args = parser.parse_args()

    try:
        mod = import_module(args.package)
    except ImportError:
        print("ImportError")
        sys.exit(1)

    try:
        path_include = Path(mod.get_include())
    except AttributeError:
        print(f"No {args.package}.get_include")
        sys.exit(1)

    try:
        path_include = path_include.relative_to(Path.cwd())
    except ValueError:
        pass

    print(path_include)
