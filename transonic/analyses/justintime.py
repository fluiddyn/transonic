"""Analyses for ``@jit``
========================

"""
import gast as ast
from path import Path

from transonic.log import logger

from transonic.analyses import extast
from transonic.analyses import compute_ancestors_chains, get_decorated_dicts
from transonic.analyses.capturex import CaptureX

from transonic.analyses.util import print_dumped


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

    import sys

    def filter_external_code(module: object, names: list):
        """ Filter the module to keep only the necessary nodes 
            needed by functions in the parameter names
        """
        import gast as ast

        code = ""
        for node in module.body:
            for name in names:
                if isinstance(node, ast.FunctionDef):
                    if node.name == extast.unparse(name).rstrip("\n\r"):
                        ancestors, duc, udc = compute_ancestors_chains(module)
                        capturex = CaptureX(
                            [node],
                            module,
                            ancestors,
                            defuse_chains=duc,
                            usedef_chains=udc,
                            consider_annotations=None,
                        )

                        code += " \n " + str(extast.unparse(node))
                if isinstance(node, ast.Assign):
                    if node.targets[0].id == extast.unparse(name).rstrip("\n\r"):
                        code += str(extast.unparse(node))
        code_dependance_annotations = capturex.make_code_external()
        return code_dependance_annotations + code

    # FIXME find path in non local imports
    def find_path(node: object):
        """ Return the path of node (instance of ast.Import or ast.ImportFrom)
        """
        name = str()
        path = str()
        if isinstance(node, ast.ImportFrom):
            name = node.module
            if name in ["numpy", "math", "functools", "cmath"]:
                return None, None
            else:
                parent = Path(pathfile).parent
                path = parent / (name.replace(".", "/")) + ".py"

        else:
            # TODO complete the list
            if node.names[0].name in ["numpy", "math", "functools", "cmath"]:
                pass
            else:
                # TODO deal with an ast.Import
                raise NotImplementedError
        return name, path

    def change_import_name(code_dep: str, changed_node: object, func: str):
        """ Change the name of changed_node in code_dep by adding "__"+func+"__" 
            at the beginning of the imported module, and return the modified code
        """
        mod = extast.parse(code_dep)
        for node in mod.body:
            if extast.unparse(node) == extast.unparse(changed_node):
                if isinstance(node, ast.ImportFrom):
                    node.module = "__" + func + "__" + node.module
                elif isinstance(node, ast.Import):
                    node.names[0].name = "__" + func + "__" + node.names[0].name
        return extast.unparse(mod)

    code_ext = {}
    for func, dep in codes_dependance.items():
        if dep:
            module_ext = extast.parse(dep)
            for node in module_ext.body:
                if isinstance(node, ast.ImportFrom) or isinstance(
                    node, ast.Import
                ):
                    # get the path of the imported module
                    file_name, file_path = find_path(node)
                    if file_name:
                        file_name = "__" + func + "__" + file_name
                        # get the content of the file 
                        with open(str(file_path), "r") as file:
                            content = file.read()
                        file.close()
                        mod = extast.parse(content)
                        # filter the code and add it to code_ext dict
                        if file_name in code_ext:
                            code_ext[file_name] += str(
                                filter_external_code(mod, node.names)
                            )
                        else:
                            code_ext[file_name] = str(
                                filter_external_code(mod, node.names)
                            )
                        # change imported module names
                        codes_dependance[func] = change_import_name(
                            codes_dependance[func], node, func
                        )

    return (jitted_dicts, codes_dependance, codes_dependance_classes, code_ext)
