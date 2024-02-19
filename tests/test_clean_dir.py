from unittest.mock import patch

from transonic.backends import backends

from transonic.clean_dir import main

cmd = "transonic-clean-dir"


names = [backend for backend in backends]


def test_clean_dir(tmp_path):

    subpack_foo = tmp_path / "foo"
    subpack_bar = subpack_foo / "bar"

    subpack_bar.mkdir(parents=True)

    for subpack in (subpack_foo, subpack_bar):
        for name in names:
            (subpack / f"__{name}__").mkdir()

    with patch("sys.argv", [cmd, "-h"]):
        try:
            main()
        except SystemExit as system_exit:
            assert system_exit.code == 0
        else:
            raise RuntimeError("Issue with -h")

    with patch("sys.argv", [cmd, str(tmp_path / "does_not_exist")]):
        try:
            main()
        except SystemExit as system_exit:
            assert system_exit.code == 1
        else:
            raise RuntimeError("Issue with not is_dir()")

    with patch("sys.argv", [cmd, str(tmp_path)]):
        main()

    for subpack in (subpack_foo, subpack_bar):
        assert subpack.exists()
        for name in names:
            assert not (subpack / f"__{name}__").exists()
