import gast as ast

from transonic.analyses.util import gather_rawcode_comments


class BlockDefinition:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.__dict__.update(**kwargs)

    def __repr__(self):
        return repr(self.kwargs)


def get_block_definitions(code, module, ancestors, duc, udc):

    blocks = []
    node_transonic_obj = None
    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.module == "transonic":
            for alias in node.names:
                if alias.name == "Transonic":
                    Transonic_node = alias
                    node_transonic_obj = None
                    for user in duc.chains[Transonic_node].users():
                        parent = ancestors.parent(user.node)
                        if isinstance(parent, ast.Call):
                            grandparent = ancestors.parent(parent)
                            if len(grandparent.targets) != 1:
                                continue
                            node_transonic_obj = grandparent.targets[0]
                    if node_transonic_obj is not None:
                        break

    if node_transonic_obj is None:
        return blocks

    def_ = duc.chains[node_transonic_obj]
    nodes_using_ts = [user.node for user in def_.users()]

    for user in def_.users():
        for user1 in user.users():
            if isinstance(user1.node, ast.Attribute):
                attribute = user1.node
                if attribute.attr == "is_transpiled":
                    parent = ancestors.parent(attribute)
                    if isinstance(parent, ast.If):
                        # it could be the begining of a block
                        if_node = parent
                        if len(parent.body) != 1:
                            # no it's not a block definition
                            continue
                        node = parent.body[0]
                        call = node.value
                        if isinstance(node, ast.Expr):
                            results = []
                        elif isinstance(node, ast.Assign):
                            results = [target.id for target in node.targets]
                        else:
                            # no it's not a block definition
                            continue

                        attribute = call.func
                        ts_node = attribute.value
                        if (
                            ts_node not in nodes_using_ts
                            or attribute.attr != "use_block"
                        ):
                            # no it's not a block definition
                            continue

                        name_block = call.args[0].s

                        rawcode, comments = gather_rawcode_comments(if_node, code)

                        # if we are here, it's a block definition
                        blocks.append(
                            BlockDefinition(
                                name=name_block,
                                results=results,
                                ast_code=if_node.orelse,
                                comments=comments,
                                rawcode=rawcode,
                            )
                        )

    return blocks
