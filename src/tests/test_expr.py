"""Tests for expr.py module."""
import pytest

import expr
from tokens import Token, TokenType

# Examples of Token instances
TOKEN_0 = Token(TokenType.IDENTIFIER, 1, 1, "abc")
TOKEN_1 = Token(TokenType.IDENTIFIER, 1, 2, "abc")
TOKEN_2 = Token(TokenType.BANG, 2, 3, "!")
TOKEN_3 = Token(TokenType.PLUS, 2, 3, "+")
TOKEN_4 = Token(TokenType.PLUS, 3, 3, "+")

# Examples of Expr instances
EXPR_0 = expr.Literal(TOKEN_0)
EXPR_1 = expr.Literal(TOKEN_1)

# pylint: disable=no-self-use, protected-access, too-few-public-methods


class TestLiteral:
    """Tests for expr.Literal."""

    def test_accept(self, mocker):
        """Test accept method."""
        visitor = mocker.Mock()
        literal = expr.Literal(mocker.Mock())

        literal.accept(visitor)

        visitor.visit_literal.assert_called_once_with(literal)

    @pytest.mark.parametrize("left,right,expected", [
        (expr.Literal(TOKEN_0), expr.Literal(TOKEN_0), True),
        (expr.Literal(TOKEN_1), expr.Literal(TOKEN_0), False),
        (expr.Literal(TOKEN_0), expr.Literal(TOKEN_1), False),
        (expr.Literal(TOKEN_0), expr.Unary(TOKEN_0,
                                           expr.Literal(TOKEN_0)), False),
    ])
    def test_eq(self, left, right, expected):
        """Test __eq__ method."""
        result = left == right

        assert result == expected


class TestUnary:
    """Tests for expr.Unary."""

    def test_accept(self, mocker):
        """Test accept method."""
        visitor = mocker.Mock()
        unary = expr.Unary(mocker.Mock(), mocker.Mock())

        unary.accept(visitor)

        visitor.visit_unary.assert_called_once_with(unary)

    @pytest.mark.parametrize(
        "left,right,expected",
        [(expr.Unary(TOKEN_2, EXPR_0), expr.Unary(TOKEN_2, EXPR_0), True),
         (expr.Unary(TOKEN_2, EXPR_0), expr.Unary(TOKEN_2, EXPR_1), False),
         (expr.Unary(TOKEN_2, EXPR_0), EXPR_1, False)])
    def test_eq(self, left, right, expected):
        """Test __eq__ method."""
        result = left == right

        assert result == expected


class TestArithmeticBinary:
    """Tests for expr.ArithmeticBinary."""

    def test_accept(self, mocker):
        """Test accept method."""
        visitor = mocker.Mock()
        binary = expr.ArithmeticBinary(mocker.Mock(), mocker.Mock(),
                                       mocker.Mock())

        binary.accept(visitor)

        visitor.visit_arithmetic_binary.assert_called_once_with(binary)

    @pytest.mark.parametrize(
        "left,right,expected",
        [(expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_0),
          expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_0), True),
         (expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_1),
          expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_0), False),
         (expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_1),
          expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_0), False),
         (expr.ArithmeticBinary(EXPR_0, TOKEN_3, EXPR_0), EXPR_0, False)])
    def test_eq(self, left, right, expected):
        """Test __eq__ method."""
        result = left == right

        assert result == expected


class TestTernary:
    """Tests for expr.Ternary."""

    def test_accept(self, mocker):
        """Test accept method."""
        visitor = mocker.Mock()
        ternary = expr.Ternary(mocker.Mock(), mocker.Mock(), mocker.Mock(),
                               mocker.Mock(), mocker.Mock())

        ternary.accept(visitor)

        visitor.visit_ternary.assert_called_once_with(ternary)

    @pytest.mark.parametrize("left,right,expected", [
        (expr.Ternary(EXPR_0, TOKEN_3, EXPR_1, TOKEN_4, EXPR_0),
         expr.Ternary(EXPR_0, TOKEN_3, EXPR_1, TOKEN_4, EXPR_0), True),
        (expr.Ternary(EXPR_0, TOKEN_3, EXPR_0, TOKEN_4, EXPR_0),
         expr.Ternary(EXPR_0, TOKEN_3, EXPR_1, TOKEN_4, EXPR_0), False),
        (expr.Ternary(EXPR_0, TOKEN_3, EXPR_1, TOKEN_3, EXPR_0),
         expr.Ternary(EXPR_0, TOKEN_3, EXPR_1, TOKEN_4, EXPR_0), False),
        (expr.Ternary(EXPR_0, TOKEN_3, EXPR_1, TOKEN_3, EXPR_0), EXPR_0, False)
    ])
    def test_eq(self, left, right, expected):
        """Test __eq__ method."""
        result = left == right

        assert result == expected
