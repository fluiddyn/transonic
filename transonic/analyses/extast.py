"""Extended AST with CommentLine nodes
======================================

"""

from io import StringIO
from copy import deepcopy

import ast as _ast

import gast as ast
from gast.ast3 import GAstToAst3 as _GAstToAst3
import astunparse

from transonic.analyses import beniget


class CommentLine(ast.AST):
    """"New AST node representing a comment line"""

    _fields = ("s",)

    def __init__(self, s, lineno=None):
        super().__init__()
        self.s = s
        if lineno is not None:
            self.lineno = lineno

    def __deepcopy__(self, memo):
        try:
            lineno = self.lineno
        except AttributeError:
            lineno = None
        return self.__class__(deepcopy(self.s), lineno)


class GAstToAst3(_GAstToAst3):
    def visit_CommentLine(self, node):
        return node


def gast_to_ast(node):
    return GAstToAst3().visit(node)


class UnparserExtended(astunparse.Unparser):
    """Unparser for extented AST"""

    def __init__(self, tree, file, with_comments=True):
        self.with_comments = with_comments
        super().__init__(tree, file=file)

    boolops = {ast.And: "and", ast.Or: "or", _ast.And: "and", _ast.Or: "or"}

    def _CommentLine(self, node):
        if self.with_comments:
            self.write(f"\n{'    '* self._indent}{node.s}")


def parse(code, *args, **kwargs):
    """Parse a code and produce the extended AST"""
    tree = ast.parse(code, *args, **kwargs)
    CommentInserter(tree, code)
    return tree


def unparse(tree, with_comments=True):
    """Unparse the extended AST"""

    module = type(tree).__module__
    if "gast" in module:
        tree = gast_to_ast(tree)

    v = StringIO()
    UnparserExtended(tree, file=v, with_comments=with_comments)
    return v.getvalue()


class CommentInserter(ast.NodeVisitor):
    """Insert the CommentLine nodes in an AST tree"""

    def __init__(self, tree, code):
        self.tree = tree

        self.ancestors = beniget.Ancestors()
        self.ancestors.visit(tree)

        self.code = code
        self.lines = code.split("\n")

        self.lines_comments = []
        self.lineno_comments = []
        for index, line in enumerate(self.lines):
            if line.strip().startswith("#"):
                self.lineno_comments.append(index + 1)
                self.lines_comments.append(line)

        if not self.lineno_comments:
            # nothing to do
            return

        self.last_line_comment = max(self.lineno_comments)

        self.index_comment = 0

        self.node_after = {}
        self.node_before = []

        self.previous_node = None

        self._done = False

        self.visit(tree)

        self.node_before = {
            self.lineno_comments[index]: node_before
            for index, node_before in enumerate(self.node_before)
        }

        self.modify_tree()

    def visit(self, node):

        if self._done:
            return

        if hasattr(node, "lineno"):

            linenos = self.lineno_comments

            while node.lineno > linenos[self.index_comment]:
                self.node_after[linenos[self.index_comment]] = node
                if linenos[self.index_comment] == self.last_line_comment:
                    self._done = True
                    return
                self.index_comment += 1

            while len(self.node_after) > len(self.node_before):
                self.node_before.append(self.previous_node)

        self.previous_node = node

        super().visit(node)

    def modify_tree(self):

        # todo: debug this buggy code!

        for lineno, line in zip(self.lineno_comments, self.lines_comments):
            try:
                node_after = self.node_after[lineno]
            except KeyError:
                self.tree.body.append(CommentLine(line, lineno))
                continue
            else:
                self.insert_comment_in_parent_before_node(
                    line, lineno, node_after
                )
                continue

            try:
                node_before = self.node_before[lineno]
            except KeyError:
                pass
            else:
                if isinstance(node_before, ast.Module):
                    self.tree.body.insert(0, CommentLine(line, lineno))

    def insert_comment_in_parent_before_node(self, line, lineno, node):

        parent = self.ancestors.parent(node)
        comment = line.strip()

        for field, value in ast.iter_fields(parent):
            if isinstance(value, list):
                if node in value:
                    index = value.index(node)
                    value.insert(index, CommentLine(comment, lineno))


try:
    ast.Constant
except AttributeError:
    # gast < 0.3.0
    class Constant(ast.Str):
        def __init__(self, value):
            super().__init__(value)
            self.value = value

    class Name(ast.Name):
        def __init__(self, id="annotations", ctx=ast.Store(), annotation=None):
            super().__init__(id, ctx, annotation)

    class FunctionDef(ast.FunctionDef):
        def __init__(
            self,
            name,
            args,
            body,
            decorator_list=None,
            returns=None,
            type_comment=None,
        ):
            if decorator_list is None:
                decorator_list = []
            super().__init__(name, args, body, decorator_list, returns)


else:
    # gast >= 0.3.0
    class Constant(ast.Constant):
        def __init__(self, value):
            super().__init__(value, None)

    class Name(ast.Name):
        def __init__(self, id="annotations", ctx=ast.Store(), annotation=None):
            super().__init__(id, ctx, annotation, None)

    class FunctionDef(ast.FunctionDef):
        def __init__(
            self,
            name,
            args,
            body,
            decorator_list=None,
            returns=None,
            type_comment=None,
        ):
            if decorator_list is None:
                decorator_list = []
            super().__init__(
                name, args, body, decorator_list, returns, type_comment
            )


if __name__ == "__main__":
    code = """
# comment 0
# comment 1
if True:
# comment 1bis
    # comment 2
    # comment 3
    var_if = 1
    # comment after var_if
    if False:
        var_ifif = 1
        # comment ifif
    # comment if end
# comment 4
else:
    # comment else
    var_else = 1
# comment after else
a += 1
# comment after last
    """

    code = """
from transonic import Transonic
import numpy as np
import foo

ts = Transonic()
a = n = 1
b = np.ones(2)

if ts.is_transpiled:
    result = ts.use_block("block0")
else:
    # transonic block (
    #     A a; A1 b;
    #     float n
    # )

    # transonic block (
    #     int[:] a, b;
    #     float n
    # )

    result = a ** 2 + b.mean() ** 3 + foo.bar(n)

    """

    tree = parse(code)

    print(unparse(tree, with_comments=True))

    from transonic.analyses import compute_ancestors_chains

    compute_ancestors_chains(tree)
