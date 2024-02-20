import argparse
import sys

from pathlib import Path, PurePosixPath


template = """
python_sources = [
{sources}
]

py.install_sources(
  python_sources,
  subdir: '{subdir}'
)
"""


def process_directory(path_dir, path_pack=None):

    if path_pack is None:
        path_pack = path_dir
        print(f"Process {path_dir}")
        subdir=path_pack.name
    else:
        subdir=PurePosixPath(path_dir.relative_to(path_pack.parent))
        print(f"Process subdir {subdir}")

    names_py = sorted(path.name for path in path_dir.glob("*.py"))
    print(f"{names_py = }")
    paths_subdirs = [
        path
        for path in path_dir.glob("*")
        if path.is_dir() and not path.name.startswith("__")
    ]

    names_subdirs = sorted(path.name for path in paths_subdirs)
    print(f"{names_subdirs = }")

    if names_py:
        code = template.format(
            sources="\n".join(f"  '{name}'," for name in names_py),
            subdir=subdir,
        )
    else:
        code = ""

    if names_subdirs:
        code += (
            "\n" + "\n".join(f"subdir('{name}')" for name in names_subdirs) + "\n"
        )

    if not code:
        return

    with open(path_dir / "meson.build", "w", encoding="utf-8") as file:
        file.write(code)

    for path_subdir in paths_subdirs:
        process_directory(path_subdir, path_pack)


def main():

    parser = argparse.ArgumentParser(
        prog="transonic-init-meson",
        description="Create Meson files from a Python package",
    )
    parser.add_argument("path", help="Path package.")

    args = parser.parse_args()

    path_pack = Path(args.path)

    if not path_pack.is_dir():
        print("Path given is not a directory", file=sys.stderr)
        sys.exit(1)

    process_directory(path_pack)

