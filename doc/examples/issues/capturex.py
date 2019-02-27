import gast as ast
import beniget
import astunparse


class CaptureX(ast.NodeVisitor):
    def __init__(self, module_node, fun):
        self.fun = fun
        # initialize use-def chains
        self.ud_chains = beniget.UseDefChains()
        self.ud_chains.visit(module_node)
        self.ancestors = beniget.Ancestors()
        self.ancestors.visit(module_node)
        self.external = set()

    def visit_Name(self, node):
        # register load of identifiers not locally defined
        if isinstance(node.ctx, ast.Load):
            def_ = self.ud_chains.chains[node]
            parents = self.ancestors.parents[def_.node]
            if self.fun not in parents:
                parent = parents[-1]
                if parent not in self.external:
                    self.external.add(parent)
                    self.rec(parent)

    def rec(self, node):
        "walk definitions to find their operands's def"
        if isinstance(node, ast.Assign):
            self.visit(node.value)
        # TODO: implement this for AugAssign etc


if __name__ == "__main__":

    code = "a = 1; b = [a, a]\ndef foo():\n return b"
    # code = "a = 1; b = len([a, a])\ndef foo():\n return b"
    # code = "import numpy as bar\na = 1\ndef foo():\n return bar.zeros(2)"
    module = ast.parse(code)
    function = module.body[2]
    capturex = CaptureX(module, function)
    capturex.visit(function)
    # the two top level assignments have been captured!
    list(map(type, capturex.external))

    for node in capturex.external:
        print(astunparse.dump(node))
        print(astunparse.unparse(node))
