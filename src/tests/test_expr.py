"""Tests for expr.py module."""
import pytest

import expr
from tokens import Token, TokenType

TOKEN_0 = Token(TokenType.IDENTIFIER, 1, 1, "abc")
TOKEN_1 = Token(TokenType.IDENTIFIER, 1, 2, "abc")
TOKEN_1 = Token(TokenType.IDENTIFIER, 1, 1, "ABC")

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
