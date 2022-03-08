"""Tests for parsing module."""
import pytest

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

    @pytest.mark.parametrize("token_list,current,ttype,expected_index", [
        ([Token(TokenType.BANG, 1, 1), Token(TokenType.EOF, 1, 2)], 0,
         TokenType.MINUS, 0),
        ([Token(TokenType.BANG, 1, 1), Token(TokenType.SEMICOLON, 1, 2),
          Token(TokenType.EOF, 1, 3)], 2, TokenType.SEMICOLON, 1),
    ])  # yapf: disable
    def test_consume_raises(self, token_list, current, ttype, expected_index):
        """Test Parser._consume."""
        lexer = parsing.Parser(token_list)
        lexer._current = current

        with pytest.raises(parsing.ParseError):
            _ = lexer._consume(ttype)
