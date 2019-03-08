import gast as ast

import beniget


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