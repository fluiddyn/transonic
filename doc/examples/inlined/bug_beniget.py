
import gast as ast
import beniget

mod = ast.parse("""
T = int
def func() -> T:
    return 1
""")

fdef = mod.body[1]
node = fdef.returns

du = beniget.DefUseChains()
du.visit(mod)

du.chains[node]

ud = beniget.UseDefChains(du)

ud.chains[node]
