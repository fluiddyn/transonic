"""Analyses for ``@jit``
========================

"""
import gast as ast

from transonic.log import logger

from transonic.analyses import extast
from transonic.analyses import compute_ancestors_chains, get_decorated_dicts
from transonic.analyses.capturex import CaptureX

from transonic.analyses.util import print_dumped
from .util import find_path, change_import_name, filter_external_code


def analysis_jit(code, pathfile):
    """Gather the informations for ``@jit`` with an ast analysis"""
    debug = logger.debug

    debug("extast.parse")
    module = extast.parse(code)

    debug("compute ancestors and chains")
    ancestors, duc, udc = compute_ancestors_chains(module)

    # boosted_dicts = get_boosted_dicts(module, ancestors, duc)

    jitted_dicts = get_decorated_dicts(module, ancestors, duc, decorator="jit")

    debug("compute code dependance")

    def_nodes_dict = {
        key: def_node
        for kind in ["functions"]
        for key, def_node in jitted_dicts[kind].items()
    }

    codes_dependance = {}

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

    code_ext = {}
    code_ext_cls = {}

    def get_exterior_code(
        codes_dependance: dict, previous_file_name=None, cls=None
    ):
        """ Get all imported functions needed by jitted functions add multiple levels,
            i.e get functions needed by functions needed by jitted function.
        """
        for func, dep in codes_dependance.items():
            if not dep:
                continue
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
                        if cls:
                            # filter the code and add it to code_ext dict
                            code_ext_cls[file_name] = str(
                                filter_external_code(mod, node.names)
                            )
                            # change imported module names
                            codes_dependance_classes[func] = change_import_name(
                                codes_dependance_classes[func],
                                node,
                                func,
                                cls="yes",
                            )
                            # recursively get the exteriors codes
                            if code_ext_cls[file_name]:
                                get_exterior_code(
                                    {func: code_ext_cls[file_name]},
                                    file_name,
                                    cls="yes",
                                )
                                if previous_file_name:
                                    code_ext_cls[
                                        previous_file_name
                                    ] = change_import_name(
                                        code_ext_cls[previous_file_name],
                                        node,
                                        func,
                                        cls="yes",
                                    )
                        else:
                            # filter the code and add it to code_ext dict
                            code_ext[file_name] = str(
                                filter_external_code(mod, node.names)
                            )
                            # change imported module names
                            codes_dependance[func] = change_import_name(
                                codes_dependance[func], node, func
                            )
                            # recursively get the exteriors codes
                            if code_ext[file_name]:
                                get_exterior_code(
                                    {func: code_ext[file_name]}, file_name
                                )
                                if previous_file_name:
                                    code_ext[
                                        previous_file_name
                                    ] = change_import_name(
                                        code_ext[previous_file_name], node, func
                                    )

    if jitted_dicts["methods"]:
        get_exterior_code(codes_dependance_classes, cls="yes")
    get_exterior_code(codes_dependance)
    return (
        jitted_dicts,
        codes_dependance,
        codes_dependance_classes,
        code_ext,
        code_ext_cls,
    )
