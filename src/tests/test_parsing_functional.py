"""Functional tests for parsing.py module."""
import itertools

import pytest

import expr
import parsing
from tokens import Token, TokenType

# pylint: disable=no-self-use, protected-access, too-few-public-methods


def test_indexes():
    """Simple test to parse expression of the form <identifier>[:][:]."""

    expected = expr.Variable(Token(TokenType.IDENTIFIER, 1, 1, "my_name"), [
        expr.Indexes([expr.Range(None, None)]),
        expr.Indexes([expr.Range(None, None)])
    ])

    token_list = [
        Token(TokenType.IDENTIFIER, 1, 1, "my_name"),
        Token(TokenType.LBRACK, 1, 2, "["),
        Token(TokenType.COLON, 1, 3, ":"),
        Token(TokenType.RBRACK, 1, 4, "]"),
        Token(TokenType.LBRACK, 1, 5, "["),
        Token(TokenType.COLON, 1, 6, ":"),
        Token(TokenType.RBRACK, 1, 7, "]"),
        Token(TokenType.EOF, 1, 8, "")
    ]

    parser = parsing.Parser(token_list)

    result = parser._parse_expression()

    assert expected == result


def test_parse_precedences(mocker):
    """Functional test to validate correct precedences between chosen ops."""
    operands = [mocker.Mock() for _ in range(10)]
    operators = [
        Token(TokenType.PLUS, 2, 1, "+"),
        Token(TokenType.TIMES, 2, 3, "*"),
        Token(TokenType.EQUALS, 2, 5, "=="),
        Token(TokenType.MINUS, 2, 6, "-"),
        Token(TokenType.HAT, 2, 8, "^"),
        Token(TokenType.TIMES, 2, 11, "*"),
        Token(TokenType.AND, 2, 18, "&&"),
        Token(TokenType.MODULO, 2, 23, "%"),
        Token(TokenType.MINUS, 2, 28, "-"),
        Token(TokenType.NEQUALS, 2, 31, "!="),
        Token(TokenType.EOF, 2, 31, ""),
    ]

    token_list = list(itertools.chain(*zip(operands, operators)))
    token_list = [
        operands[0],
        operators[0],  # +
        operands[1],
        operators[1],  # *
        operands[2],
        operators[2],  # ==
        operators[3],  # - (unary)
        operands[3],
        operators[4],  # ^
        operands[4],
        operators[5],  # *
        operands[5],
        operators[6],  # &&
        operands[6],
        operators[7],  # %
        operands[7],
        operators[8],  # -
        operands[8],
        operators[9],  # !=
        operands[9],
        operators[10],  # EOF
    ]

    expr_0 = expr.ArithmeticBinary(
        operands[0], operators[0],
        expr.ArithmeticBinary(operands[1], operators[1], operands[2]))

    expr_1 = expr.ArithmeticBinary(
        expr.Unary(
            operators[3],
            expr.ArithmeticBinary(operands[3], operators[4], operands[4])),
        operators[5], operands[5])

    expr_2 = expr.ArithmeticBinary(
        expr.ArithmeticBinary(operands[6], operators[7], operands[7]),
        operators[8], operands[8])
    lhs_ = expr.ArithmeticBinary(expr_0, operators[2], expr_1)
    rhs_ = expr.ArithmeticBinary(expr_2, operators[9], operands[9])
    expected = expr.ArithmeticBinary(lhs_, operators[6], rhs_)

    lexer = parsing.Parser(token_list)
    mocker.patch.object(lexer, "_parse_primary", new=lexer._pop_token)
    result = lexer._parse_precedence_10()

    assert result == expected
