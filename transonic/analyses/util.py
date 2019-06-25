"""Utilities for the analyses
=============================

"""
import beniget
from pathlib import Path
from textwrap import dedent
import gast as ast
from transonic.analyses import extast
from transonic.analyses.capturex import CaptureX
import astunparse


def print_dumped(source):
    """Pretty print the AST"""
    if isinstance(source, str):
        module = extast.parse(source)
        if len(module.body) == 1:
            node = module.body[0]
        else:
            node = module
    else:
        node = source
    print(astunparse.dump(node))


def print_unparsed(node):
    """Print the code corresponding to a tree or a node"""
    print(extast.unparse(node))


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
    """Create the annotations from a definition node"""

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

    source = extast.unparse(ast_annotations)

    try:
        del namespace["__builtins__"]
    except KeyError:
        pass
    exec(source, namespace)
    return namespace["annotations"]


def filter_code_typevars(module, duc, ancestors):
    """Create a filtered code with what is needed to create the annotations"""

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

    return extast.unparse(module_filtered)


class AnalyseLines(ast.NodeVisitor):
    """Analyse to find the last line of a node"""

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
    """Get the comments in a node"""
    analysis = AnalyseLines(node)
    rawcode = dedent(analysis.get_code(code_module))
    comments = dedent(
        "\n".join(
            line for line in rawcode.split("\n") if line.strip().startswith("#")
        )
    )
    return rawcode, comments


packages_supported_by_pythran = ["numpy", "math", "functools", "cmath"]
# FIXME find path in non local imports
def find_path(node: object, pathfile: str):
    """ Return the path of node (instance of ast.Import or ast.ImportFrom)
    """
    name = str()
    path = str()

    if isinstance(node, ast.ImportFrom):
        name = node.module
        if name in packages_supported_by_pythran:
            return None, None
        else:
            parent = parent = Path(pathfile).parent
            path = parent / Path(str(name.replace(".", "/")) + ".py")

    else:
        # TODO complete the list
        if node.names[0].name in packages_supported_by_pythran:
            pass
        else:
            # TODO deal with an ast.Import
            raise NotImplementedError
    return name, path


def change_import_name(
    code_dep: str, changed_node: object, func_name: str, cls: str = None
):
    """ Change the name of changed_node in code_dep by adding "__"+func+"__" 
        at the beginning of the imported module, and return the modified code
    """
    mod = extast.parse(code_dep)
    for node in mod.body:
        if extast.unparse(node) == extast.unparse(changed_node):
            if isinstance(node, ast.ImportFrom):
                node.module = "__" + func_name + "__" + node.module
            elif isinstance(node, ast.Import):
                node.names[0].name = "__" + func_name + "__" + node.names[0].name
        if cls:
            node.level = 0
    return extast.unparse(mod)


def filter_external_code(module: object, names: list):
    """ Filter the module to keep only the necessary nodes 
        needed by functions or class in the parameter names
    """
    code_dependance_annotations = ""
    lines_code = []
    for node in module.body:
        for name in names:
            if isinstance(node, ast.FunctionDef):
                if node.name == extast.unparse(name).rstrip("\n\r"):
                    ancestors = beniget.Ancestors()
                    ancestors.visit(module)
                    duc = beniget.DefUseChains()
                    duc.visit(module)
                    udc = beniget.UseDefChains(duc)
                    capturex = CaptureX(
                        [node],
                        module,
                        ancestors,
                        defuse_chains=duc,
                        usedef_chains=udc,
                        consider_annotations=None,
                    )
                    lines_code.append(str(extast.unparse(node)))
                    code_dependance_annotations = capturex.make_code_external()
            if isinstance(node, ast.Assign):
                if node.targets[0].id == extast.unparse(name).rstrip("\n\r"):
                    lines_code.append(str(extast.unparse(node)))
            if isinstance(node, ast.ClassDef):
                if node.name == extast.unparse(name).rstrip("\n\r"):
                    print_dumped(node)
                    lines_code.append(str(extast.unparse(node)))

    return code_dependance_annotations + "\n".join(lines_code)
