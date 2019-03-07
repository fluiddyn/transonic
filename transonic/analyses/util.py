import gast as ast
import astunparse


def print_ast(code):
    module = ast.parse(code)
    print(astunparse.dump(module))
    return module


def print_dump(node):
    print(astunparse.dump(node))


def _fill_ast_annotations_function(function_def, ast_annotations):

    dict_node = ast_annotations.value
    for arg in function_def.args.args:
        if arg.annotation is not None:
            try:
                name = arg.arg
            except AttributeError:
                name = arg.id

            dict_node.keys.append(ast.Str(s=name))
            dict_node.values.append(arg.annotation)


def _fill_ast_annotations_class(class_def, ast_annotations):

    dict_node = ast_annotations.value
    for node in class_def.body:
        if not isinstance(node, ast.AnnAssign):
            continue

        if node.annotation is not None:
            name = node.target.id
            dict_node.keys.append(ast.Str(s=name))
            dict_node.values.append(node.annotation)


def get_annotations(object_def, namespace):

    # print_dump(object_def)

    ast_annotations = ast.Assign(
        targets=[ast.Name(id="annotations", ctx=ast.Store(), annotation=None)],
        value=ast.Dict(keys=[], values=[]),
    )

    if isinstance(object_def, ast.FunctionDef):
        _fill_ast_annotations_function(object_def, ast_annotations)
    elif isinstance(object_def, ast.ClassDef):
        _fill_ast_annotations_class(object_def, ast_annotations)
    else:
        raise NotImplementedError

    # print_dump(ast_annotations)

    source = astunparse.unparse(ast_annotations)

    try:
        del namespace["__builtins__"]
    except KeyError:
        pass
    exec(source, namespace)
    return namespace["annotations"]
