import ast as _ast

import gast
from beniget import beniget as _beniget
from beniget import Ancestors
from beniget import DefUseChains as DUC
from beniget import UseDefChains
from beniget.beniget import Def

__all__ = ["Ancestors", "DefUseChains", "UseDefChains"]


def _pkg(node):
    """
    Given a supported AST node, return the origin module where it's class is defined.
    The result will be gast or ast.
    """
    module_name = node.__class__.__module__
    return (
        gast.gast
        if module_name in ["gast.gast", "transonic.analyses.extast"]
        else _ast
    )


_beniget.pkg = _pkg


class DefUseChains(DUC):
    def visit_List(self, node):
        if isinstance(node.ctx, gast.Load):
            dnode = self.chains.setdefault(node, Def(node))
            for elt in node.elts:
                if isinstance(elt, CommentLine):
                    continue
                self.visit(elt).add_user(dnode)
            return dnode
        # unfortunately, destructured node are marked as Load,
        # only the parent List/Tuple is marked as Store
        elif isinstance(node.ctx, gast.Store):
            return self.visit_Destructured(node)

    visit_Tuple = visit_List


# this import has to be after the definition of DefUseChains
from transonic.analyses.extast import CommentLine  # noqa: E402
