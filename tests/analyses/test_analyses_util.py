import sys

import pytest

from transonic.analyses.extast import parse
from transonic.analyses.util import print_dumped, print_unparsed

source = "def func(): return True"


def test_print_dumped():

    if sys.version_info > (3, 13, 3):
        pytest.xfail("bug gast 0.6.0 for Python >= 3.13.4 (but should work)")
        # see https://github.com/serge-sans-paille/gast/issues/95

    print_dumped(source)


def test_print_unparsed():
    node = parse(source)
    print_unparsed(node)
