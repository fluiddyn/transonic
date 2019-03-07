import ast
import astunparse


def print_ast(code):
    module = ast.parse(code)
    print(astunparse.dump(module))
    return module


def dump(node):
    print(astunparse.dump(node))


code = """

type_ = float

def myfunc(a: int, b: type_):
    pass

"""

module = ast.parse(code)

fdef = module.body[1]

new_ast = ast.Assign(
    targets=[ast.Name(id="annotations", ctx=ast.Store())],
    value=ast.Dict(keys=[], values=[]),
)

dict_node = new_ast.value

for arg in fdef.args.args:
    name = arg.arg
    dict_node.keys.append(ast.Str(s=name))
    dict_node.values.append(arg.annotation)

print(astunparse.unparse(new_ast))
