from transonic import util
from transonic.util import query_yes_no, timeit, print_versions, timeit_verbose


def test_query_yes_no():
    util.input = lambda: "y"

    query_yes_no("test", default="y")
    query_yes_no("test", default="n")
    query_yes_no("test")

    util.input = lambda: ""
    query_yes_no("test", default="y")

    query_yes_no("test", force=True)


def test_timeit():
    a = 1
    b = 2
    timeit("a + b", total_duration=0.001, globals=locals())


def test_timeit_verbose():
    a = 1
    b = 2
    norm = timeit_verbose("a + b", total_duration=0.001, globals=locals())
    timeit_verbose("a + b", total_duration=0.001, globals=locals(), norm=norm)


def test_print_versions():
    print_versions()
