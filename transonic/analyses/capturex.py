import gast as ast
import beniget
import astunparse


class CaptureX(ast.NodeVisitor):
    def __init__(
        self,
        functions,
        module_node,
        ancestors=None,
        defuse_chains=None,
        usedef_chains=None,
        consider_annotations=True,
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

    def visit_Name(self, node):
        # register load of identifiers not locally defined
        if isinstance(node.ctx, ast.Load):
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

                        self.visited_external.add(defining_node)
                        self.external.append(defining_node)
        elif isinstance(node.ctx, (ast.Param, ast.Store)) and self.consider_annotations:
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

    def rec(self, node):
        "walk definitions to find their operands's def"
        if isinstance(node, ast.Assign):
            self.visit(node.value)
        elif isinstance(node, ast.FunctionDef):
            old_func = self.func
            self.func = node
            self.visit(node)
            self.func = old_func

        # TODO: implement this for AugAssign etc


def make_code_external(external, code_module=None):
    code = []
    for node in external:
        code.append(astunparse.unparse(node).strip())
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

    module = ast.parse(code)
    function = module.body[3]
    capturex = CaptureX((function,), module)

    print(make_code_external(capturex.external))
