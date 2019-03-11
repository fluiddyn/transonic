import gast as ast
import beniget


class CaptureX(ast.NodeVisitor):
    def __init__(self, module_node, fun):
        self.fun = fun
        # initialize use-def chains
        self.du_chains = du = beniget.DefUseChains()
        du.visit(module_node)
        self.ud_chains = beniget.UseDefChains(du)
        self.ancestors = beniget.Ancestors()
        self.ancestors.visit(module_node)
        self.external = []
        self.visited_external = set()

    def visit_Name(self, node):
        # register load of identifiers not locally defined
        if isinstance(node.ctx, ast.Load):
            def_ = self.ud_chains.chains[node]
            try:
                parents = self.ancestors.parents(def_.node)
            except KeyError:
                return  # a builtin
            if self.fun not in parents:
                try:
                    defining_node = self.ancestors.parentStmt(def_.node)
                except ValueError:
                    # FunctionDef
                    defining_node = def_.node
                if defining_node not in self.visited_external:
                    self.rec(defining_node)
                    self.visited_external.add(defining_node)
                    self.external.append(defining_node)

    def rec(self, node):
        "walk definitions to find their operands's def"
        if isinstance(node, ast.Assign):
            self.visit(node.value)
        elif isinstance(node, ast.FunctionDef):
            old_func = self.fun
            self.fun = node
            self.visit(node)
            self.fun = old_func

        # TODO: implement this for AugAssign etc


if __name__ == "__main__":

    from transonic.analyses import extast

    code = "a = 1; b = [a, a]\ndef foo():\n return b"
    # code = "a = 1; b = len([a, a])\ndef foo():\n return b"
    # code = "import numpy as np\na = np.int(1)\ndef foo():\n return np.zeros(a)"

    code = """

a = 1

def fooo():
    # comment fooo
    return 1

# comment in module

def foo():
    # comment in foo
    return a + fooo()

def bar():
    return foo()

    """


    module = extast.parse(code)
    function = module.body[3]
    capturex = CaptureX(module, function)

    capturex.visit(function)
    for node in capturex.external:
        # print(astunparse.dump(node))
        print(extast.unparse(node).strip())
