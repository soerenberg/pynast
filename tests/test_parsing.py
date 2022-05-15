"""Tests for parsing module."""
import pytest

from nast import expr
from nast import parsing
from nast import stmt
from nast.tokens import RealValue, Token, TokenType


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
        "args,peek_token,is_at_end,expected",
        [([TokenType.PLUS, TokenType.BANG], Token(TokenType.BANG, 2, 3),
          False, True),
         ([TokenType.BANG, TokenType.PLUS], Token(TokenType.BANG, 1, 1),
          True, False),
         ([TokenType.SEMICOLON, TokenType.AND], Token(TokenType.COLON, 3, 8),
          False, False),
         ([TokenType.OR, TokenType.SEMICOLON], Token(TokenType.COLON, 9, 7),
          True, False)])  # yapf: disable
    def test_check_any(self, lexer, args, peek_token, is_at_end, expected,
                       mocker):
        """Test Parser._check"""
        mocker.patch.object(lexer, "_is_at_end", return_value=is_at_end)
        mocker.patch.object(lexer, "_peek", return_value=peek_token)

        result = lexer._check_any(*args)

        assert result == expected

    def test_check(self, lexer, mocker):
        """Test Parser._check."""
        mocker.patch.object(lexer, "_check_any")
        mocked_ttype = mocker.Mock()

        _ = lexer._check(mocked_ttype)

        lexer._check_any.assert_called_once_with(mocked_ttype)

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

    @pytest.mark.parametrize("token_list,expected", [
        ([
            Token(TokenType.INT, 3, 2),
            Token(TokenType.IDENTIFIER, 3, 7, "myvar"),
            Token(TokenType.SEMICOLON, 3, 12, ";")
        ],
         stmt.Declaration(Token(TokenType.INT, 3, 2),
                          Token(TokenType.IDENTIFIER, 3, 7, "myvar"))),
        ([
            Token(TokenType.REAL, 5, 4),
            Token(TokenType.LABRACK, 5, 9, "<"),
            Token(TokenType.UPPER, 5, 10, "upper"),
            Token(TokenType.ASSIGN, 5, 18, "="),
            Token(TokenType.REALNUMERAL, 5, 18, "2.3", RealValue(2, 3)),
            Token(TokenType.RABRACK, 5, 9, ">"),
            Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
            Token(TokenType.SEMICOLON, 5, 14, ";")
        ],
         stmt.Declaration(
             Token(TokenType.REAL, 5, 4),
             Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
             upper=expr.Literal(
                 Token(TokenType.REALNUMERAL, 5, 18, "2.3", RealValue(2, 3))),
         )),
        ([
            Token(TokenType.REAL, 5, 4),
            Token(TokenType.LABRACK, 5, 9, "<"),
            Token(TokenType.UPPER, 5, 10, "upper"),
            Token(TokenType.ASSIGN, 5, 18, "="),
            Token(TokenType.REALNUMERAL, 5, 18, "2.3", RealValue(2, 3)),
            Token(TokenType.COMMA, 5, 20, ","),
            Token(TokenType.LOWER, 5, 22, "lower"),
            Token(TokenType.ASSIGN, 5, 23, "="),
            Token(TokenType.INTNUMERAL, 5, 18, "-1", RealValue(-1)),
            Token(TokenType.RABRACK, 5, 9, ">"),
            Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
            Token(TokenType.SEMICOLON, 5, 14, ";")
        ],
         stmt.Declaration(
             Token(TokenType.REAL, 5, 4),
             Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
             lower=expr.Literal(
                 Token(TokenType.INTNUMERAL, 5, 18, "-1", RealValue(-1))),
             upper=expr.Literal(
                 Token(TokenType.REALNUMERAL, 5, 18, "2.3", RealValue(2, 3))),
         )),
        ([
            Token(TokenType.REAL, 5, 4),
            Token(TokenType.LABRACK, 5, 9, "<"),
            Token(TokenType.LOWER, 5, 10, "lower"),
            Token(TokenType.ASSIGN, 5, 18, "="),
            Token(TokenType.REALNUMERAL, 5, 18, "-2.3", RealValue(-2, 3)),
            Token(TokenType.COMMA, 5, 20, ","),
            Token(TokenType.UPPER, 5, 22, "upper"),
            Token(TokenType.ASSIGN, 5, 23, "="),
            Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11)),
            Token(TokenType.RABRACK, 5, 9, ">"),
            Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
            Token(TokenType.SEMICOLON, 5, 14, ";")
        ],
         stmt.Declaration(
             Token(TokenType.REAL, 5, 4),
             Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
             lower=expr.Literal(
                 Token(TokenType.REALNUMERAL, 5, 18, "-2.3", RealValue(-2,
                                                                       3))),
             upper=expr.Literal(
                 Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11))),
         )),
        ([
            Token(TokenType.REAL, 5, 4),
            Token(TokenType.LABRACK, 5, 9, "<"),
            Token(TokenType.OFFSET, 5, 10, "offset"),
            Token(TokenType.ASSIGN, 5, 18, "="),
            Token(TokenType.REALNUMERAL, 5, 18, "-2.3", RealValue(-2, 3)),
            Token(TokenType.COMMA, 5, 20, ","),
            Token(TokenType.MULTIPLIER, 5, 22, "multiplier"),
            Token(TokenType.ASSIGN, 5, 23, "="),
            Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11)),
            Token(TokenType.RABRACK, 5, 9, ">"),
            Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
            Token(TokenType.ASSIGN, 5, 25, "="),
            Token(TokenType.REALNUMERAL, 5, 30, "3.14", RealValue(3, 14)),
            Token(TokenType.SEMICOLON, 5, 14, ";")
        ],
         stmt.Declaration(
             Token(TokenType.REAL, 5, 4),
             Token(TokenType.IDENTIFIER, 5, 9, "my_var"),
             offset=expr.Literal(
                 Token(TokenType.REALNUMERAL, 5, 18, "-2.3", RealValue(-2,
                                                                       3))),
             multiplier=expr.Literal(
                 Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11))),
             initializer=expr.Literal(
                 Token(TokenType.REALNUMERAL, 5, 30, "3.14", RealValue(3,
                                                                       14))),
         )),
        ([
            Token(TokenType.VECTOR, 8, 3, "vector"),
            Token(TokenType.LBRACK, 8, 11, "["),
            Token(TokenType.INTNUMERAL, 8, 12, "3", RealValue(3)),
            Token(TokenType.RBRACK, 8, 13, "]"),
            Token(TokenType.IDENTIFIER, 8, 15, "my_var"),
            Token(TokenType.LBRACK, 8, 18, "["),
            Token(TokenType.INTNUMERAL, 8, 22, "3", RealValue(3)),
            Token(TokenType.COMMA, 8, 23, "3", ","),
            Token(TokenType.INTNUMERAL, 8, 27, "3", RealValue(4)),
            Token(TokenType.RBRACK, 8, 33, "]"),
            Token(TokenType.SEMICOLON, 8, 32, ";"),
        ],
         stmt.Declaration(
             Token(TokenType.VECTOR, 8, 3, "vector"),
             Token(TokenType.IDENTIFIER, 8, 15, "my_var"),
             type_dims=[
                 expr.Literal(
                     Token(TokenType.INTNUMERAL, 8, 12, "3", RealValue(3)))
             ],
             array_dims=[
                 expr.Literal(
                     Token(TokenType.INTNUMERAL, 8, 22, "3", RealValue(3))),
                 expr.Literal(
                     Token(TokenType.INTNUMERAL, 8, 27, "4", RealValue(4)))
             ])),
        ([
            Token(TokenType.MATRIX, 8, 3, "matrix"),
            Token(TokenType.LABRACK, 8, 9, "<"),
            Token(TokenType.UPPER, 8, 10, "upper"),
            Token(TokenType.ASSIGN, 8, 18, "="),
            Token(TokenType.REALNUMERAL, 8, 18, "2.3", RealValue(2, 3)),
            Token(TokenType.RABRACK, 8, 9, ">"),
            Token(TokenType.LBRACK, 8, 11, "["),
            Token(TokenType.INTNUMERAL, 8, 12, "3", RealValue(3)),
            Token(TokenType.COMMA, 8, 13, ","),
            Token(TokenType.INTNUMERAL, 8, 14, "4", RealValue(4)),
            Token(TokenType.RBRACK, 8, 15, "]"),
            Token(TokenType.IDENTIFIER, 8, 17, "my_var"),
            Token(TokenType.SEMICOLON, 8, 22, ";"),
        ],
         stmt.Declaration(
             Token(TokenType.MATRIX, 8, 3, "matrix"),
             Token(TokenType.IDENTIFIER, 8, 17, "my_var"),
             type_dims=[
                 expr.Literal(
                     Token(TokenType.INTNUMERAL, 8, 12, "3", RealValue(3))),
                 expr.Literal(
                     Token(TokenType.INTNUMERAL, 8, 14, "4", RealValue(4)))
             ],
             upper=expr.Literal(
                 Token(TokenType.REALNUMERAL, 8, 18, "2.3", RealValue(2,
                                                                      3))))),
    ])
    def test_parse_declaration(self, token_list, expected):
        """Test Parser._parse_declaration."""
        lexer = parsing.Parser(token_list)

        result = lexer._parse_declaration()

        assert result == expected

    @pytest.mark.parametrize("token_list", [
        [
            Token(TokenType.REAL, 5, 4),
            Token(TokenType.LABRACK, 5, 9, "<"),
            Token(TokenType.OFFSET, 5, 10, "offset"),
            Token(TokenType.ASSIGN, 5, 18, "="),
            Token(TokenType.REALNUMERAL, 5, 18, "-2.3", RealValue(-2, 3)),
            Token(TokenType.COMMA, 5, 20, ","),
            Token(TokenType.OFFSET, 5, 22, "offset"),
            Token(TokenType.ASSIGN, 5, 23, "="),
            Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11)),
            Token(TokenType.RABRACK, 5, 9, ">"),
        ],
        [
            Token(TokenType.REAL, 5, 4),
            Token(TokenType.LABRACK, 5, 9, "<"),
            Token(TokenType.LOWER, 5, 10, "lower"),
            Token(TokenType.ASSIGN, 5, 18, "="),
            Token(TokenType.REALNUMERAL, 5, 18, "-2.3", RealValue(-2, 3)),
            Token(TokenType.COMMA, 5, 20, ","),
            Token(TokenType.UPPER, 5, 22, "upper"),
            Token(TokenType.ASSIGN, 5, 23, "="),
            Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11)),
            Token(TokenType.COMMA, 5, 20, ","),
            Token(TokenType.UPPER, 5, 22, "upper"),
            Token(TokenType.ASSIGN, 5, 23, "="),
            Token(TokenType.INTNUMERAL, 5, 18, "11", RealValue(11)),
            Token(TokenType.RABRACK, 5, 9, ">"),
        ],
    ])
    def test_parse_declaration_multiple_modifier_raises(self, token_list):
        """Test that repeating a keyword ('upper', ...) raises ParseError."""
        lexer = parsing.Parser(token_list)
        with pytest.raises(parsing.ParseError):
            _ = lexer._parse_declaration()

    @pytest.mark.parametrize("token_list", [[
        Token(TokenType.REAL, 5, 4),
        Token(TokenType.LABRACK, 5, 9, "<"),
        Token(TokenType.RABRACK, 5, 9, ">"),
    ]])
    def test_parse_declaration_empty_constraints_raises(self, token_list):
        """Test that empty constraints ('int<> name;') raises ParseError."""
        lexer = parsing.Parser(token_list)
        with pytest.raises(parsing.ParseError):
            _ = lexer._parse_declaration()

    @pytest.mark.parametrize("ttype", [TokenType.INT, TokenType.REAL])
    def test_parse_type_dims_0(self, ttype):
        """Test Parser._parse_type_dims for scalar types."""

        lexer = parsing.Parser([])
        expected = []

        result = lexer._parse_type_dims(ttype)

        assert result == expected

    @pytest.mark.parametrize("ttype", [
        TokenType.VECTOR, TokenType.ORDERED, TokenType.POSITIVEORDERED,
        TokenType.SIMPLEX, TokenType.UNITVECTOR, TokenType.ROWVECTOR,
        TokenType.CHOLESKYFACTORCORR, TokenType.CORRMATRIX,
        TokenType.COVMATRIX, TokenType.CHOLESKYFACTORCOV
    ])
    def test_parse_type_dims_1(self, ttype, mocker):
        """Test Parser._parse_type_dims for 1-dim types."""

        token_list = [
            Token(TokenType.LBRACK, 1, 2, "["),
            Token(TokenType.RBRACK, 1, 5, "]"),
        ]

        lexer = parsing.Parser(token_list)
        mocked_expression = mocker.Mock()
        mocker.patch.object(lexer,
                            "_parse_expression",
                            return_value=mocked_expression)
        expected = [mocked_expression]

        result = lexer._parse_type_dims(ttype)

        assert result == expected

    @pytest.mark.parametrize("ttype",
                             [TokenType.MATRIX, TokenType.CHOLESKYFACTORCOV])
    def test_parse_type_dims_2(self, ttype, mocker):
        """Test Parser._parse_type_dims for 2-dim types."""

        token_list = [
            Token(TokenType.LBRACK, 1, 2, "["),
            Token(TokenType.COMMA, 1, 3, ","),
            Token(TokenType.RBRACK, 1, 5, "]"),
        ]

        lexer = parsing.Parser(token_list)
        mocked_expressions = [mocker.Mock(), mocker.Mock()]
        mocker.patch.object(lexer,
                            "_parse_expression",
                            side_effect=mocked_expressions)
        expected = list(mocked_expressions)

        result = lexer._parse_type_dims(ttype)

        assert result == expected

    @pytest.mark.parametrize("token_list,ttype_0,ttype_1", [
        ([Token(TokenType.RETURN, 5, 22, "return")
          ], TokenType.OFFSET, TokenType.MULTIPLIER),
        ([Token(TokenType.RETURN, 5, 22, "return")
          ], TokenType.LOWER, TokenType.UPPER),
    ])
    def test_parse_var_constraint_wrong_keyword_raises(self, token_list,
                                                       ttype_0, ttype_1):
        """Test invalid modifier ('int<foo=..> name;') raises ParseError."""
        lexer = parsing.Parser(token_list)

        with pytest.raises(parsing.ParseError):
            _ = lexer._parse_var_constraints(ttype_0, ttype_1)

    @pytest.mark.parametrize("num_dims", [1, 2, 5])
    def test_parse_array_dims(self, num_dims, mocker):
        """Test Parser._parse_array_dims."""
        token_list = ([Token(TokenType.LBRACK, 1, 2, "[")] + [
            Token(TokenType.COMMA, 1, 8 * i, ",") for i in range(1, num_dims)
        ] + [Token(TokenType.RBRACK, 1, 5, "]")])

        lexer = parsing.Parser(token_list)
        mocked_expressions = [mocker.Mock() for _ in range(num_dims)]
        mocker.patch.object(lexer,
                            "_parse_expression",
                            side_effect=mocked_expressions)
        expected = list(mocked_expressions)

        result = lexer._parse_array_dims()

        assert result == expected

    def test_parse_array_dims_empty_raises(self, mocker):
        """Test that empty array dimensions, e.g., `[]`, raise a ParseError."""
        token_list = [
            Token(TokenType.LBRACK, 1, 2, "["),
            Token(TokenType.RBRACK, 1, 5, "]"),
        ]

        lexer = parsing.Parser(token_list)

        with pytest.raises(parsing.ParseError):
            _ = lexer._parse_array_dims()

    @pytest.mark.parametrize("token_list,expected", [
        ([
            Token(TokenType.IDENTIFIER, 2, 3, "my_var"),
            Token(TokenType.LBRACK, 2, 9, "["),
            Token(TokenType.INTNUMERAL, 2, 10, "3", RealValue(3)),
            Token(TokenType.RBRACK, 2, 11, "]"),
            Token(TokenType.ASSIGN, 2, 14, "="),
            Token(TokenType.REALNUMERAL, 2, 18, "8.1", RealValue(8, 1)),
            Token(TokenType.SEMICOLON, 2, 22, ";"),
        ],
         stmt.Assign(
             expr.Indexing(
                 expr.Variable(Token(TokenType.IDENTIFIER, 2, 3, "my_var")),
                 Token(TokenType.RBRACK, 2, 11, "]"), [
                     expr.Literal(
                         Token(TokenType.INTNUMERAL, 2, 10, "3", RealValue(3)))
                 ]), Token(TokenType.ASSIGN, 2, 14, "="),
             expr.Literal(
                 Token(TokenType.REALNUMERAL, 2, 18, "8.1", RealValue(8,
                                                                      1))))),
        ([
            Token(TokenType.IDENTIFIER, 2, 3, "my_var"),
            Token(TokenType.LBRACK, 2, 9, "["),
            Token(TokenType.INTNUMERAL, 2, 10, "3", RealValue(3)),
            Token(TokenType.RBRACK, 2, 11, "]"),
            Token(TokenType.TILDE, 2, 14, "~"),
            Token(TokenType.IDENTIFIER, 2, 15, "normal"),
            Token(TokenType.LPAREN, 2, 17, "("),
            Token(TokenType.REALNUMERAL, 2, 18, "8.1", RealValue(8, 1)),
            Token(TokenType.COMMA, 2, 20, ","),
            Token(TokenType.INTNUMERAL, 2, 22, "2", RealValue(2)),
            Token(TokenType.RPAREN, 2, 23, ")"),
            Token(TokenType.SEMICOLON, 2, 24, ";"),
        ],
         stmt.Tilde(
             expr.Indexing(
                 expr.Variable(Token(TokenType.IDENTIFIER, 2, 3, "my_var")),
                 Token(TokenType.RBRACK, 2, 11, "]"), [
                     expr.Literal(
                         Token(TokenType.INTNUMERAL, 2, 10, "3", RealValue(3)))
                 ]), Token(TokenType.IDENTIFIER, 2, 15, "normal"), [
                     expr.Literal(
                         Token(TokenType.REALNUMERAL, 2, 18, "8.1",
                               RealValue(8, 1))),
                     expr.Literal(
                         Token(TokenType.INTNUMERAL, 2, 22, "2", RealValue(2)))
                 ])),
        ([
            Token(TokenType.BREAK, 3, 5, "break"),
            Token(TokenType.SEMICOLON, 3, 9, ";")
        ], stmt.Break(Token(TokenType.BREAK, 3, 5, "break"))),
        ([
            Token(TokenType.CONTINUE, 3, 5, "continue"),
            Token(TokenType.SEMICOLON, 3, 9, ";")
        ], stmt.Continue(Token(TokenType.CONTINUE, 3, 5, "continue"))),
        ([
            Token(TokenType.RETURN, 3, 5, "return"),
            Token(TokenType.SEMICOLON, 3, 9, ";")
        ], stmt.Return(Token(TokenType.RETURN, 3, 5, "return"))),
        ([
            Token(TokenType.RETURN, 3, 5, "return"),
            Token(TokenType.INTNUMERAL, 3, 11, "1", RealValue(1)),
            Token(TokenType.SEMICOLON, 3, 12, ";")
        ],
         stmt.Return(
             Token(TokenType.RETURN, 3, 5, "return"),
             expr.Literal(Token(TokenType.INTNUMERAL, 3, 11, "1",
                                RealValue(1))))),
        (
            [
                Token(TokenType.IF, 3, 5, "if"),
                Token(TokenType.LPAREN, 1, 8, "("),
                Token(TokenType.IDENTIFIER, 1, 11, "my_bool"),
                Token(TokenType.RPAREN, 1, 17, ")"),
                Token(TokenType.IDENTIFIER, 2, 3, "my_var"),
                Token(TokenType.ASSIGN, 2, 14, "="),
                Token(TokenType.INTNUMERAL, 2, 18, "1", RealValue(1)),
                Token(TokenType.SEMICOLON, 2, 22, ";"),
                Token(TokenType.EOF, 2, 23, ""),
            ],
            stmt.IfElse(
                expr.Variable(Token(TokenType.IDENTIFIER, 1, 11, "my_bool")),
                stmt.Assign(
                    expr.Variable(Token(TokenType.IDENTIFIER, 2, 3, "my_var")),
                    Token(TokenType.ASSIGN, 2, 14, "="),
                    expr.Literal(
                        Token(TokenType.INTNUMERAL, 2, 18, "1",
                              RealValue(1))))),
        ),
        (
            [
                Token(TokenType.IF, 3, 5, "if"),
                Token(TokenType.LPAREN, 1, 8, "("),
                Token(TokenType.IDENTIFIER, 1, 11, "my_bool"),
                Token(TokenType.RPAREN, 1, 17, ")"),
                Token(TokenType.IDENTIFIER, 2, 3, "my_var"),
                Token(TokenType.ASSIGN, 2, 14, "="),
                Token(TokenType.INTNUMERAL, 2, 18, "1", RealValue(1)),
                Token(TokenType.SEMICOLON, 2, 22, ";"),
                Token(TokenType.ELSE, 3, 3, "else"),
                Token(TokenType.IDENTIFIER, 3, 3, "my_var"),
                Token(TokenType.ASSIGN, 3, 14, "="),
                Token(TokenType.INTNUMERAL, 3, 18, "-1", RealValue(-1)),
                Token(TokenType.SEMICOLON, 3, 22, ";"),
            ],
            stmt.IfElse(
                expr.Variable(Token(TokenType.IDENTIFIER, 1, 11, "my_bool")),
                stmt.Assign(
                    expr.Variable(Token(TokenType.IDENTIFIER, 2, 3, "my_var")),
                    Token(TokenType.ASSIGN, 2, 14, "="),
                    expr.Literal(
                        Token(TokenType.INTNUMERAL, 2, 18, "1",
                              RealValue(1)))),
                stmt.Assign(
                    expr.Variable(Token(TokenType.IDENTIFIER, 3, 3, "my_var")),
                    Token(TokenType.ASSIGN, 3, 14, "="),
                    expr.Literal(
                        Token(TokenType.INTNUMERAL, 3, 18, "-1",
                              RealValue(-1))))),
        ),
        ([
            Token(TokenType.WHILE, 3, 5, "while"),
            Token(TokenType.LPAREN, 1, 8, "("),
            Token(TokenType.IDENTIFIER, 1, 11, "my_bool"),
            Token(TokenType.RPAREN, 1, 17, ")"),
            Token(TokenType.IDENTIFIER, 2, 3, "my_var"),
            Token(TokenType.ASSIGN, 2, 14, "="),
            Token(TokenType.INTNUMERAL, 2, 18, "1", RealValue(1)),
            Token(TokenType.SEMICOLON, 2, 22, ";")
        ],
         stmt.While(
             expr.Variable(Token(TokenType.IDENTIFIER, 1, 11, "my_bool")),
             stmt.Assign(
                 expr.Variable(Token(TokenType.IDENTIFIER, 2, 3, "my_var")),
                 Token(TokenType.ASSIGN, 2, 14, "="),
                 expr.Literal(
                     Token(TokenType.INTNUMERAL, 2, 18, "1", RealValue(1)))))),
        ([
            Token(TokenType.PRINT, 3, 5, "print"),
            Token(TokenType.LPAREN, 1, 8, "("),
            Token(TokenType.IDENTIFIER, 1, 11, "var_0"),
            Token(TokenType.COMMA, 1, 13, ","),
            Token(TokenType.IDENTIFIER, 1, 16, "var_1"),
            Token(TokenType.RPAREN, 1, 17, ")"),
            Token(TokenType.SEMICOLON, 1, 22, ";")
        ],
         stmt.Print([
             expr.Variable(Token(TokenType.IDENTIFIER, 1, 11, "var_0")),
             expr.Variable(Token(TokenType.IDENTIFIER, 1, 16, "var_1")),
         ])),
        ([
            Token(TokenType.REJECT, 3, 5, "reject"),
            Token(TokenType.LPAREN, 1, 8, "("),
            Token(TokenType.IDENTIFIER, 1, 11, "var_0"),
            Token(TokenType.COMMA, 1, 13, ","),
            Token(TokenType.IDENTIFIER, 1, 16, "var_1"),
            Token(TokenType.RPAREN, 1, 17, ")"),
            Token(TokenType.SEMICOLON, 1, 22, ";")
        ],
         stmt.Reject([
             expr.Variable(Token(TokenType.IDENTIFIER, 1, 11, "var_0")),
             expr.Variable(Token(TokenType.IDENTIFIER, 1, 16, "var_1")),
         ])),
        ([
            Token(TokenType.TARGET, 7, 3, "target"),
            Token(TokenType.PLUSASSIGN, 7, 9, "+="),
            Token(TokenType.REALNUMERAL, 7, 14, "0.12", RealValue(0, 12)),
            Token(TokenType.SEMICOLON, 7, 22, ";"),
        ],
         stmt.TargetPlusAssign(
             expr.Literal(
                 Token(TokenType.REALNUMERAL, 7, 14, "0.12", RealValue(0,
                                                                       12))))),
    ])
    def test_parse_statement(self, token_list, expected):
        """Test Parser._parse_statement."""
        lexer = parsing.Parser(token_list)

        result = lexer._parse_statement()

        assert result == expected
