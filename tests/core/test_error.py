"""Tests for error.py module."""
import re

import pytest

from nast.core import error
from nast.core import scanner


@pytest.mark.parametrize("line,column,message,expected_msg", [
    (2, 3, "lipsum", "[line 2, column 3]: lipsum"),
    (12, 23, "lorem", "[line 12, column 23]: lorem"),
])
def test_throw_at(line, column, message, expected_msg):
    """Test error.throw_at."""
    with pytest.raises(RuntimeError, match=re.escape(expected_msg)):
        error.throw_at(line, column, message)


@pytest.mark.parametrize("token,message", [
    (scanner.Token(scanner.TokenType.STRING, 2, 3, "", None), "lipsum"),
    (scanner.Token(scanner.TokenType.SPACE, 12, 23, "", None), "lorem"),
])
def test_throw_token(token, message, mocker):
    """Test error.throw_token."""
    mocker.patch.object(error, "throw_at")
    error.throw_token(token, message)
    error.throw_at.assert_called_once_with(token.line, token.column, message)
