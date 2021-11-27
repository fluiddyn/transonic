from transonic.analyses.extast import parse
from transonic.analyses.util import print_dumped, print_unparsed

source = "def func(): return True"


def test_print_dumped():
    print_dumped(source)


def test_print_unparsed():
    node = parse(source)
    print_unparsed(node)
