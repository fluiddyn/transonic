import beniget
import gast as ast
import astunparse


def dump(node):
    print(astunparse.dump(node))


# from capturex import CaptureX

with open("issue7_method.py") as file:
    code = file.read()

module = ast.parse(code)

duc = beniget.DefUseChains()
duc.visit(module)

ucc = beniget.UseDefChains(duc)

ancestors = beniget.Ancestors()
ancestors.visit(module)

boost = [d for d in duc.locals[module] if d.name() == "boost"][0]

chain = duc.chains[boost.node]
