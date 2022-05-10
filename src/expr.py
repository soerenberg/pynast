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


class Literal(Expr):
    """Literal expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, token: tokens.Token):
        super().__init__()
        self.token = token

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_literal(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, Literal) and self.token == other.token


class Unary(Expr):
    """Unary operation with one operator and one expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, operator: tokens.Token, right: Expr):
        super().__init__()
        self.operator = operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Unary) and self.operator == other.operator
                and self.right == other.right)


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

    def __eq__(self, other) -> bool:
        return (isinstance(other, ArithmeticBinary) and self.left == other.left
                and self.operator == other.operator
                and self.right == other.right)


class Ternary(Expr):
    """Ternary expression, with 3 operands and two infix operators."""

    # pylint: disable=too-few-public-methods

    def __init__(self, left: Expr, left_operator: tokens.Token, middle: Expr,
                 right_operator: tokens.Token,
                 right: Expr
                 ):  # yapf: disable, pylint: disable=too-many-arguments
        super().__init__()
        self.left = left
        self.left_operator = left_operator
        self.middle = middle
        self.right_operator = right_operator
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_ternary(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Ternary) and self.left == other.left
                and self.left_operator == other.left_operator
                and self.middle == other.middle
                and self.right_operator == other.right_operator
                and self.right == other.right)


class FunctionApplication(Expr):
    """Function application."""

    def __init__(self, callee: Expr, closing_paren: tokens.Token,
                 arguments: List[Expr]):
        self.callee = callee
        self.closing_paren = closing_paren
        self.arguments = arguments

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_function_application(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, FunctionApplication)
                and self.callee == other.callee
                and self.closing_paren == other.closing_paren
                and self.arguments == other.arguments)


class Indexing(Expr):
    """Array or matrix indexing."""

    def __init__(self, callee: Expr, closing_bracket: tokens.Token,
                 indices: List[Expr]):
        self.callee = callee
        self.closing_bracket = closing_bracket
        self.indices = indices

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_indexing(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Indexing) and self.callee == other.callee
                and self.closing_bracket == other.closing_bracket
                and self.indices == other.indices)


class Slice(Expr):
    """Array or matrix indexing slice."""
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_slice(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Slice) and self.left == other.left
                and self.right == other.right)


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


class Indexes(Expr):
    """Indexes expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, expressions: List[Expr]):
        self.expressions = expressions

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_indexes(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Indexes)
                and self.expressions == other.expressions)


class Variable(Expr):
    """Variable expression."""

    # pylint: disable=too-few-public-methods

    def __init__(self, identifier: tokens.Token):
        super().__init__()
        self.identifier = identifier

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_variable(self)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Variable)
                and self.identifier == other.identifier)


class Visitor:
    """Visitor for Expr types."""

    @abc.abstractmethod
    def visit_literal(self, expr: Literal) -> Any:
        """Visit Literal."""

    @abc.abstractmethod
    def visit_unary(self, expr: Unary) -> Any:
        """Visit Unary."""

    @abc.abstractmethod
    def visit_arithmetic_binary(self, expr: ArithmeticBinary) -> Any:
        """Visit ArithmeticBinary."""

    @abc.abstractmethod
    def visit_ternary(self, expr: Ternary) -> Any:
        """Visit Ternary."""

    @abc.abstractmethod
    def visit_function_application(self, expr: FunctionApplication) -> Any:
        """Visit FunctionApplication."""

    @abc.abstractmethod
    def visit_indexing(self, expr: Indexing) -> Any:
        """Visit Indexing."""

    @abc.abstractmethod
    def visit_slice(self, expr: Slice) -> Any:
        """Visit Slice."""

    @abc.abstractmethod
    def visit_range(self, expr: Range) -> Any:
        """Visit Range."""

    @abc.abstractmethod
    def visit_indexes(self, expr: Indexes) -> Any:
        """Visit Indexes."""

    @abc.abstractmethod
    def visit_variable(self, expr: Variable) -> Any:
        """Visit Variable."""
