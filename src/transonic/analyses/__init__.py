"""Code analyses
================

.. autosummary::
   :toctree:

    blocks_if
    capturex
    extast
    justintime
    parser
    util
    objects_from_str

"""

import re
from pprint import pformat

import gast as ast
from transonic.analyses import beniget

from transonic.log import logger

from .util import (
    filter_code_typevars,
    get_annotations,
    print_dumped,
    print_unparsed,
    find_path,
    get_exterior_code,
    extract_variable_annotations,
    extract_returns_annotation,
)
from .capturex import CaptureX
from .blocks_if import get_block_definitions
from .parser import parse_transonic_def_commands
from .objects_from_str import replace_strings_by_objects
from . import extast


__all__ = ["print_dumped", "print_unparsed"]


def compute_ancestors_chains(module_node):
    """Create Beniget objects"""

    ancestors = beniget.Ancestors()
    ancestors.visit(module_node)

    duc = beniget.DefUseChains()
    duc.visit(module_node)

    udc = beniget.UseDefChains(duc)

    return ancestors, duc, udc


def find_decorated_function(module, function_name: str, pathfile: str = None):
    ext_module = False
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == function_name:
                return node, ext_module
        # look for function_name in the imports of module
        if isinstance(node, ast.ImportFrom):
            for func in node.names:
                if func.name == function_name:
                    # find and read the imported module file
                    name, path = find_path(node, pathfile)
                    with open(path) as file:
                        ext_module = extast.parse(file.read())
                    # find the definition of function_name in the imported module
                    node, _ = find_decorated_function(ext_module, function_name)
                    return node, ext_module
    raise RuntimeError


def get_decorated_dicts(
    module, ancestors, duc, pathfile: str, backend_name, decorator="boost"
):
    """Get the definitions of the decorated functions and classes"""

    kinds = ("functions", "functions_ext", "methods", "classes")

    backend_names = ("pythran", "cython", "numba", "python")
    decorated_dicts = {
        kind: {name: {} for name in backend_names} for kind in kinds
    }

    def add_definition(node_using_decorator):
        """

        NotImplemented:

        decor = boost(inline=1)

        isinstance(node_using_decorator, ast.Call)
        isinstance(node_parent, ast.Assign)
        node_parent.value.keywords

        """

        backend_name_def = backend_name
        decorated_dict = None
        ext_module = False
        node_parent = ancestors.parent(node_using_decorator)

        # first, get the keywords
        keywords = None
        if isinstance(node_using_decorator, ast.Call):
            # decorator used in the form boost(...)
            if node_using_decorator.keywords:
                # decorator used in the form boost(key=value)
                keywords = {
                    keyword.arg: eval(extast.unparse(keyword.value))
                    for keyword in node_using_decorator.keywords
                }
                backend_name_def = keywords.get("backend", backend_name)

        if isinstance(
            node_using_decorator, (ast.FunctionDef, ast.ClassDef)
        ) and isinstance(node_parent, (ast.Module, ast.ClassDef)):
            """case

            @boost
            def f():
                ...

            """
            definition_node = node_using_decorator

        elif isinstance(node_using_decorator, ast.Call) and isinstance(
            node_parent, (ast.FunctionDef, ast.ClassDef)
        ):
            """
            @boost(inline=1)
            def f():
                pass
            """

            definition_node = node_parent

        elif isinstance(node_using_decorator, ast.Call) and isinstance(
            node_parent, ast.Assign
        ):
            """
            f1_ = boost(f1)
            or
            decor = boost(foo=True)
            """

            call = node_using_decorator
            if call.keywords:
                "decor = boost(foo=True)"
                raise NotImplementedError
            else:
                "f1_ = boost(f1)"
                if len(call.args) > 1:
                    raise NotImplementedError
                func_name = call.args[0].id

                definition_node, ext_module = find_decorated_function(
                    module, func_name, pathfile
                )

        elif isinstance(node_using_decorator, ast.Call) and isinstance(
            node_parent, ast.Call
        ):
            """f1_ = boost(inline=1)(f1)"""

            call = node_parent
            if call.keywords or len(call.args) > 1:
                raise NotImplementedError

            call_arg = call.args[0]
            if isinstance(call_arg, ast.Attribute):
                func_name = call_arg.attr
            else:
                func_name = call_arg.id

            definition_node, ext_module = find_decorated_function(
                module, func_name, pathfile
            )

        else:
            raise NotImplementedError

        if keywords is not None:
            definition_node._transonic_keywords = keywords

        # if the definition node is in an imported module
        if ext_module:
            decorated_dict = decorated_dicts["functions_ext"][backend_name_def]
            decorated_dict[func_name] = (definition_node, ext_module)
        # If the definition node is not imported
        else:
            func_name = definition_node.name
            if isinstance(definition_node, ast.FunctionDef):
                parent = ancestors.parent(definition_node)
                if isinstance(parent, ast.ClassDef):
                    decorated_dict = decorated_dicts["methods"][backend_name_def]
                    func_name = (parent.name, func_name)
                else:
                    decorated_dict = decorated_dicts["functions"][
                        backend_name_def
                    ]
            elif isinstance(definition_node, ast.ClassDef):
                decorated_dict = decorated_dicts["classes"][backend_name_def]
            else:
                raise RuntimeError
            if decorated_dict is not None:
                decorated_dict[func_name] = definition_node

    # we first need to find the node where transonic.boost is defined...
    for node in module.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "transonic":
                    transonic_def_node = alias
                    transonic_def = duc.chains[transonic_def_node]
                    for user in transonic_def.users():
                        for user1 in user.users():
                            if (
                                isinstance(user1.node, ast.Attribute)
                                and user1.node.attr == decorator
                            ):
                                definition_node = ancestors.parent(user1.node)
                                add_definition(definition_node)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "transonic":
                for alias in node.names:
                    if alias.name == decorator:
                        boost_def_node = alias
                        boost_def = duc.chains[boost_def_node]
                        for user in boost_def.users():
                            definition_node = ancestors.parent(user.node)
                            add_definition(definition_node)

    return decorated_dicts


def get_types_from_transonic_signature(signature: str, function_name: str):
    types = []
    tmp = signature[len(function_name) + 1 : -1]

    while tmp:
        try:
            index_comma = tmp.index(",")
        except ValueError:
            tmp = tmp.strip()
            if tmp:
                types.append(tmp)
            break

        try:
            index_open_bracket = tmp.index("[")
        except ValueError:
            index_open_bracket = None

        if index_open_bracket is None or index_comma < index_open_bracket:
            type_, tmp = tmp.split(",", 1)

        else:
            index_close_bracket = tmp.index("]")
            # cover int[][] and int[:, :] but could be buggy!
            type0 = tmp[:index_close_bracket]
            type1, tmp = tmp[index_close_bracket:].split(",", 1)

            type_ = type0 + type1

        types.append(type_.strip())

    return types


def analyse_aot(code, pathfile, backend_name):
    """Gather the informations for ``@boost`` and blocks"""
    debug = logger.debug

    debug("extast.parse")
    module = extast.parse(code)

    debug("compute ancestors and chains")
    ancestors, duc, udc = compute_ancestors_chains(module)

    debug("filter_code_typevars")
    code_dependance_annotations = filter_code_typevars(module, duc, ancestors)
    debug(code_dependance_annotations)

    debug("find boosted objects")
    boosted_dicts = get_decorated_dicts(
        module, ancestors, duc, None, backend_name
    )
    debug(pformat(boosted_dicts))

    debug("compute the annotations")

    from transonic import aheadoftime

    aheadoftime.is_transpiling = True

    def_nodes = [
        def_node
        for boosted_dict in boosted_dicts.values()
        for boosted_dict_backend in boosted_dict.values()
        for def_node in boosted_dict_backend.values()
    ]

    capturex = CaptureX(
        def_nodes,
        module,
        ancestors,
        defuse_chains=duc,
        usedef_chains=udc,
        consider_annotations="only",
    )

    code_dependance_annotations = capturex.make_code_external()

    namespace = {}
    exec(code_dependance_annotations, namespace)

    aheadoftime.is_transpiling = False

    annotations = {}

    for kind, boosted_dict in boosted_dicts.items():
        annotations[kind] = {}
        for boosted_dict_backend in boosted_dict.values():
            for key, definition in boosted_dict_backend.items():
                ann = get_annotations(definition, namespace)
                if ann != {}:
                    annotations[kind][key] = ann

    debug(pformat(annotations))

    debug("get_block_definitions")
    blocks = get_block_definitions(code, module, ancestors, duc, udc)

    for block in blocks:
        replace_strings_by_objects(block.signatures, module, ancestors, udc, duc)

    debug(pformat(blocks))

    debug("compute code dependance:")

    # remove the decorator (boost) to compute the code dependance
    # + do not consider the class annotations
    for def_node in def_nodes:
        def_node.decorator_list = []
        if isinstance(def_node, ast.ClassDef):
            def_node.body = [
                node
                for node in def_node.body
                if not isinstance(node, ast.AnnAssign)
            ]

    blocks_for_capturex = [block.ast_code for block in blocks]

    capturex = CaptureX(
        def_nodes,
        module,
        ancestors=ancestors,
        defuse_chains=duc,
        usedef_chains=udc,
        consider_annotations=False,
        blocks=blocks_for_capturex,
    )
    code_ext = {"function": {}, "class": {}}
    code_dependance = capturex.make_code_external()
    # TODO implement class for new backends + debug this code :-)
    if boosted_dicts["functions"]["pythran"]:
        func = next(iter(boosted_dicts["functions"]["pythran"]))
        code_dependance, code_ext, _, _ = get_exterior_code(
            {func: code_dependance}, pathfile, classes="function", relative=True
        )
        code_dependance = code_dependance[func]
    if boosted_dicts["classes"]["pythran"]:
        cls = next(iter(boosted_dicts["classes"]["pythran"]))
        code_dependance, code_ext, _, _ = get_exterior_code(
            {cls: code_dependance}, pathfile, classes="class", relative=True
        )
        code_dependance = code_dependance[cls]
    debug(code_dependance)

    debug("parse_transonic_def_commands")
    signatures_p = parse_transonic_def_commands(code)

    annotations["__in_comments__"] = {}
    annotations["__locals__"] = {}
    annotations["__returns__"] = {}

    # match a comma except if inside backets (for `float[:,:]`)
    pattern = re.compile(r",\s*(?![^[]*\])")

    for functions_backend in boosted_dicts["functions"].values():
        for name_func, fdef in functions_backend.items():
            try:
                signatures = signatures_p[name_func]
            except KeyError:
                signatures = tuple()
            arg_names = [arg.id for arg in fdef.args.args]
            annotations_sign = []
            for sig in signatures:
                types = [
                    type_.strip()
                    for type_ in re.split(pattern, sig[len(fdef.name) + 1 : -1])
                ]
                annotations_sign.append(dict(zip(arg_names, types)))
            if annotations_sign:
                annotations["__in_comments__"][name_func] = annotations_sign

            # locals: variable annotations
            annotations_locals = extract_variable_annotations(fdef, namespace)
            if annotations_locals:
                annotations["__locals__"][name_func] = annotations_locals

            if fdef.returns:
                annotations["__returns__"][
                    name_func
                ] = extract_returns_annotation(fdef.returns, namespace)

    for signatures in annotations["__in_comments__"].values():
        replace_strings_by_objects(signatures, module, ancestors, udc, duc)

    debug("annotations:\n" + pformat(annotations))

    return boosted_dicts, code_dependance, annotations, blocks, code_ext
