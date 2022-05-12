"""Statement nodes for ASTs."""
from __future__ import annotations
import abc
from typing import Any, Optional

import expr
import tokens


class Stmt:
    """Statement base class."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        """Accept method for the visitor pattern."""


class Declaration(Stmt):
    """Variable declaration statement."""

    # pylint: disable=too-few-public-methods

    def __init__(self,
                 dtype: tokens.Token,
                 identifier: tokens.Token,
                 lower: Optional[expr.Expr] = None,
                 upper: Optional[expr.Expr] = None,
                 offset: Optional[expr.Expr] = None,
                 multiplier: Optional[expr.Expr] = None,
                 initializer: Optional[expr.Expr] = None):
        # pylint: disable=too-many-arguments
        self.dtype = dtype
        self.identifier = identifier
        self.lower = lower
        self.upper = upper
        self.offset = offset
        self.multiplier = multiplier
        self.initializer = initializer

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_declaration(self)

    def __eq__(self, other):
        return (isinstance(other, Declaration) and self.dtype == other.dtype
                and self.identifier == other.identifier
                and self.lower == other.lower and self.upper == other.upper
                and self.offset == other.offset
                and self.multiplier == other.multiplier
                and self.initializer == other.initializer)


class Visitor:
    """Visitor for Stmt types."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def visit_declaration(self, statement: Declaration) -> Any:
        """Visit Declaration."""
