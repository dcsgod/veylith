"""Source distribution hygiene: docstring, comment, and source-map stripping using LibCST."""

from __future__ import annotations

import libcst as cst
from libcst import (
    EmptyLine,
    FunctionDef,
    Module,
    TrailingWhitespace,
)


def _is_docstring_stmt(stmt: cst.CSTNode) -> bool:
    """Return True if node is a SimpleStatementLine containing a docstring string literal."""
    if isinstance(stmt, cst.SimpleStatementLine) and stmt.body:
        small = stmt.body[0]
        if isinstance(small, cst.Expr) and isinstance(
            small.value, (cst.SimpleString, cst.ConcatenatedString)
        ):
            return True
    return False


class DocstringAndCommentStripper(cst.CSTTransformer):
    """Safely strips docstrings and inline comments while preserving code structure and syntax."""

    def __init__(self, strip_docstrings: bool = True, strip_comments: bool = True) -> None:
        self.strip_docstrings = strip_docstrings
        self.strip_comments = strip_comments

    def visit_Module(self, node: Module) -> bool:
        return True

    def leave_Module(self, original_node: Module, updated_node: Module) -> Module:
        if not self.strip_docstrings:
            return updated_node

        # Check if first statement in module body is a docstring
        if updated_node.body and _is_docstring_stmt(updated_node.body[0]):
            new_body = list(updated_node.body[1:])
            return updated_node.with_changes(body=new_body)

        return updated_node

    def leave_FunctionDef(
        self, original_node: FunctionDef, updated_node: FunctionDef
    ) -> FunctionDef:
        if not self.strip_docstrings:
            return updated_node

        body = updated_node.body
        if isinstance(body, cst.IndentedBlock) and body.body and _is_docstring_stmt(body.body[0]):
            if len(body.body) == 1:
                pass_stmt = cst.SimpleStatementLine(body=[cst.Pass()])
                new_block = body.with_changes(body=[pass_stmt])
            else:
                new_block = body.with_changes(body=list(body.body[1:]))
            return updated_node.with_changes(body=new_block)

        return updated_node

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        if not self.strip_docstrings:
            return updated_node

        body = updated_node.body
        if isinstance(body, cst.IndentedBlock) and body.body and _is_docstring_stmt(body.body[0]):
            if len(body.body) == 1:
                pass_stmt = cst.SimpleStatementLine(body=[cst.Pass()])
                new_block = body.with_changes(body=[pass_stmt])
            else:
                new_block = body.with_changes(body=list(body.body[1:]))
            return updated_node.with_changes(body=new_block)

        return updated_node

    def leave_TrailingWhitespace(
        self, original_node: TrailingWhitespace, updated_node: TrailingWhitespace
    ) -> TrailingWhitespace:
        if self.strip_comments and updated_node.comment is not None:
            return updated_node.with_changes(comment=None)
        return updated_node

    def leave_EmptyLine(self, original_node: EmptyLine, updated_node: EmptyLine) -> EmptyLine:
        if self.strip_comments and updated_node.comment is not None:
            return updated_node.with_changes(comment=None)
        return updated_node


def apply_python_hygiene(
    source_code: str, strip_docstrings: bool = True, strip_comments: bool = True
) -> str:
    """Parse Python code using LibCST, apply hygiene transformations, and return updated code."""
    try:
        tree = cst.parse_module(source_code)
    except Exception:
        # If parsing fails (e.g. invalid syntax), return original unmodified
        return source_code

    transformer = DocstringAndCommentStripper(
        strip_docstrings=strip_docstrings, strip_comments=strip_comments
    )
    modified_tree = tree.visit(transformer)
    return modified_tree.code
