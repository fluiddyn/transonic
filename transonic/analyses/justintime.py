"""Analyses for ``@jit``
========================

"""
import gast as ast

from transonic.log import logger

from transonic.analyses import extast
from transonic.analyses import compute_ancestors_chains, get_decorated_dicts
from transonic.analyses.capturex import CaptureX

from transonic.analyses.util import print_dumped
from .util import (
    find_path,
    change_import_name,
    filter_external_code,
    get_exterior_code,
)


def analysis_jit(code, pathfile):
    """Gather the informations for ``@jit`` with an ast analysis"""
    debug = logger.debug

    debug("extast.parse")
    module = extast.parse(code)

    debug("compute ancestors and chains")
    ancestors, duc, udc = compute_ancestors_chains(module)

    # boosted_dicts = get_boosted_dicts(module, ancestors, duc)

    jitted_dicts = get_decorated_dicts(
        module, ancestors, duc, pathfile, decorator="jit"
    )

    debug("compute code dependance")

    def_nodes_dict = {
        key: def_node
        for kind in ["functions"]
        for key, def_node in jitted_dicts[kind].items()
    }

    codes_dependance = {}

    # get code dependance for a decorated function from a imported module
    for func_name, (func_node, imported_module) in jitted_dicts[
        "functions_ext"
    ].items():
        capturex = CaptureX(
            (func_node,), imported_module, consider_annotations=False
        )
        # replace the tuple (func_node, imported_module) in jitted_dicts by the dependance of func_node
        codes_dependance[func_name] = capturex.make_code_external()

    # remove the decorator (jit) to compute the code dependance
    for key, def_node in def_nodes_dict.items():
        def_node.decorator_list = []

        capturex = CaptureX(
            (def_node,),
            module,
            ancestors=ancestors,
            defuse_chains=duc,
            usedef_chains=udc,
            consider_annotations=False,
        )

        codes_dependance[key] = capturex.make_code_external()

    debug(codes_dependance)

    def_nodes_dict = {}

    for (class_name, method_name), def_node in jitted_dicts["methods"].items():
        if class_name not in def_nodes_dict:
            def_nodes_dict[class_name] = []

        def_nodes_dict[class_name].append(def_node)

    codes_dependance_classes = {}

    for key, def_nodes in def_nodes_dict.items():

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

        codes_dependance_classes[key] = capturex.make_code_external()

    if jitted_dicts["methods"]:
        codes_dependance_classes, code_ext = get_exterior_code(
            codes_dependance_classes,
            pathfile,
            previous_file_name=None,
            classes="classe",
            relative=False,
        )
    codes_dependance, code_ext = get_exterior_code(
        codes_dependance,
        pathfile,
        previous_file_name=None,
        classes="function",
        relative=False,
    )
    return (jitted_dicts, codes_dependance, codes_dependance_classes, code_ext)
