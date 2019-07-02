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

    def adapt_code_dependance(func: str, codes_dependance: str):
        """
        Adapt code_dependance to the call of a jitted function in a jitted function:
            - Remove the import transonic
            - Remove the jitted function statement (i.e func = jit(func))
            - Add a import statement to the jitted function 
            - remove the definition of the jitted function if its on the file, or remove the import statement
        """
        module = extast.parse(codes_dependance)
        module_body = module.body.copy()
        jitted_functions = []
        for node in module_body:
            # remove the transonic import
            if isinstance(node, ast.ImportFrom):
                if node.module == "transonic":
                    module.body.remove(node)
            # remove the jitted function by jit() (i.e. func = jit(func))
            # and add the import statement for the jitted function
            elif isinstance(node, ast.Assign):
                if node.value.func.id == "jit":
                    jitted_functions.append(node.targets[0].id)
                    module.body.remove(node)
                    module.body.insert(
                        0,
                        [
                            extast.parse(
                                "from "
                                + node.value.args[0].id
                                + " import "
                                + node.value.args[0].id
                            )
                        ],
                    )
        # remove the definition:
        for node in module_body:
            # of the jitted function in the file
            if isinstance(node, ast.FunctionDef):
                if node.name in jitted_functions:
                    module.body.remove(node)
            # of the jitted imported function
            if isinstance(node, ast.ImportFrom):
                for name in node.names:
                    if name.name in jitted_functions:
                        node.names.remove(name)
                # remove the importFrom if no function is imported
                if not node.names:
                    module.body.remove(node)
        return extast.unparse(module)

    code_ext = {"function": {}, "classe": {}}

    def get_exterior_code(
        codes_dependance: dict,
        previous_file_name=None,
        classes: str = None,
        relative: bool = None,
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
                        # a jitted function or method needs another jitted function
                        if file_name == "transonic":
                            codes_dependance[func] = adapt_code_dependance(
                                func, codes_dependance[func]
                            )
                        elif file_name:
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
                                codes_dependance[func], node, func, relative
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
                                        relative,
                                    )
        return codes_dependance

    if jitted_dicts["methods"]:
        codes_dependance_classes = get_exterior_code(
            codes_dependance_classes, classes="classe", relative=False
        )
    codes_dependance = get_exterior_code(
        codes_dependance, classes="function", relative=False
    )
    return (jitted_dicts, codes_dependance, codes_dependance_classes, code_ext)
