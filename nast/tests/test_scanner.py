"""Tests for scanner.py module."""
import pytest

import scanner
from tokens import Token, TokenType, ComplexValue, RealValue

# pylint: disable=no-self-use, protected-access, too-few-public-methods

ONE_CHAR_EOF = Token(TokenType.EOF, 1, 2, "")
TWO_CHAR_EOF = Token(TokenType.EOF, 1, 3, "")
THREE_CHAR_EOF = Token(TokenType.EOF, 1, 4, "")


@pytest.mark.functional
@pytest.mark.parametrize("source,expected_tokens", [
    ("\n", [
        Token(TokenType.EOF, 2, 1, ""),
    ]),
    (" ", [ONE_CHAR_EOF]),
    ("{", [Token(TokenType.LBRACE, 1, 1, "{"), ONE_CHAR_EOF]),
    ("}", [Token(TokenType.RBRACE, 1, 1, "}"), ONE_CHAR_EOF]),
    ("(", [Token(TokenType.LPAREN, 1, 1, "("), ONE_CHAR_EOF]),
    (")", [Token(TokenType.RPAREN, 1, 1, ")"), ONE_CHAR_EOF]),
    ("[", [Token(TokenType.LBRACK, 1, 1, "["), ONE_CHAR_EOF]),
    ("]", [Token(TokenType.RBRACK, 1, 1, "]"), ONE_CHAR_EOF]),
    ("<", [Token(TokenType.LABRACK, 1, 1, "<"), ONE_CHAR_EOF]),
    (">", [Token(TokenType.RABRACK, 1, 1, ">"), ONE_CHAR_EOF]),
    (",", [Token(TokenType.COMMA, 1, 1, ","), ONE_CHAR_EOF]),
    (";", [Token(TokenType.SEMICOLON, 1, 1, ";"), ONE_CHAR_EOF]),
    ("|", [Token(TokenType.BAR, 1, 1, "|"), ONE_CHAR_EOF]),
    ("?", [Token(TokenType.QMARK, 1, 1, "?"), ONE_CHAR_EOF]),
    (":", [Token(TokenType.COLON, 1, 1, ":"), ONE_CHAR_EOF]),
    ("!", [Token(TokenType.BANG, 1, 1, "!"), ONE_CHAR_EOF]),
    ("-", [Token(TokenType.MINUS, 1, 1, "-"), ONE_CHAR_EOF]),
    ("+", [Token(TokenType.PLUS, 1, 1, "+"), ONE_CHAR_EOF]),
    ("^", [Token(TokenType.HAT, 1, 1, "^"), ONE_CHAR_EOF]),
    ("'", [Token(TokenType.TRANSPOSE, 1, 1, "'"), ONE_CHAR_EOF]),
    ("*", [Token(TokenType.TIMES, 1, 1, "*"), ONE_CHAR_EOF]),
    ("/", [Token(TokenType.DIVIDE, 1, 1, "/"), ONE_CHAR_EOF]),
    ("%", [Token(TokenType.MODULO, 1, 1, "%"), ONE_CHAR_EOF]),
    ("%/%", [Token(TokenType.IDIVIDE, 1, 1, "%/%"), THREE_CHAR_EOF]),
    ("\\", [Token(TokenType.LDIVIDE, 1, 1, "\\"), ONE_CHAR_EOF]),
    (".*", [Token(TokenType.ELTTIMES, 1, 1, ".*"), TWO_CHAR_EOF]),
    (".^", [Token(TokenType.ELTPOW, 1, 1, ".^"), TWO_CHAR_EOF]),
    ("./", [Token(TokenType.ELTDIVIDE, 1, 1, "./"), TWO_CHAR_EOF]),
    ("||", [Token(TokenType.OR, 1, 1, "||"), TWO_CHAR_EOF]),
    ("&&", [Token(TokenType.AND, 1, 1, "&&"), TWO_CHAR_EOF]),
    ("==", [Token(TokenType.EQUALS, 1, 1, "=="), TWO_CHAR_EOF]),
    ("!=", [Token(TokenType.NEQUALS, 1, 1, "!="), TWO_CHAR_EOF]),
    ("<=", [Token(TokenType.LEQ, 1, 1, "<="), TWO_CHAR_EOF]),
    (">=", [Token(TokenType.GEQ, 1, 1, ">="), TWO_CHAR_EOF]),
    ("~", [Token(TokenType.TILDE, 1, 1, "~"), ONE_CHAR_EOF]),
    ("=", [Token(TokenType.ASSIGN, 1, 1, "="), ONE_CHAR_EOF]),
    ("+=", [Token(TokenType.PLUSASSIGN, 1, 1, "+="), TWO_CHAR_EOF]),
    ("-=", [Token(TokenType.MINUSASSIGN, 1, 1, "-="), TWO_CHAR_EOF]),
    ("*=", [Token(TokenType.TIMESASSIGN, 1, 1, "*="), TWO_CHAR_EOF]),
    ("/=", [Token(TokenType.DIVIDEASSIGN, 1, 1, "/="), TWO_CHAR_EOF]),
    (".*=", [Token(TokenType.ELTTIMESASSIGN, 1, 1, ".*="), THREE_CHAR_EOF]),
    ("./=", [Token(TokenType.ELTDIVIDEASSIGN, 1, 1, "./="), THREE_CHAR_EOF]),
    ("<-", [Token(TokenType.ARROWASSIGN, 1, 1, "<-"), TWO_CHAR_EOF]),
    ("\t\n  // a comment \n \n", [
        Token(TokenType.EOF, 4, 1, ""),
    ]),
    ("\"abc\"", [
        Token(TokenType.STRING, 1, 1, "\"abc\"", "abc"),
        Token(TokenType.EOF, 1, 6, ""),
    ]),
    ("\"ab c\"  // another comment", [
        Token(TokenType.STRING, 1, 1, "\"ab c\"", "ab c"),
        Token(TokenType.EOF, 1, 27, ""),
    ]),
    ("= == =  ==", [
        Token(TokenType.ASSIGN, 1, 1, "="),
        Token(TokenType.EQUALS, 1, 3, "=="),
        Token(TokenType.ASSIGN, 1, 6, "="),
        Token(TokenType.EQUALS, 1, 9, "=="),
        Token(TokenType.EOF, 1, 11, ""),
    ]),
    (" \"abc\"", [
        Token(TokenType.STRING, 1, 2, "\"abc\"", "abc"),
        Token(TokenType.EOF, 1, 7, ""),
    ]),
    ("model \n {// some comment\n}", [
        Token(TokenType.MODELBLOCK, 1, 1, "model"),
        Token(TokenType.LBRACE, 2, 2, "{"),
        Token(TokenType.RBRACE, 3, 1, "}"),
        Token(TokenType.EOF, 3, 2, ""),
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


@pytest.mark.functional
@pytest.mark.parametrize("keyword,token_type", [
    ("functions", TokenType.FUNCTIONBLOCK),
    ("data", TokenType.DATABLOCK),
    ("transformed data", TokenType.TRANSFORMEDDATABLOCK),
    ("parameters", TokenType.PARAMETERSBLOCK),
    ("transformed parameters", TokenType.TRANSFORMEDPARAMETERSBLOCK),
    ("model", TokenType.MODELBLOCK),
    ("generated quantities", TokenType.GENERATEDQUANTITIESBLOCK),
    ("return", TokenType.RETURN),
    ("if", TokenType.IF),
    ("else", TokenType.ELSE),
    ("while", TokenType.WHILE),
    ("profile", TokenType.PROFILE),
    ("for", TokenType.FOR),
    ("in", TokenType.IN),
    ("break", TokenType.BREAK),
    ("continue", TokenType.CONTINUE),
    ("void", TokenType.VOID),
    ("int", TokenType.INT),
    ("real", TokenType.REAL),
    ("complex", TokenType.COMPLEX),
    ("vector", TokenType.VECTOR),
    ("row_vector", TokenType.ROWVECTOR),
    ("array", TokenType.ARRAY),
    ("matrix", TokenType.MATRIX),
    ("ordered", TokenType.ORDERED),
    ("positive_ordered", TokenType.POSITIVEORDERED),
    ("simplex", TokenType.SIMPLEX),
    ("unit_vector", TokenType.UNITVECTOR),
    ("cholesky_factor_corr", TokenType.CHOLESKYFACTORCORR),
    ("cholesky_factor_cov", TokenType.CHOLESKYFACTORCOV),
    ("corr_matrix", TokenType.CORRMATRIX),
    ("cov_matrix", TokenType.COVMATRIX),
    ("lower", TokenType.LOWER),
    ("upper", TokenType.UPPER),
    ("offset", TokenType.OFFSET),
    ("multiplier", TokenType.MULTIPLIER),
    ("increment_log_prob", TokenType.INCREMENTLOGPROB),
    ("print", TokenType.PRINT),
    ("reject", TokenType.REJECT),
    ("identifiername", TokenType.IDENTIFIER),
    ("identifier_name", TokenType.IDENTIFIER),
    ("identifier_name", TokenType.IDENTIFIER),
])
def test_scan_source_keyword(keyword, token_type):
    """Simple functional test for scanning reserved keywords.

    This test is similar to `test_scan_source` but simplifies the setup
    slightly for reserved keywords.
    """
    source = keyword
    eof_token = Token(TokenType.EOF, 1, len(keyword) + 1, "")
    expected_tokens = [Token(token_type, 1, 1, keyword), eof_token]

    # GIVEN a source code and a Scanner instance
    lexer = scanner.Scanner(source)

    # WHEN tokens are scanned
    lexer.scan_tokens()

    # THEN the scanned list of tokens is as expected
    assert lexer._tokens == expected_tokens


@pytest.mark.functional
@pytest.mark.parametrize("keyword,token_type,literal", [
    ("0", TokenType.INTNUMERAL, 0),
    ("123", TokenType.INTNUMERAL, 123),
    ("2.0", TokenType.REALNUMERAL, RealValue(2, 0, 1)),
    ("1.3", TokenType.REALNUMERAL, RealValue(1, 3, 1)),
    ("10.4e2", TokenType.REALNUMERAL, RealValue(10, 4, 2)),
    ("10.42E12", TokenType.REALNUMERAL, RealValue(10, 42, 12)),
    ("123i", TokenType.IMAGNUMERAL, ComplexValue(RealValue(123, 0, 1))),
    ("1.3i", TokenType.IMAGNUMERAL, ComplexValue(RealValue(1, 3, 1))),
    ("10.4e2i", TokenType.IMAGNUMERAL, ComplexValue(RealValue(10, 4, 2))),
])
def test_scan_literal(keyword, token_type, literal):
    """Simple functional test for scanning reserved keywords.

    This test is similar to `test_scan_source` but simplifies the setup
    slightly for reserved keywords.
    """
    source = keyword
    eof_token = Token(TokenType.EOF, 1, len(keyword) + 1, "")
    expected_tokens = [Token(token_type, 1, 1, keyword, literal), eof_token]

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
    ("_", True, False),
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
