"""Tests for parsing module."""
import pytest

import expr
import parsing
from tokens import Token, TokenType


class TestParser:
    """Tests for parsing.Parser."""

    # pylint: disable=no-self-use, protected-access, too-many-arguments

    @pytest.fixture(name="lexer")
    def lexer_fixture(self, mocker):
        """Scanner instance."""
        lexer = parsing.Parser(mocker.MagicMock())
        yield lexer

    @pytest.mark.parametrize("current,expected", [(0, 1), (10, 11), (25, 26)])
    def test_pop_token_increments(self, lexer, current, expected, mocker):
        """Test that _pop_token increases _current if not _is_at_end = True."""
        lexer._current = current
        mocker.patch.object(lexer, "_peek")
        mocker.patch.object(lexer, "_is_at_end", return_value=False)

        lexer._pop_token()

        assert lexer._current == expected

    @pytest.mark.parametrize("current,expected", [(0, 0), (10, 10), (25, 25)])
    def test_pop_token_not_increments(self, lexer, current, expected, mocker):
        """Test that _pop_token increases _current if not _is_at_end = True."""
        lexer._current = current
        mocker.patch.object(lexer, "_peek")
        mocker.patch.object(lexer, "_is_at_end", return_value=True)

        lexer._pop_token()

        assert lexer._current == expected

    @pytest.mark.parametrize(
        "ttype,peek_token,is_at_end,expected",
        [(TokenType.BANG, Token(TokenType.BANG, 2, 3), False, True),
         (TokenType.BANG, Token(TokenType.BANG, 1, 1), True, False),
         (TokenType.SEMICOLON, Token(TokenType.COLON, 3, 8), False, False),
         (TokenType.SEMICOLON, Token(TokenType.COLON, 9, 7), True, False)])
    def test_check(self, lexer, ttype, peek_token, is_at_end, expected,
                   mocker):
        """Test Scanner._check"""
        mocker.patch.object(lexer, "_is_at_end", return_value=is_at_end)
        mocker.patch.object(lexer, "_peek", return_value=peek_token)

        result = lexer._check(ttype)

        assert result == expected

    @pytest.mark.parametrize(
        "ttypes,check_ttype,expected",
        [([], TokenType.TIMES, False),
         ([TokenType.BANG, TokenType.PLUS, TokenType.MINUS
           ], TokenType.BANG, True),
         ([TokenType.BANG, TokenType.PLUS, TokenType.MINUS
           ], TokenType.MINUS, True),
         ([TokenType.BANG, TokenType.PLUS, TokenType.MINUS
           ], TokenType.TIMES, False)])
    def test_match_any(self, lexer, ttypes, check_ttype, expected, mocker):
        """Test Parser._match_any."""
        mocker.patch.object(lexer, "_check", new=lambda x: x == check_ttype)
        mocker.patch.object(lexer, "_pop_token")

        result = lexer._match_any(*ttypes)

        assert result == expected

    def test_match(self, lexer, mocker):
        """Test Parser._match."""
        mocked_return_value = mocker.MagicMock()
        mocker.patch.object(lexer,
                            "_match_any",
                            return_value=mocked_return_value)

        mocked_ttype = mocker.MagicMock()
        result = lexer._match(mocked_ttype)

        lexer._match_any.assert_called_once_with(mocked_ttype)
        assert result is mocked_return_value

    @pytest.mark.parametrize("token_list,current,ttype,expected_index", [
        ([Token(TokenType.BANG, 1, 1), Token(TokenType.EOF, 1, 2)], 0,
         TokenType.BANG, 0),
        ([Token(TokenType.BANG, 1, 1), Token(TokenType.SEMICOLON, 1, 2),
          Token(TokenType.EOF, 1, 3)], 1, TokenType.SEMICOLON, 1),
    ])  # yapf: disable
    def test_consume(self, token_list, current, ttype, expected_index):
        """Test Parser._consume."""
        lexer = parsing.Parser(token_list)
        lexer._current = current

        result = lexer._consume(ttype)

        assert result is token_list[expected_index]

    @pytest.mark.parametrize(
        "token_list,current,ttype,message,expected_message,expected_index", [
            ([Token(TokenType.BANG, 1, 1),
              Token(TokenType.EOF, 1, 2)
              ], 0, TokenType.MINUS, None, r"Expected TokenType.MINUS.", 0),
            ([
                Token(TokenType.BANG, 1, 1),
                Token(TokenType.SEMICOLON, 1, 2),
                Token(TokenType.EOF, 1, 3)
            ], 2, TokenType.SEMICOLON, "some message", r"some message", 1),
        ])
    def test_consume_raises(self, token_list, current, ttype, message,
                            expected_message, expected_index):
        """Test Parser._consume."""
        lexer = parsing.Parser(token_list)
        lexer._current = current

        with pytest.raises(parsing.ParseError, match=expected_message):
            _ = lexer._consume(ttype, message)

    @pytest.mark.parametrize("ttype,lexeme,left_associative", [
        (TokenType.OR, "||", True),
        (TokenType.AND, "||", True),
        (TokenType.EQUALS, "==", True),
        (TokenType.NEQUALS, "!=", True),
        (TokenType.LABRACK, "<", True),
        (TokenType.LEQ, "<=", True),
        (TokenType.RABRACK, ">", True),
        (TokenType.GEQ, ">=", True),
        (TokenType.OR, "||", True),
        (TokenType.PLUS, "+", True),
        (TokenType.MINUS, "-", True),
        (TokenType.TIMES, "*", True),
        (TokenType.DIVIDE, "/", True),
        (TokenType.MODULO, "%", True),
        (TokenType.LDIVIDE, "\\", True),
        (TokenType.ELTTIMES, ".*", True),
        (TokenType.ELTTIMES, ".*", True),
        (TokenType.HAT, "^", False),
    ])
    def test_binary_op(self, ttype, lexeme, left_associative, mocker):
        """Test binary operation.

        This is a simple test to test arithmetic or logical operations and
        their associativity. E.g. for a left associative binary op `#` we
        perform a test that an expression of the form
            (a # b) # c,
        is parsed correctly. For right associative binary we use
            a # (b # c).
        """
        operator_left = Token(ttype, 2, 3, lexeme)
        operator_right = Token(ttype, 2, 7, lexeme)

        left = mocker.Mock()
        middle = mocker.Mock()
        right = mocker.Mock()

        if left_associative:
            expected = expr.ArithmeticBinary(
                expr.ArithmeticBinary(left, operator_left, middle),
                operator_right, right)
        else:
            expected = expr.ArithmeticBinary(
                left, operator_left,
                expr.ArithmeticBinary(middle, operator_right, right))

        token_list = [
            left,
            operator_left,
            middle,
            operator_right,
            right,
            Token(TokenType.IDENTIFIER, 2, 8, "abc"),
        ]
        lexer = parsing.Parser(token_list)
        mocker.patch.object(lexer, "_parse_primary", new=lexer._pop_token)

        result = lexer._parse_precedence_10()

        assert result == expected

    @pytest.mark.parametrize("token_list,expected", [
        ([
            Token(TokenType.BANG, 1, 1, "!"),
            Token(TokenType.STRING, 1, 2, "abc"),
            Token(TokenType.EOF, 1, 5, ""),
        ],
         expr.Unary(Token(TokenType.BANG, 1, 1, "!"),
                    expr.Literal(Token(TokenType.STRING, 1, 2, "abc")))),
        ([
            Token(TokenType.BANG, 1, 1, "!"),
            Token(TokenType.BANG, 1, 2, "!"),
            Token(TokenType.IDENTIFIER, 1, 3, "foo"),
            Token(TokenType.EOF, 1, 6, ""),
        ],
         expr.Unary(
             Token(TokenType.BANG, 1, 1, "!"),
             expr.Unary(
                 Token(TokenType.BANG, 1, 2, "!"),
                 expr.Variable(Token(TokenType.IDENTIFIER, 1, 3, "foo"))))),
    ])
    def test_parse_precedence_1(self, token_list, expected):
        """Test Parser._parse_precedence_1."""
        lexer = parsing.Parser(token_list)

        result = lexer._parse_precedence_1()

        assert result == expected

    def test_parse_function_application(self):
        """Test parsing function call of the form Identifier(arg0,arg1)."""
        token_list = [
            Token(TokenType.IDENTIFIER, 5, 2, "my_func"),
            Token(TokenType.LPAREN, 5, 10, "("),
            Token(TokenType.IDENTIFIER, 5, 16, "my_var"),
            Token(TokenType.COMMA, 5, 23, ","),
            Token(TokenType.IDENTIFIER, 5, 24, "some_other_var"),
            Token(TokenType.RPAREN, 5, 40, ")"),
        ]

        expected = expr.FunctionApplication(
            callee=expr.Variable(Token(TokenType.IDENTIFIER, 5, 2, "my_func")),
            closing_paren=Token(TokenType.RPAREN, 5, 40, ")"),
            arguments=[
                expr.Variable(Token(TokenType.IDENTIFIER, 5, 16, "my_var")),
                expr.Variable(
                    Token(TokenType.IDENTIFIER, 5, 24, "some_other_var")),
            ])

        lexer = parsing.Parser(token_list)

        result = lexer._parse_precedence_0()

        assert result == expected

    def test_parse_indexing(self):
        """Test parsing indexing of the form <identifier>[a,b][c,d:e]."""
        token_list = [
            Token(TokenType.IDENTIFIER, 5, 2, "my_func"),
            Token(TokenType.LBRACK, 5, 10, "["),
            Token(TokenType.IDENTIFIER, 5, 16, "var_0"),
            Token(TokenType.COMMA, 5, 23, ","),
            Token(TokenType.IDENTIFIER, 5, 24, "var_1"),
            Token(TokenType.RBRACK, 5, 40, "]"),
            Token(TokenType.LBRACK, 5, 41, "["),
            Token(TokenType.IDENTIFIER, 5, 42, "var_2"),
            Token(TokenType.COMMA, 5, 48, ","),
            Token(TokenType.IDENTIFIER, 5, 50, "var_3"),
            Token(TokenType.COLON, 5, 51, ":"),
            Token(TokenType.IDENTIFIER, 5, 53, "var_4"),
            Token(TokenType.RBRACK, 5, 61, "]"),
            Token(TokenType.EQUALS, 5, 63, "="),
        ]

        first_indexing = expr.Indexing(
            callee=expr.Variable(Token(TokenType.IDENTIFIER, 5, 2, "my_func")),
            closing_bracket=Token(TokenType.RBRACK, 5, 40, "]"),
            indices=[
                expr.Variable(Token(TokenType.IDENTIFIER, 5, 16, "var_0")),
                expr.Variable(Token(TokenType.IDENTIFIER, 5, 24, "var_1")),
            ])
        expected = expr.Indexing(
            callee=first_indexing,
            closing_bracket=Token(TokenType.RBRACK, 5, 61, "]"),
            indices=[
                expr.Variable(Token(TokenType.IDENTIFIER, 5, 42, "var_2")),
                expr.Slice(
                    expr.Variable(Token(TokenType.IDENTIFIER, 5, 50, "var_3")),
                    expr.Variable(Token(TokenType.IDENTIFIER, 5, 53,
                                        "var_4"))),
            ])

        lexer = parsing.Parser(token_list)

        result = lexer._parse_precedence_0()

        assert result == expected

    @pytest.mark.parametrize("token_list,expected", [
        ([
            Token(TokenType.STRING, 2, 3, "abc"),
            Token(TokenType.EOF, 2, 4, "")
        ], expr.Literal(Token(TokenType.STRING, 2, 3, "abc"))),
        ([
            Token(TokenType.INTNUMERAL, 2, 3, "7"),
            Token(TokenType.EOF, 2, 4, "")
        ], expr.Literal(Token(TokenType.INTNUMERAL, 2, 3, "7"))),
        ([
            Token(TokenType.IDENTIFIER, 5, 2, "my_var"),
            Token(TokenType.EOF, 5, 3, "")
        ], expr.Variable(Token(TokenType.IDENTIFIER, 5, 2, "my_var"))),
    ])
    def test_parse_primary(self, token_list, expected):
        """Test Parser._parse_primary."""
        lexer = parsing.Parser(token_list)

        result = lexer._parse_precedence_0_5()

        assert result == expected
