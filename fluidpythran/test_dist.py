from . import dist

from .dist import detect_pythran_extensions, modification_date
from . import path_data_tests

dist.can_import_pythran = True


def test_detect_pythran_extensions():

    detect_pythran_extensions(path_data_tests)


def test_modification_date():

    modification_date(path_data_tests / "no_pythran.py")
