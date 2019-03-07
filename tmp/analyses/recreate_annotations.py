import gast as ast

from transonic.analyses.util import get_annotations

code = """

type_ = float

def myfunc(a: int, b: type_):
    pass

"""

module = ast.parse(code)
fdef = module.body[1]

print(get_annotations(fdef, {"type_": float}))