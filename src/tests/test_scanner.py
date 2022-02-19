"""Tests for scanner.py module."""
import pytest

import scanner

# pylint: disable=protected-access

ONE_CHAR_EOF = scanner.Token(scanner.TokenType.EOF, 1, 2, "")

@pytest.mark.functional
@pytest.mark.parametrize("source,expected_tokens", [
    ("\n", [
        scanner.Token(scanner.TokenType.NEWLINE, 1, 1, "\n"), 
        scanner.Token(scanner.TokenType.EOF, 2, 1, ""),
    ]),
    (" ", [scanner.Token(scanner.TokenType.SPACE, 1, 1, " "), ONE_CHAR_EOF]),
    ("{", [scanner.Token(scanner.TokenType.LBRACE, 1, 1, "{"), ONE_CHAR_EOF]),
    ("}", [scanner.Token(scanner.TokenType.RBRACE, 1, 1, "}"), ONE_CHAR_EOF]),
    ("(", [scanner.Token(scanner.TokenType.LPAREN, 1, 1, "("), ONE_CHAR_EOF]),
    (")", [scanner.Token(scanner.TokenType.RPAREN, 1, 1, ")"), ONE_CHAR_EOF]),
    ("[", [scanner.Token(scanner.TokenType.LBRACK, 1, 1, "["), ONE_CHAR_EOF]),
    ("]", [scanner.Token(scanner.TokenType.RBRACK, 1, 1, "]"), ONE_CHAR_EOF]),
    ("<", [scanner.Token(scanner.TokenType.LABRACK, 1, 1, "<"), ONE_CHAR_EOF]),
    (">", [scanner.Token(scanner.TokenType.RABRACK, 1, 1, ">"), ONE_CHAR_EOF]),
    ("\t\n  \n \n", [
        scanner.Token(scanner.TokenType.SPACE, 1, 1, "\t"),
        scanner.Token(scanner.TokenType.NEWLINE, 1, 2, "\n"),
        scanner.Token(scanner.TokenType.SPACE, 2, 1, " "),
        scanner.Token(scanner.TokenType.SPACE, 2, 2, " "),
        scanner.Token(scanner.TokenType.NEWLINE, 2, 3, "\n"),
        scanner.Token(scanner.TokenType.SPACE, 3, 1, " "),
        scanner.Token(scanner.TokenType.NEWLINE, 3, 2, "\n"),
        scanner.Token(scanner.TokenType.EOF, 4, 1, ""),
    ]),
    ("\"abc\"", [
        scanner.Token(scanner.TokenType.STRING, 1, 1, "\"abc\"", "abc"),
        scanner.Token(scanner.TokenType.EOF, 1, 2, ""),
    ]),
    (" \"abc\"", [
        scanner.Token(scanner.TokenType.SPACE, 1, 1, " "),
        scanner.Token(scanner.TokenType.STRING, 1, 2, "\"abc\"", "abc"),
        scanner.Token(scanner.TokenType.EOF, 1, 3, ""),
    ]),
])
def test_scan_source(source, expected_tokens):
    """Functional test to test source code snippets."""
    # GIVEN a source code and a Scanner instance
    lexer = scanner.Scanner(source)

    # WHEN tokens are scanned
    lexer.scan_tokens()

    # THEN the scanned list of tokens is as expected
    assert lexer._tokens == expected_tokens


@pytest.mark.parametrize("char,expected", [(" ", True), ("a", True),
                                           ("8", True), ("#", True),
                                           ("\n", False), ("\r", False),
                                           ("\"", False)])
def test_is_valid_string_literal(char, expected):
    """Test scanner.is_valid_string_literal_char."""
    result = scanner.is_valid_string_literal_char(char)

    assert result == expected
