"""Utilities to replace strings by objects
==========================================

"""

import gast as ast

from transonic.analyses import extast
from transonic.analyses.capturex import CaptureX


def find_last_def_node(variable, module):
    for node in module.body[::-1]:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if target.id == variable:
                    return node
    raise RuntimeError


def find_def_code(variables: set, module: dict, ancestors, udc, duc):
    nodes_def_vars = [
        find_last_def_node(variable, module) for variable in variables
    ]
    nodes_def_vars.sort(key=lambda x: x.lineno)

    capturex = CaptureX(
        list(nodes_def_vars),
        module,
        ancestors,
        defuse_chains=duc,
        usedef_chains=udc,
    )

    lines_ext = []
    for node in capturex.external:
        lines_ext.append(extast.unparse(node).strip())

    for node in nodes_def_vars:
        line = extast.unparse(node).strip()
        if line not in lines_ext:
            lines_ext.append(line)

    return "\n".join(lines_ext)


def create_objects_from_names(names, module, ancestors, udc, duc):
    """create a namespace for the variables defined at the module level"""
    code_def_var = find_def_code(
        names,
        module,
        ancestors,
        udc,
        duc,
    )
    namespace = {}
    exec(code_def_var, namespace)
    return namespace


def replace_strings_by_objects(signatures: dict, module, ancestors, udc, duc):
    """Replace strings in signatures by objects defined in the code"""

    types_NameError = set()
    for signature in signatures:
        for var_str, type_as_str in signature.items():
            try:
                signature[var_str] = eval(type_as_str)
            except NameError:
                types_NameError.add(type_as_str)
            except (SyntaxError, TypeError):
                pass

    namespace = create_objects_from_names(
        types_NameError, module, ancestors, udc, duc
    )

    for signature in signatures:
        for var_str, type_as_str in signature.items():
            if type_as_str in types_NameError:
                signature[var_str] = namespace[type_as_str]
