"""Expression node for ASTs."""
from __future__ import annotations

import abc
from typing import Any, List, Optional

import tokens


class Expr:
    """Base class for expressions."""

    # pylint: disable=too-few-public-methods

    @abc.abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        """Accept method for the visitor pattern."""


class Unary(Expr):
    """Unary operation with one operator and one expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, operator: tokens.Token, right: Expr):
        super().__init__()
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary(self)


class ArithmeticBinary(Expr):
    """Arithmetic binary expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, left: Expr, operator: tokens.Token, right: Expr):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_arithmetic_binary(self)


class Range(Expr):
    """Index range expression.

    Has the form <expression> ':' <expression> .
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, left: Optional[Expr], right: Optional[Expr]):
        self.left = left
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_range(self)

    def __eq__(self, other) -> bool:
        return self.left == other.left and self.right == other.right


class Variable(Expr):
    """Variable expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, identifier: tokens.Token):
        super().__init__()
        self.identifier = identifier

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_variable(self)


class Visitor:
    """Visitor for Expr types."""

    @abc.abstractmethod
    def visit_unary(self, expr: Unary) -> Any:
        """Visit Unary."""

    @abc.abstractmethod
    def visit_arithmetic_binary(self, expr: ArithmeticBinary) -> Any:
        """Visit ArithmeticBinary."""

    @abc.abstractmethod
    def visit_range(self, expr: Range) -> Any:
        """Visit Range."""

    @abc.abstractmethod
    def visit_variable(self, expr: Variable) -> Any:
        """Visit Variable."""
