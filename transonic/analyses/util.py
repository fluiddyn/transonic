from textwrap import dedent

import gast as ast
import astunparse


def print_dumped(source):
    if isinstance(source, str):
        module = ast.parse(source)
        if len(module.body) == 1:
            node = module.body[0]
        else:
            node = module
    else:
        node = source
    print(astunparse.dump(node))


def print_unparsed(node):
    print(astunparse.unparse(node))


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


def filter_code_typevars(module, duc, ancestors):

    module_filtered = ast.Module()
    kept = module_filtered.body = []
    suppressed = set()

    def fill_suppressed(def_):
        for user in def_.users():
            parent_in_body = ancestors.parents(user.node)[1]
            suppressed.add(parent_in_body)
            fill_suppressed(user)

    for node in module.body:
        if node in suppressed:
            continue

        if isinstance(node, ast.Import):
            if node.names[0].name in ["transonic", "numpy"]:
                kept.append(node)
            else:
                def_ = duc.chains[node.names[0]]
                fill_suppressed(def_)
            #     suppressed.add()
        elif isinstance(node, ast.ImportFrom):
            if node.module in ["transonic", "numpy"]:
                kept.append(node)

        elif isinstance(node, (ast.Assign, ast.AugAssign)):
            kept.append(node)

    return astunparse.unparse(module_filtered)


class AnalyseLines(ast.NodeVisitor):
    def __init__(self, main_node):
        if isinstance(main_node, ast.Module):
            self.line_start = 1
        else:
            self.line_start = main_node.lineno
        self.line_last = self.line_start
        self.visit(main_node)

    def generic_visit(self, node):
        if hasattr(node, "lineno"):
            if node.lineno > self.line_last:
                self.line_last = node.lineno
        super().generic_visit(node)

    def get_lines(self):
        return self.line_start, self.line_last

    def get_code(self, source):
        lines = source.split("\n")

        stop = self.line_last
        nb_lines = len(lines)
        if nb_lines != stop:
            # find next not empty and not comment line
            ind = stop - 1
            next_line = ""
            while ind + 1 < nb_lines and next_line == "":
                ind += 1
                next_line = lines[ind].strip()
                if next_line.startswith("#"):
                    next_line = ""

            if any(
                next_line.startswith(character) for character in (")", "]", "}")
            ):
                stop = ind + 1

        return "\n".join(lines[self.line_start - 1 : stop])


def gather_rawcode_comments(node, code_module):
    analysis = AnalyseLines(node)
    rawcode = dedent(analysis.get_code(code_module))
    comments = dedent(
        "\n".join(
            line for line in rawcode.split("\n") if line.strip().startswith("#")
        )
    )
    return rawcode, comments
