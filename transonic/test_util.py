from transonic import util
from transonic.util import query_yes_no


def test_query_yes_no():

    util.input = lambda: "y"

    query_yes_no("test", default="y")
    query_yes_no("test", default="n")
    query_yes_no("test")

    util.input = lambda: ""
    query_yes_no("test", default="y")

    query_yes_no("test", force=True)
