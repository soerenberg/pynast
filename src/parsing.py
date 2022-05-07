"""Stan parser."""
from typing import Any, List
from tokens import Token, TokenType

import expr


class ParseError(Exception):
    """Parse exception."""

    def __init__(self, token: Token, message: str):
        super().__init__(f"In line {token.line}: {message}")


class Parser:
    """Stan parser."""

    def __init__(self, token_list: List[Token]):
        self._token_list = list(token_list)
        self._current = 0

    def parse(self) -> List[Any]:
        """Run parser."""
        result = []

        while not self._is_at_end():
            self._pop_token()
            result.append(None)

        return result

    def _pop_token(self):
        token = self._peek()

        if not self._is_at_end():
            self._current += 1

        return token

    def _is_at_end(self) -> bool:
        """Check if EOF encountered yet."""
        return self._peek().ttype == TokenType.EOF

    def _peek(self) -> Token:
        """Peek at current element."""
        return self._token_list[self._current]

    def _get_current(self) -> Token:
        """Return current token."""
        return self._token_list[self._current]

    def _previous(self) -> Token:
        """Return previous token."""
        return self._token_list[self._current - 1]

    def _check(self, ttype: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().ttype == ttype

    def _match_any(self, *args) -> bool:
        for ttype in args:
            if self._check(ttype):
                self._pop_token()
                return True
        return False

    def _match(self, ttype: TokenType) -> bool:
        """Short form for _match_any with only one argument."""
        return self._match_any(ttype)

    def _consume(self, ttype: TokenType) -> Token:
        """Consume token of required type or raise error."""
        if self._check(ttype):
            return self._pop_token()

        raise ParseError(self._get_current(), "Expected {ttype}.")

    def _parse_unary(self) -> expr.Unary:
        if self._match_any(TokenType.BANG, TokenType.MINUS, TokenType.PLUS,
                           TokenType.HAT):
            operator = self._previous()

            right = self._parse_unary()

            return expr.Unary(operator, right)

        raise ParseError(self._peek(), "Expect '!', '-', '+' or '^'.")

    def _parse_expression(self) -> expr.Expr:
        # <expression> ::= <lhs>
        #        | <non_lhs>

        # TODO implement parsing <non_lhs>
        return self._parse_lhs()

    def _parse_lhs(self):
        # <lhs> ::= <identifier>
        # | <lhs> LBRACK <indexes> RBRACK

        # Due to left-recursivity transformed to:
        # <lhs> ::= <identifier> (LBRACK <indexes> RBRACK)*

        if not self._check(TokenType.IDENTIFIER):
            raise ParseError(self._get_current(),
                             "Expect identifier or lhs expression.")
        identifier = self._pop_token()

        indexes = []
        while self._match(TokenType.LBRACK):
            indexes.append(self._parse_indexes())
            self._consume(TokenType.RBRACK)

        return expr.Variable(identifier, indexes)

    def _parse_indexes(self) -> expr.Indexes:
        # <indexes> ::= epsilon
        #     | COLON
        #     | <expression>
        #     | <expression> COLON
        #     | COLON <expression>
        #     | <expression> COLON <expression>
        #     | <indexes> COMMA <indexes>

        # TODO only ':' is allowed at the moment.
        self._consume(TokenType.COLON)
        return expr.Indexes([expr.Range(None, None)])


    def _parse_precedence_5(self) -> expr.Expr:
        """Precedence level 5.

        `+` addition, binary infix, left associative,
        `-` subtraction, binary infix, left associative.
        """
        expression = self._parse_precedence_4()

        while self._match_any(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            right = self._parse_precedence_4()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_4(self) -> expr.Expr:
        """Precedence level 4.

        `*` multiplication, binary infix, left associative,
        `/` (right) division, binary infix, left associative,
        `%` modulus, binary infix, left associative.
        """
        expression = self._parse_precedence_3()

        while self._match_any(TokenType.TIMES, TokenType.DIVIDE,
                              TokenType.MODULO):
            operator = self._previous()
            right = self._parse_precedence_3()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_3(self) -> expr.Expr:
        """Precedence level 3.

        `\` left division, binary infix, left associative.
        """
        expression = self._parse_precedence_2()

        while self._match(TokenType.LDIVIDE):
            operator = self._previous()
            right = self._parse_precedence_2()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_2(self) -> expr.Expr:
        """Precedence level 2.

        `.*` elementwise multiplication, binary infix, left associative,
        `./` elementwise division, binary infix, left associative.
        """
        expression = self._parse_precedence_1()

        while self._match_any(TokenType.ELTTIMES, TokenType.ELTDIVIDE):
            operator = self._previous()
            right = self._parse_precedence_1()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_1(self) -> expr.Expr:
        """Precedence level 1. Unary prefix operators `!`, `-` and `+`."""
        if self._match_any(TokenType.BANG, TokenType.MINUS, TokenType.PLUS):
            operator = self._previous()
            right = self._parse_precedence_1()
            return expr.Unary(operator, right)
        return self._parse_precedence_0_5()

    def _parse_precedence_0_5(self) -> expr.Expr:
        """Precedence level 0.5.

        Binary infix `^`, right associative.
        """
        expression = self._parse_precedence_0()

        while self._match(TokenType.HAT):
            operator = self._previous()
            right = self._parse_precedence_0_5()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_0(self) -> expr.Expr:
        """Precedence level 0.

        Unary postfix `'` (transposition),
        `()`  (function application),
        `[]`  (array, matrix indexing).
        """
        # TODO implement `()` and `[]`
        return self._parse_primary()

    def _parse_primary(self) -> expr.Expr:
        # TODO only literals can parsed atm. False, True etc. missing.
        literal_ttypes = [
            TokenType.STRING, TokenType.INTNUMERAL, TokenType.REALNUMERAL,
            TokenType.IMAGNUMERAL
        ]
        if any(self._check(ttype) for ttype in literal_ttypes):
            return expr.Literal(self._pop_token())

        if self._match(TokenType.IDENTIFIER):
            # TODO handle indexing
            return expr.Variable(self._previous(), None)

        raise ParseError(self._get_current(), "")
