from transonic import util
from transonic.util import query_yes_no, timeit


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
