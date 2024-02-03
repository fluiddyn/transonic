import pytest

from transonic_cl.get_includes import main


class MyException(Exception):
    pass


def test_get_include(monkeypatch):
    monkeypatch.setattr("sys.argv", ["transonic-get-include", "numpy"])
    main()

    def _exit(exit_code):
        if exit_code == 1:
            raise MyException

    monkeypatch.setattr("sys.exit", _exit)
    monkeypatch.setattr("sys.argv", ["transonic-get-include", "numpyyyy"])

    with pytest.raises(MyException):
        main()
