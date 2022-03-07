"""Expression node for ASTs."""
from __future__ import annotations

import abc
from typing import Any

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


class Visitor:
    """Visitor for Expr types."""

    @abc.abstractmethod
    def visit_unary(self, expr: Unary) -> Any:
        """Visit Unary."""
