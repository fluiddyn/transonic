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

"""

from pprint import pformat
import copy

import gast as ast
import beniget
from transonic.log import logger

from .util import (
    filter_code_typevars,
    get_annotations,
    print_dumped,
    print_unparsed,
    find_path,
    change_import_name,
    filter_external_code,
    get_exterior_code,
)
from .capturex import CaptureX
from .blocks_if import get_block_definitions
from .parser import parse_code
from . import extast

from transonic.config import backend_default

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


def get_decorated_dicts(module, ancestors, duc, pathfile: str, decorator="boost"):
    """Get the definitions of the decorated functions and classes"""

    kinds = ("functions", "functions_ext", "methods", "classes")
    backends = dict(pythran={}, cython={}, numba={})
    decorated_dicts = {kind: copy.deepcopy(backends) for kind in kinds}

    def add_definition(definition_node):
        backend = backend_default
        if isinstance(definition_node, ast.Call):
            # FIXME see other element than the first of the list
            if (
                definition_node.keywords
                and definition_node.keywords[0].arg == "backend"
            ):
                backend = str(extast.unparse(definition_node.keywords[0].value))
                backend = backend.replace("'", "").rstrip()
            definition_node = ancestors.parent(definition_node)
        decorated_dict = None
        if isinstance(definition_node, ast.Assign):
            if (
                definition_node.value.keywords
                and definition_node.value.keywords[0].arg == "backend"
            ):
                backend = str(
                    extast.unparse(definition_node.value.keywords[0].value)
                )
                backend = backend.replace("'", "").rstrip()
            key = definition_node.value.args[0].id
            definition_node, ext_module = find_decorated_function(
                module, key, pathfile
            )
            decorated_dict = decorated_dicts["functions"][backend]
            # if the definition node is in an imported module
            if ext_module:
                decorated_dict = decorated_dicts["functions_ext"][backend]
                decorated_dict[key] = (definition_node, ext_module)
        else:
            key = definition_node.name
        # If the definition node is not imported
        if decorated_dict is not decorated_dicts["functions_ext"][backend]:
            if isinstance(definition_node, ast.FunctionDef):
                parent = ancestors.parent(definition_node)
                if isinstance(parent, ast.ClassDef):

                    decorated_dict = decorated_dicts["methods"][backend]
                    key = (parent.name, key)
                else:
                    decorated_dict = decorated_dicts["functions"][backend]
            elif isinstance(definition_node, ast.ClassDef):
                decorated_dict = decorated_dicts["classes"][backend]
            if decorated_dict is not None:
                decorated_dict[key] = definition_node

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


def analyse_aot(code, pathfile):
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
    boosted_dicts = get_decorated_dicts(module, ancestors, duc, None)
    debug(pformat(boosted_dicts))

    debug("compute the annotations")

    from transonic import aheadoftime

    aheadoftime.is_transpiling = True

    def_nodes = [
        def_node
        for boosted_dict in boosted_dicts.values()
        for backend in boosted_dict.values()
        for def_node in backend.values()
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
        for backend, backends in boosted_dict.items():
            for key, definition in backends.items():
                ann = get_annotations(definition, namespace)
                if ann != {}:
                    annotations[kind][key] = get_annotations(
                        definition, namespace
                    )

    debug(pformat(annotations))

    debug("get_block_definitions")
    blocks = get_block_definitions(code, module, ancestors, duc, udc)

    info_analysis = {
        "ancestors": ancestors,
        "duc": duc,
        "udc": udc,
        "module": module,
        "def_nodes": def_nodes,
    }

    for block in blocks:
        block.parse_comments(namespace, info_analysis)

    debug(pformat(blocks))

    debug("compute code dependance")

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
    code_ext = {"function": {}, "classe": {}}
    code_dependance = capturex.make_code_external()
    # TODO implement class for new backends
    if boosted_dicts["functions"]["pythran"]:
        func = next(iter(boosted_dicts["functions"]["pythran"]))
        code_dependance, code_ext, _, _ = get_exterior_code(
            {func: code_dependance}, pathfile, classes="function", relative=True
        )
        code_dependance = code_dependance[func]
    if boosted_dicts["classes"]["pythran"]:
        cls = next(iter(boosted_dicts["classes"]["pythran"]))
        code_dependance, code_ext, _, _ = get_exterior_code(
            {cls: code_dependance}, pathfile, classes="classe", relative=True
        )
        code_dependance = code_dependance[cls]
    debug(code_dependance)
    debug("parse_code")
    signatures_p = parse_code(code)

    annotations["comments"] = {}

    for name_backend, backend in boosted_dicts["functions"].items():
        for name_func, fdef in backend.items():
            try:
                signatures = signatures_p[name_func]
            except KeyError:
                signatures = tuple()
            fdef = boosted_dicts["functions"][name_backend][name_func]
            arg_names = [arg.id for arg in fdef.args.args]
            annotations_sign = annotations["comments"][name_func] = []
            for sig in signatures:
                types = [
                    type_.strip()
                    for type_ in sig[len(fdef.name) + 1 : -1].split(",")
                ]
                annotations_sign.append(
                    {arg_name: type_ for arg_name, type_ in zip(arg_names, types)}
                )
    return boosted_dicts, code_dependance, annotations, blocks, code_ext
