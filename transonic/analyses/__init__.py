from pprint import pformat

import gast as ast
import beniget

from .util import filter_code_typevars, get_annotations
from .capturex import CaptureX, make_code_external
from .blocks_if import get_block_definitions

from ..log import logger

def compute_ancestors_chains(module_node):

    ancestors = beniget.Ancestors()
    ancestors.visit(module_node)

    duc = beniget.DefUseChains()
    duc.visit(module_node)

    udc = beniget.UseDefChains(duc)

    return ancestors, duc, udc


def get_boosted_dicts(module, ancestors, duc):

    kinds = ("functions", "methods", "classes")
    boosted_dicts = {kind: {} for kind in kinds}

    def add_definition(definition_node):
        boosted_dict = None
        key = definition_node.name
        if isinstance(definition_node, ast.FunctionDef):
            parent = ancestors.parent(definition_node)
            if isinstance(parent, ast.ClassDef):
                boosted_dict = boosted_dicts["methods"]
                key = (parent.name, key)
            else:
                boosted_dict = boosted_dicts["functions"]
        elif isinstance(definition_node, ast.ClassDef):
            boosted_dict = boosted_dicts["classes"]
        if boosted_dict is not None:
            boosted_dict[key] = definition_node

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
                                and user1.node.attr == "boost"
                            ):
                                definition_node = ancestors.parent(user1.node)
                                add_definition(definition_node)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "transonic":
                for alias in node.names:
                    if alias.name == "boost":
                        boost_def_node = alias
                        boost_def = duc.chains[boost_def_node]
                        for user in boost_def.users():
                            definition_node = ancestors.parent(user.node)
                            add_definition(definition_node)

    return boosted_dicts


def analyse_aot(code):

    debug = logger.debug

    debug("ast.parse")
    module = ast.parse(code)

    debug("compute ancestors and chains")
    ancestors, duc, udc = compute_ancestors_chains(module)

    debug("filter_code_typevars")
    code_dependance_annotations = filter_code_typevars(module, duc, ancestors)
    debug(code_dependance_annotations)

    debug("find boosted objects")
    boosted_dicts = get_boosted_dicts(module, ancestors, duc)
    debug(pformat(boosted_dicts))

    debug("compute code dependance")

    def_nodes = [
        def_node
        for boosted_dict in boosted_dicts.values()
        for def_node in boosted_dict.values()
    ]

    # remove the decorator (boost) to compute the code dependance
    for def_node in def_nodes:
        def_node.decorator_list = []

    capturex = CaptureX(
        def_nodes,
        module,
        ancestors=ancestors,
        defuse_chains=duc,
        usedef_chains=udc,
        consider_annotations=False,
    )

    code_dependance = make_code_external(capturex.external)
    debug(code_dependance)

    debug("compute the annotations")
    namespace = {}
    exec(code_dependance_annotations, namespace)

    annotations = {}

    for kind, boosted_dict in boosted_dicts.items():
        annotations[kind] = {}

        for key, definition in boosted_dict.items():
            annotations[kind][key] = get_annotations(definition, namespace)

    debug(pformat(annotations))

    debug("get_block_definitions")
    blocks = get_block_definitions(code, module, ancestors, duc, udc)

    for block in blocks:
        block.parse_comments(namespace)

    debug(pformat(blocks))

    return boosted_dicts, code_dependance, annotations, blocks