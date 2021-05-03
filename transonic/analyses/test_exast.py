import ast

from .extast import parse, unparse


def test_ExtSlice():
    code = "foo[:, b]"
    code_back = unparse(parse(code)).strip()
    assert code_back == code

    code_back = unparse(ast.parse(code)).strip()
    assert code_back == code


def test_comment():
    code = "# a comment"
    code_back = unparse(parse(code)).strip()
    assert code_back == code

