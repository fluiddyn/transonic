"""Capture the external nodes used in functions
===============================================
"""

import gast as ast

from transonic.analyses import beniget
from transonic.analyses import extast


class CaptureX(ast.NodeVisitor):
    """Capture the external nodes used in functions, classes and blocks"""

    def __init__(
        self,
        functions,
        module_node,
        ancestors=None,
        defuse_chains=None,
        usedef_chains=None,
        consider_annotations=True,
        blocks=None,
    ):

        if defuse_chains is None:
            self.du_chains = du = beniget.DefUseChains()
            du.visit(module_node)
            self.ud_chains = beniget.UseDefChains(du)
            self.ancestors = beniget.Ancestors()
            self.ancestors.visit(module_node)
        else:
            self.du_chains = defuse_chains
            self.ud_chains = usedef_chains
            self.ancestors = ancestors

        self.consider_annotations = consider_annotations
        self._annot = None

        self.external = []
        self.visited_external = set()

        self.functions = functions
        for func in functions:
            self.func = func
            self.visit(func)

        if blocks is None:
            return

        for nodes in blocks:
            if nodes:
                node = nodes[0]
                self.func = ancestors.parentFunction(node)
                for node in nodes:
                    self.visit(node)

    def visit_Name(self, node):

        parent_node = self.ancestors.parents(node)[-1]
        if (
            isinstance(parent_node, ast.FunctionDef)
            and node == parent_node.returns
            and not self.consider_annotations
        ):
            return

        # register load of identifiers not locally defined
        if isinstance(node.ctx, ast.Load):
            try:
                self.ud_chains.chains[node]
            except KeyError:
                if not (
                    isinstance(parent_node, ast.FunctionDef)
                    and node == parent_node.returns
                ):
                    raise
                from warnings import warn

                warn(f"BUG Beniget (node.id={node.id}), but we try to continue!")
                return

            for def_ in self.ud_chains.chains[node]:
                try:
                    parents = self.ancestors.parents(def_.node)
                except KeyError:
                    return  # a builtin
                if self.func not in parents:
                    if isinstance(def_.node, ast.FunctionDef):
                        defining_node = def_.node
                    else:
                        defining_node = self.ancestors.parentStmt(def_.node)
                    if defining_node not in self.visited_external:
                        self.rec(defining_node)
                        if defining_node in self.functions:
                            return

                        if (
                            self.consider_annotations == "only"
                            and self._annot is None
                        ):
                            return

                        if defining_node not in self.visited_external:
                            self.visited_external.add(defining_node)
                            self.external.append(defining_node)
        elif (
            isinstance(node.ctx, (ast.Param, ast.Store))
            and self.consider_annotations
        ):
            if node.annotation is None:
                return
            self._annot = node.annotation
            self.visit(node.annotation)
            self._annot = None

    def visit_ClassDef(self, node_class):
        for node in node_class.body:
            if isinstance(node, ast.AnnAssign):
                self._annot = node.annotation
                self.visit(node)
                self._annot = None

    def visit_AnnAssign(self, node):
        if self.consider_annotations:
            self._annot = node.annotation
            self.visit(node.annotation)
            self._annot = None

        if node.value is not None and self.consider_annotations != "only":
            self.visit(node.value)

    def rec(self, node):
        "walk definitions to find their operands's def"
        if node is self.func:
            return

        if isinstance(node, ast.Assign):
            self.visit(node.value)
        elif isinstance(node, ast.FunctionDef):
            # tmp: to deal with @include
            node.decorator_list = []

            old_func = self.func
            self.func = node
            self.visit(node)
            self.func = old_func

        # TODO: implement this for AugAssign etc

    def make_code_external(self):
        code = []
        for node in self.external:
            code.append(extast.unparse(node).strip())
        return "\n".join(code)


if __name__ == "__main__":

    code = "a = 1; b = [a, a]\ndef foo():\n return b"
    # code = "a = 1; b = len([a, a])\ndef foo():\n return b"
    # code = "import numpy as np\na = np.int(1)\ndef foo():\n return np.zeros(a)"

    code = """

a = 1

def fooo():
    return 1

def foo():
    return a + fooo()

def bar():
    return foo()

    """

    module = extast.parse(code)
    function = module.body[3]
    capturex = CaptureX((function,), module)

    print(capturex.make_code_external())
