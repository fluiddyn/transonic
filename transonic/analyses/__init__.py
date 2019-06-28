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
)
from .capturex import CaptureX
from .blocks_if import get_block_definitions
from .parser import parse_code
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


def get_decorated_dicts(module, ancestors, duc, pathfile: str, decorator="boost"):
    """Get the definitions of the decorated functions and classes"""

    kinds = ("functions", "functions_ext", "methods", "classes")
    decorated_dicts = {kind: {} for kind in kinds}

    def add_definition(definition_node):
        if isinstance(definition_node, ast.Call):
            definition_node = ancestors.parent(definition_node)
        decorated_dict = None
        if isinstance(definition_node, ast.Assign):
            key = definition_node.value.args[0].id
            definition_node, ext_module = find_decorated_function(
                module, key, pathfile
            )
            decorated_dict = decorated_dicts["functions"]
            # if the definition node is in an imported module
            if ext_module:
                # add this node and its module in decorated_dict["functions_ext"]
                decorated_dict = decorated_dicts["functions_ext"]
                decorated_dict[key] = (definition_node, ext_module)
        else:
            key = definition_node.name
        # If the definition node is not imported
        if decorated_dict is not decorated_dicts["functions_ext"]:
            if isinstance(definition_node, ast.FunctionDef):
                parent = ancestors.parent(definition_node)
                if isinstance(parent, ast.ClassDef):
                    decorated_dict = decorated_dicts["methods"]
                    key = (parent.name, key)
                else:
                    decorated_dict = decorated_dicts["functions"]
            elif isinstance(definition_node, ast.ClassDef):
                decorated_dict = decorated_dicts["classes"]
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
        for def_node in boosted_dict.values()
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

        for key, definition in boosted_dict.items():
            ann = get_annotations(definition, namespace)
            if ann != {}:
                annotations[kind][key] = get_annotations(definition, namespace)

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

    code_dependance = capturex.make_code_external()

    code_ext = {"function": {}, "classe": {}}

    def get_exterior_code(
        codes_dependance: dict, previous_file_name=None, classes: str = None
    ):
        """ Get all imported functions needed by boosted functions and methods at multiple levels,
            (i.e get functions needed by functions imported by boosted function) and add them into code_ext
        """
        for func, dep in codes_dependance.items():
            if dep:
                module_ext = extast.parse(dep)
                for node in module_ext.body:
                    if isinstance(node, (ast.ImportFrom, ast.Import)):
                        # get the path of the imported module
                        file_name, file_path = find_path(node, pathfile)
                        if file_name:
                            file_name = "__" + func + "__" + file_name
                            # get the content of the file
                            with open(str(file_path), "r") as file:
                                content = file.read()
                            mod = extast.parse(content)
                            # filter the code and add it to code_ext dict
                            code_ext[classes][file_name] = str(
                                filter_external_code(mod, node.names)
                            )
                            # change imported module names
                            codes_dependance[func] = change_import_name(
                                codes_dependance[func], node, func
                            )
                            # recursively get the exterior codes
                            if code_ext[classes][file_name]:
                                get_exterior_code(
                                    {func: code_ext[classes][file_name]},
                                    file_name,
                                    classes,
                                )
                                if previous_file_name:
                                    code_ext[classes][
                                        previous_file_name
                                    ] = change_import_name(
                                        code_ext[classes][previous_file_name],
                                        node,
                                        func,
                                    )
            return codes_dependance[func]

    if boosted_dicts["functions"]:
        func = next(iter(boosted_dicts["functions"]))
        code_dependance = get_exterior_code(
            {func: code_dependance}, classes="function"
        )
    if boosted_dicts["classes"]:
        cls = next(iter(boosted_dicts["classes"]))
        code_dependance = get_exterior_code(
            {cls: code_dependance}, classes="classe"
        )
    debug(code_dependance)
    debug("parse_code")
    signatures_p = parse_code(code)

    annotations["comments"] = {}

    for name_func, fdef in boosted_dicts["functions"].items():
        try:
            signatures = signatures_p[name_func]
        except KeyError:
            signatures = tuple()
        fdef = boosted_dicts["functions"][name_func]
        arg_names = [arg.id for arg in fdef.args.args]
        annotations_sign = annotations["comments"][name_func] = []
        for sig in signatures:
            types = [
                type_.strip() for type_ in sig[len(fdef.name) + 1 : -1].split(",")
            ]
            annotations_sign.append(
                {arg_name: type_ for arg_name, type_ in zip(arg_names, types)}
            )
    return boosted_dicts, code_dependance, annotations, blocks, code_ext
