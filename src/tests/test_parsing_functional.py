"""Functional tests for parsing.py module."""
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
