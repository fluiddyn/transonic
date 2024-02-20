import sys
from pathlib import PurePosixPath
from unittest.mock import patch

from transonic_cl.init_meson import main

cmd = "transonic-init-meson"


mypack = {
    "mypack": {
        "a.py": None,
        "b.py": None,
        "c.txt": None,
        "subpack0": {"d.py": None},
        "subpack1": {},
        "subpack2": {"subsubpack": {"e.py": None}},
    }
}


meson_files = {
    "mypack": """
python_sources = [
  'a.py',
  'b.py',
]

py.install_sources(
  python_sources,
  subdir: 'mypack'
)

subdir('subpack0')
subdir('subpack1')
subdir('subpack2')
""",
    "mypack/subpack0": """
python_sources = [
  'd.py',
]

py.install_sources(
  python_sources,
  subdir: 'mypack/subpack0'
)
""",
    "mypack/subpack2": """
subdir('subsubpack')
""",
    "mypack/subpack2/subsubpack": """
python_sources = [
  'e.py',
]

py.install_sources(
  python_sources,
  subdir: 'mypack/subpack2/subsubpack'
)
""",
}


def create_package(package: dict, path_dir):
    path_dir.mkdir(exist_ok=True)
    for key, value in package.items():
        if value is None:
            # it should be a file
            (path_dir / key).touch()
        else:
            assert isinstance(value, dict)
            create_package(value, path_dir / key)


def test_init_meson(tmp_path):
    path_mypack = tmp_path / "mypack"
    print(f"create package\n{path_mypack}")
    create_package(mypack, tmp_path)

    with patch("sys.argv", [cmd, str(path_mypack)]):
        main()

    meson_paths = sorted(path_mypack.rglob("meson.build"))
    assert len(meson_paths) == len(meson_files)

    for meson_path in meson_paths:
        code = (path_mypack / meson_path).read_text(encoding="utf-8")

        meson_path = PurePosixPath(meson_path.relative_to(path_mypack.parent))
        print(meson_path)
        code_should_be = meson_files[str(meson_path.parent)]

        if code != code_should_be:
            print(code_should_be)

        assert code == code_should_be
