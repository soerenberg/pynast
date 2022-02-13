"""Tests for scanner.py module."""
import pytest

import scanner

# pylint: disable=protected-access


@pytest.mark.functional
@pytest.mark.parametrize("source,expected_tokens", [
    (" ", [
        scanner.Token(scanner.TokenType.SPACE, 1, 1, " "),
        scanner.Token(scanner.TokenType.EOF, 1, 2, "")
    ]),
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
    ("\"abc\"",
     [scanner.Token(scanner.TokenType.STRING, 1, 1, "\"abc\"", "abc")]),
    (" \"abc\"", [
        scanner.Token(scanner.TokenType.SPACE, 1, 1, " "),
        scanner.Token(scanner.TokenType.STRING, 1, 2, "\"abc\"", "abc")
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
