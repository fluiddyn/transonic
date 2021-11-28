import gast as ast

from beniget import Ancestors, DefUseChains as DUC, UseDefChains

from beniget.beniget import Def


__all__ = ["Ancestors", "DefUseChains", "UseDefChains"]


class DefUseChains(DUC):
    def visit_List(self, node):
        if isinstance(node.ctx, ast.Load):
            dnode = self.chains.setdefault(node, Def(node))
            for elt in node.elts:
                if isinstance(elt, CommentLine):
                    continue
                self.visit(elt).add_user(dnode)
            return dnode
        # unfortunately, destructured node are marked as Load,
        # only the parent List/Tuple is marked as Store
        elif isinstance(node.ctx, ast.Store):
            return self.visit_Destructured(node)

    visit_Tuple = visit_List


# this import has to be after the definition of DefUseChains
from transonic.analyses.extast import CommentLine  # noqa: E402
