"""Tests for scanner.py module."""
import pytest

import scanner

# pylint: disable=no-self-use, protected-access, too-few-public-methods

ONE_CHAR_EOF = scanner.Token(scanner.TokenType.EOF, 1, 2, "")
TWO_CHAR_EOF = scanner.Token(scanner.TokenType.EOF, 1, 3, "")
THREE_CHAR_EOF = scanner.Token(scanner.TokenType.EOF, 1, 4, "")


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
    (",", [scanner.Token(scanner.TokenType.COMMA, 1, 1, ","), ONE_CHAR_EOF]),
    (";",
     [scanner.Token(scanner.TokenType.SEMICOLON, 1, 1, ";"), ONE_CHAR_EOF]),
    ("|", [scanner.Token(scanner.TokenType.BAR, 1, 1, "|"), ONE_CHAR_EOF]),
    ("?", [scanner.Token(scanner.TokenType.QMARK, 1, 1, "?"), ONE_CHAR_EOF]),
    (":", [scanner.Token(scanner.TokenType.COLON, 1, 1, ":"), ONE_CHAR_EOF]),
    ("!", [scanner.Token(scanner.TokenType.BANG, 1, 1, "!"), ONE_CHAR_EOF]),
    ("-", [scanner.Token(scanner.TokenType.MINUS, 1, 1, "-"), ONE_CHAR_EOF]),
    ("+", [scanner.Token(scanner.TokenType.PLUS, 1, 1, "+"), ONE_CHAR_EOF]),
    ("^", [scanner.Token(scanner.TokenType.HAT, 1, 1, "^"), ONE_CHAR_EOF]),
    ("'",
     [scanner.Token(scanner.TokenType.TRANSPOSE, 1, 1, "'"), ONE_CHAR_EOF]),
    ("*", [scanner.Token(scanner.TokenType.TIMES, 1, 1, "*"), ONE_CHAR_EOF]),
    ("/", [scanner.Token(scanner.TokenType.DIVIDE, 1, 1, "/"), ONE_CHAR_EOF]),
    ("%", [scanner.Token(scanner.TokenType.MODULO, 1, 1, "%"), ONE_CHAR_EOF]),
    ("%/%",
     [scanner.Token(scanner.TokenType.IDIVIDE, 1, 1, "%/%"), THREE_CHAR_EOF]),
    ("\\",
     [scanner.Token(scanner.TokenType.LDIVIDE, 1, 1, "\\"), ONE_CHAR_EOF]),
    (".*",
     [scanner.Token(scanner.TokenType.ELTTIMES, 1, 1, ".*"), TWO_CHAR_EOF]),
    (".^", [scanner.Token(scanner.TokenType.ELTPOW, 1, 1, ".^"), TWO_CHAR_EOF
            ]),
    ("./",
     [scanner.Token(scanner.TokenType.ELTDIVIDE, 1, 1, "./"), TWO_CHAR_EOF]),
    ("||", [scanner.Token(scanner.TokenType.OR, 1, 1, "||"), TWO_CHAR_EOF]),
    ("&&", [scanner.Token(scanner.TokenType.AND, 1, 1, "&&"), TWO_CHAR_EOF]),
    ("==", [scanner.Token(scanner.TokenType.EQUALS, 1, 1, "=="), TWO_CHAR_EOF
            ]),
    ("!=",
     [scanner.Token(scanner.TokenType.NEQUALS, 1, 1, "!="), TWO_CHAR_EOF]),
    ("<=", [scanner.Token(scanner.TokenType.LEQ, 1, 1, "<="), TWO_CHAR_EOF]),
    (">=", [scanner.Token(scanner.TokenType.GEQ, 1, 1, ">="), TWO_CHAR_EOF]),
    ("~", [scanner.Token(scanner.TokenType.TILDE, 1, 1, "~"), ONE_CHAR_EOF]),
    ("=", [scanner.Token(scanner.TokenType.ASSIGN, 1, 1, "="), ONE_CHAR_EOF]),
    ("+=",
     [scanner.Token(scanner.TokenType.PLUSASSIGN, 1, 1, "+="), TWO_CHAR_EOF]),
    ("-=",
     [scanner.Token(scanner.TokenType.MINUSASSIGN, 1, 1, "-="), TWO_CHAR_EOF]),
    ("*=",
     [scanner.Token(scanner.TokenType.TIMESASSIGN, 1, 1, "*="), TWO_CHAR_EOF]),
    ("/=", [
        scanner.Token(scanner.TokenType.DIVIDEASSIGN, 1, 1, "/="), TWO_CHAR_EOF
    ]),
    (".*=", [
        scanner.Token(scanner.TokenType.ELTTIMESASSIGN, 1, 1, ".*="),
        THREE_CHAR_EOF
    ]),
    ("./=", [
        scanner.Token(scanner.TokenType.ELTDIVIDEASSIGN, 1, 1, "./="),
        THREE_CHAR_EOF
    ]),
    ("<-",
     [scanner.Token(scanner.TokenType.ARROWASSIGN, 1, 1, "<-"), TWO_CHAR_EOF]),
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
        scanner.Token(scanner.TokenType.EOF, 1, 6, ""),
    ]),
    ("= == =  ==", [
        scanner.Token(scanner.TokenType.ASSIGN, 1, 1, "="),
        scanner.Token(scanner.TokenType.SPACE, 1, 2, " "),
        scanner.Token(scanner.TokenType.EQUALS, 1, 3, "=="),
        scanner.Token(scanner.TokenType.SPACE, 1, 5, " "),
        scanner.Token(scanner.TokenType.ASSIGN, 1, 6, "="),
        scanner.Token(scanner.TokenType.SPACE, 1, 7, " "),
        scanner.Token(scanner.TokenType.SPACE, 1, 8, " "),
        scanner.Token(scanner.TokenType.EQUALS, 1, 9, "=="),
        scanner.Token(scanner.TokenType.EOF, 1, 11, ""),
    ]),
    (" \"abc\"", [
        scanner.Token(scanner.TokenType.SPACE, 1, 1, " "),
        scanner.Token(scanner.TokenType.STRING, 1, 2, "\"abc\"", "abc"),
        scanner.Token(scanner.TokenType.EOF, 1, 7, ""),
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


class TestScanner:
    """Tests for scanner.Scanner"""

    @pytest.mark.parametrize("source,num_pops,offset,expected", [
        ("", 0, 0, True),
        ("", 0, 1, True),
        ("x", 0, 0, False),
        ("x", 1, 0, True),
        ("x", 0, 1, True),
        ("abcde", 3, 1, False),
        ("abcde", 3, 2, True),
    ])
    def test_is_at_end(self, source, num_pops, offset, expected):
        """Test _is_at_end."""
        # GIVEN a Scanner instance...
        scnnr = scanner.Scanner(source)

        # ... where `num_pops` characters have been advanced
        for _ in range(num_pops):
            scnnr._pop_char()

        # WHEN _is_at_end is called
        result = scnnr._is_at_end(offset)

        # THEN the result is as expected
        assert result == expected


@pytest.mark.parametrize("char,expected", [(" ", True), ("a", True),
                                           ("8", True), ("#", True),
                                           ("\n", False), ("\r", False),
                                           ("\"", False)])
def test_is_valid_string_literal(char, expected):
    """Test scanner.is_valid_string_literal_char."""
    result = scanner.is_valid_string_literal_char(char)

    assert result == expected


@pytest.mark.parametrize("char,is_first_char,expected", [
    ("a", True, True),
    ("a", False, True),
    ("u", True, True),
    ("u", False, True),
    ("_", True, True),
    ("_", False, True),
    (" ", True, False),
    (" ", False, False),
    ("2", True, False),
    ("2", False, True),
])
def test_is_identifier_char(char, is_first_char, expected):
    """Test scanner.is_identifier_char."""
    result = scanner.is_identifier_char(char, is_first_char)

    assert result == expected
