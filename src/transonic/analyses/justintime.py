"""Analyses for ``@jit``
========================

"""

from transonic.analyses import extast
from transonic.analyses import compute_ancestors_chains, get_decorated_dicts
from transonic.analyses.capturex import CaptureX

from transonic.log import logger
from transonic.analyses.util import get_exterior_code


def analysis_jit(code, pathfile, backend_name):
    """Gather the informations for ``@jit`` with an ast analysis"""
    debug = logger.debug

    debug("extast.parse")
    module = extast.parse(code)

    debug("compute ancestors and chains")
    ancestors, duc, udc = compute_ancestors_chains(module)

    jitted_dicts = get_decorated_dicts(
        module, ancestors, duc, pathfile, backend_name, decorator="jit"
    )

    jitted_dicts = dict(
        functions=jitted_dicts["functions"][backend_name],
        functions_ext=jitted_dicts["functions_ext"][backend_name],
        methods=jitted_dicts["methods"][backend_name],
        classes=jitted_dicts["classes"][backend_name],
    )

    debug("compute code dependance")

    def_nodes_dict = {
        key: def_node
        for kind in ["functions"]
        for key, def_node in jitted_dicts[kind].items()
    }

    codes_dependance = {}

    # get code dependance of a decorated function from a imported module
    for func_name, (func_node, imported_module) in jitted_dicts[
        "functions_ext"
    ].items():
        capturex = CaptureX(
            (func_node,), imported_module, consider_annotations=False
        )
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

    special = []
    spe = []
    if jitted_dicts["methods"]:
        codes_dependance_classes, code_ext, jitted_dicts, spe = get_exterior_code(
            codes_dependance_classes,
            pathfile,
            previous_file_name=None,
            classes="class",
            relative=False,
            jitted_dicts=jitted_dicts,
        )
    special = special + spe
    codes_dependance, code_ext, jitted_dicts, spe = get_exterior_code(
        codes_dependance,
        pathfile,
        previous_file_name=None,
        classes="function",
        relative=False,
        jitted_dicts=jitted_dicts,
    )
    special = special + spe

    return (
        jitted_dicts,
        codes_dependance,
        codes_dependance_classes,
        code_ext,
        special,
    )
