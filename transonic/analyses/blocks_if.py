"""Analyses for "if blocks"
===========================

"""

import gast as ast

from transonic.analyses import extast
from transonic.analyses.util import gather_rawcode_comments
from transonic.analyses.capturex import CaptureX


class BlockDefinition:
    """Represent a block definition"""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.__dict__.update(**kwargs)

    def __repr__(self):
        return repr(self.kwargs)

    def parse_comments(self, namespace=None, info_analysis=None):
        self.signatures = get_signatures_from_comments(
            self.comments, namespace, info_analysis
        )


def get_block_definitions(code, module, ancestors, duc, udc):
    """Get all "if" block definitions"""
    blocks = []
    node_transonic_obj = None
    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.module == "transonic":
            for alias in node.names:
                if alias.name == "Transonic":
                    Transonic_node = alias
                    node_transonic_obj = None
                    for user in duc.chains[Transonic_node].users():
                        parent = ancestors.parent(user.node)
                        if isinstance(parent, ast.Call):
                            grandparent = ancestors.parent(parent)
                            if len(grandparent.targets) != 1:
                                continue
                            node_transonic_obj = grandparent.targets[0]
                    if node_transonic_obj is not None:
                        break

    if node_transonic_obj is None:
        return blocks

    def_ = duc.chains[node_transonic_obj]
    nodes_using_ts = [user.node for user in def_.users()]

    for user in def_.users():
        for user1 in user.users():
            if isinstance(user1.node, ast.Attribute):
                attribute = user1.node
                if attribute.attr == "is_transpiled":
                    parent = ancestors.parent(attribute)
                    if isinstance(parent, ast.If):
                        # it could be the begining of a block
                        if_node = parent
                        if len(parent.body) != 1:
                            # no it's not a block definition
                            continue
                        node = parent.body[0]
                        call = node.value
                        if isinstance(node, ast.Expr):
                            results = []
                        elif isinstance(node, ast.Assign):
                            results = [target.id for target in node.targets]
                        else:
                            # no it's not a block definition
                            continue

                        attribute = call.func
                        ts_node = attribute.value
                        if (
                            ts_node not in nodes_using_ts
                            or attribute.attr != "use_block"
                        ):
                            # no it's not a block definition
                            continue

                        try:
                            # gast >= 0.3.0 (py3.8)
                            name_block = call.args[0].value
                        except AttributeError:
                            name_block = call.args[0].s

                        rawcode, comments = gather_rawcode_comments(if_node, code)

                        # if we are here, it's a block definition
                        blocks.append(
                            BlockDefinition(
                                name=name_block,
                                results=results,
                                ast_code=if_node.orelse,
                                comments=comments,
                                rawcode=rawcode,
                            )
                        )

    return blocks


def find_index_closing_parenthesis(string: str):
    """Find the index of the closing parenthesis"""
    assert string.startswith("("), "string has to start with '('"
    stack = []
    for index, letter in enumerate(string):
        if letter == "(":
            stack.append(letter)
        elif letter == ")":
            stack.pop()
            if not stack:
                return index

    raise SyntaxError(f"Transonic syntax error for string {string}")


def find_last_def_node(variable, module):
    for node in module.body[::-1]:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if target.id == variable:
                    return node
    raise RuntimeError


def find_def_code(
    variables: set, def_nodes: list, module: dict, ancestors, udc, duc
):

    nodes_def_vars = [
        find_last_def_node(variable, module) for variable in variables
    ]
    nodes_def_vars.sort(key=lambda x: x.lineno)

    capturex = CaptureX(
        list(nodes_def_vars) + def_nodes,
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


def create_objects_from_names(names, def_nodes, module, ancestors, udc, duc):
    """create a namespace for the variables defined at the module level"""
    code_def_var = find_def_code(names, def_nodes, module, ancestors, udc, duc,)
    namespace = {}
    exec(code_def_var, namespace)
    return namespace


def get_signatures_from_comments(
    comments, namespace_from_code=None, info_analysis=None
):
    """Get the blocks signatures for a block"""
    if namespace_from_code is None:
        namespace_from_code = {}

    comments = comments.replace("#", "").replace("\n", "")

    signatures_tmp = [
        sig.split("->", 1)[0].strip()
        for sig in comments.split("transonic block")[1:]
    ]

    signatures = []
    for sig in signatures_tmp:
        if sig.startswith("("):
            sig = sig[1 : find_index_closing_parenthesis(sig)]
        signatures.append(sig)

    types_NameError = set()
    signatures_tmp = signatures
    signatures = []
    for sig_str in signatures_tmp:
        sig_dict = {}
        type_vars_strs = [tmp.strip() for tmp in sig_str.split(";")]
        type_vars_strs = [tmp for tmp in type_vars_strs if tmp]

        for type_vars_str in type_vars_strs:
            type_, vars_str = type_vars_str.strip().split(" ", 1)
            if type_ in namespace_from_code:
                type_ = namespace_from_code[type_]
            else:
                try:
                    type_ = eval(type_)
                except NameError:
                    types_NameError.add(type_)
                except (SyntaxError, TypeError):
                    pass
            for var_str in vars_str.split(","):
                var_str = var_str.strip()
                sig_dict[var_str] = type_
        signatures.append(sig_dict)

    if types_NameError:
        # create a namespace for the variables defined at the module level
        namespace = create_objects_from_names(
            types_NameError,
            info_analysis["def_nodes"],
            info_analysis["module"],
            info_analysis["ancestors"],
            info_analysis["udc"],
            info_analysis["duc"],
        )

        for signature in signatures:
            for var_str, type_ in signature.items():
                if type_ in types_NameError:
                    signature[var_str] = namespace[type_]

    return signatures
