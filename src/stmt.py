"""Statement nodes for ASTs."""
from __future__ import annotations
import abc
from typing import Any, List, Optional

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
                 type_dims: Optional[List[expr.Expr]] = None,
                 lower: Optional[expr.Expr] = None,
                 upper: Optional[expr.Expr] = None,
                 offset: Optional[expr.Expr] = None,
                 multiplier: Optional[expr.Expr] = None,
                 array_dims: Optional[List[expr.Expr]] = None,
                 initializer: Optional[expr.Expr] = None):
        # pylint: disable=too-many-arguments
        self.dtype = dtype
        self.identifier = identifier
        self.type_dims = type_dims or []
        self.lower = lower
        self.upper = upper
        self.offset = offset
        self.multiplier = multiplier
        self.array_dims = array_dims or []
        self.initializer = initializer

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_declaration(self)

    def __eq__(self, other):
        return (isinstance(other, Declaration) and self.dtype == other.dtype
                and self.identifier == other.identifier
                and self.type_dims == other.type_dims
                and self.lower == other.lower and self.upper == other.upper
                and self.offset == other.offset
                and self.multiplier == other.multiplier
                and self.initializer == other.initializer)


class IncrementLogProb(Stmt):
    """increment_log_prob statement, deprecated in Stan 3."""

    def __init__(self, keyword: tokens.Token, value: expr.Expr):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_increment_log_prob(self)

    def __eq__(self, other):
        return (isinstance(other, IncrementLogProb)
                and self.keyword == other.keyword
                and self.value == other.value)


class Break(Stmt):
    """break statement."""

    def __init__(self, keyword: tokens.Token):
        self.keyword = keyword

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_break(self)

    def __eq__(self, other):
        return (isinstance(other, Break) and self.keyword == other.keyword)


class Visitor:
    """Visitor for Stmt types."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def visit_declaration(self, statement: Declaration) -> Any:
        """Visit Declaration."""

    @abc.abstractmethod
    def visit_increment_log_prob(self, statement: IncrementLogProb) -> Any:
        """Visit IncrementLogProb."""

    @abc.abstractmethod
    def visit_break(self, statement: Break) -> Any:
        """Visit Break."""
