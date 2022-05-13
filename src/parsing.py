"""Stan parser."""
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Tuple
from tokens import Token, TokenType

import expr
import stmt

# Data types that with no dimensions
SCALAR_VAR_TYPES = [
    TokenType.INT,
    TokenType.REAL,
]

# Data types that with one dimension
ONE_DIM_VAR_TYPES = [
    TokenType.VECTOR,
    TokenType.ORDERED,
    TokenType.POSITIVEORDERED,
    TokenType.SIMPLEX,
    TokenType.UNITVECTOR,
    TokenType.ROWVECTOR,
    TokenType.CHOLESKYFACTORCORR,
    TokenType.CORRMATRIX,
    TokenType.COVMATRIX,
]

# Data types that with two dimensions
TWO_DIM_VAR_TYPES = [TokenType.MATRIX]

# Data types that with one or two dimensions
OPT_TWO_DIM_VAR_TYPES = [TokenType.CHOLESKYFACTORCOV]

# All data types
VAR_TYPES = (SCALAR_VAR_TYPES + ONE_DIM_VAR_TYPES + TWO_DIM_VAR_TYPES +
             OPT_TWO_DIM_VAR_TYPES)

# Data types that may have upper/lower constraints.
LOWER_UPPER_CONSTRAINT_VAR_TYPES = [
    TokenType.INT,
    TokenType.REAL,
    TokenType.VECTOR,
    TokenType.ROWVECTOR,
    TokenType.MATRIX,
]

# Data types that may have offset/multiplier constraints.
OFFSET_MULTIPLIER_CONSTRAINT_VAR_TYPES = [
    TokenType.REAL,
    TokenType.VECTOR,
    TokenType.ROWVECTOR,
    TokenType.MATRIX,
]


class ParseError(Exception):
    """Parse exception."""

    def __init__(self, token: Token, message: str):
        super().__init__(f"In line {token.line}: {message}")


class VarConstraints(NamedTuple):
    lower: Optional[expr.Expr] = None
    upper: Optional[expr.Expr] = None
    offset: Optional[expr.Expr] = None
    multiplier: Optional[expr.Expr] = None


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

    def _check_any(self, *args: TokenType) -> bool:
        """Check if current token has 1 of given TokenTypes, but not consume."""
        if self._is_at_end():
            return False

        return self._peek().ttype in args

    def _check(self, ttype: TokenType) -> bool:
        """Check if current token has TokenType, but not consume."""
        return self._check_any(ttype)

    def _match_any(self, *args: TokenType) -> bool:
        """Check if current has one of given TokenTypes, consume if it does."""
        for ttype in args:
            if self._check(ttype):
                self._pop_token()
                return True
        return False

    def _match(self, ttype: TokenType) -> bool:
        """Check if current has TokenType, and consume if it does."""
        return self._match_any(ttype)

    def _consume(self,
                 ttype: TokenType,
                 message: Optional[str] = None) -> Token:
        """Consume token of required type or raise error."""
        if self._check(ttype):
            return self._pop_token()

        raise ParseError(self._get_current(), message or f"Expected {ttype}.")

    def _parse_expression(self) -> expr.Expr:
        # <expression> ::= <lhs>
        #        | <non_lhs>
        return self._parse_precedence_10()

    def _parse_precedence_10(self) -> expr.Expr:
        """Precedence level 10.

        `?~:` conditional op, ternary infix, right associative.
        """
        # According to the Stan manual
        # a ? b : c ? d : e    is equivalent to   a ? b : (c ? d : e)
        # It is also implied that
        # a ? b ? c : d : e   is equivalent to   a ? (b ? c : d) : e
        expression = self._parse_precedence_9()

        while self._match(TokenType.QMARK):
            left_operator = self._previous()
            middle = self._parse_precedence_10()
            right_operator = self._consume(TokenType.COLON)
            right = self._parse_precedence_10()

            expression = expr.Ternary(expression, left_operator, middle,
                                      right_operator, right)

        return expression

    def _parse_precedence_9(self) -> expr.Expr:
        """Precedence level 9.

        `||` logical or, binary infix, left associative.
        """
        expression = self._parse_precedence_8()

        while self._match(TokenType.OR):
            operator = self._previous()
            right = self._parse_precedence_8()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_8(self) -> expr.Expr:
        """Precedence level 8.

        `&&` logical and, binary infix, left associative.
        """
        expression = self._parse_precedence_7()

        while self._match(TokenType.AND):
            operator = self._previous()
            right = self._parse_precedence_7()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_7(self) -> expr.Expr:
        """Precedence level 7.

        `==' equality, binary infix, left associative,
        `!=' inequality, binary infix, left associative.
        """
        expression = self._parse_precedence_6()

        while self._match_any(TokenType.EQUALS, TokenType.NEQUALS):
            operator = self._previous()
            right = self._parse_precedence_6()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

    def _parse_precedence_6(self) -> expr.Expr:
        """Precedence level 6.

        `<` less than, binary infix, left associative,
        `<=` less than or equal, binary infix, left associative,
        `>` greater than, binary infix, left associative,
        `>=` greater than or equal, binary infix, left associative.
        """
        expression = self._parse_precedence_5()

        while self._match_any(TokenType.LABRACK, TokenType.LEQ,
                              TokenType.RABRACK, TokenType.GEQ):
            operator = self._previous()
            right = self._parse_precedence_5()
            expression = expr.ArithmeticBinary(expression, operator, right)

        return expression

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
        expression = self._parse_primary()

        if self._match(TokenType.LPAREN):
            expression = self._complete_function_application(expression)
        elif self._check(TokenType.LBRACK):
            while self._match(TokenType.LBRACK):
                expression = self._complete_indexing(expression)

        return expression

    def _complete_function_application(
            self, callee: expr.Expr) -> expr.FunctionApplication:
        """Finish parsing FunctionApplication.

        At this point it is assumed that callee and opening parenthesis have
        been consumed.
        """
        arguments = []
        if not self._check(TokenType.RPAREN):
            arguments.append(self._parse_expression())

            while self._match(TokenType.COMMA):
                arguments.append(self._parse_expression())

        paren = self._consume(TokenType.RPAREN, "Expect ')' after arguments.")

        return expr.FunctionApplication(callee, paren, arguments)

    def _complete_indexing(self, callee: expr.Expr) -> expr.Indexing:
        """Finish parsing Indexing.

        At this point it is assumed that callee and opening brackets have
        been consumed.
        """
        indices = []
        if not self._check(TokenType.RBRACK):
            expression = self._parse_slice()
            indices.append(expression)

            while self._match(TokenType.COMMA):
                expression = self._parse_slice()
                indices.append(expression)

        paren = self._consume(TokenType.RBRACK, "Expect ']' after indices.")

        return expr.Indexing(callee, paren, indices)

    def _parse_slice(self) -> expr.Expr:
        """Parse slice."""
        expression = self._parse_expression()
        if self._match(TokenType.COLON):
            right = self._parse_expression()
            expression = expr.Slice(left=expression, right=right)
        return expression

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
            return expr.Variable(self._previous())

        raise ParseError(self._get_current(), "")

    def _parse_declaration(self) -> stmt.Stmt:
        dtype = self._pop_token()
        var_constraints = self._parse_lower_upper_offset_multiplier(dtype)
        type_dims = self._parse_type_dims(dtype.ttype)
        identifier = self._consume(TokenType.IDENTIFIER,
                                   "Expect identifier in declaration.")

        # TODO parse 'dims' here

        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after declaration.")

        return stmt.Declaration(dtype=dtype,
                                identifier=identifier,
                                type_dims=type_dims,
                                initializer=initializer,
                                **var_constraints._asdict())

    def _parse_type_dims(self, ttype: TokenType) -> List[expr.Expr]:
        type_dims = []
        if ttype in ONE_DIM_VAR_TYPES:
            self._consume(TokenType.LBRACK, "Expected '['.")
            type_dims.append(self._parse_expression())
            self._consume(TokenType.RBRACK, "Expected ']'.")
        elif ttype in TWO_DIM_VAR_TYPES:
            self._consume(TokenType.LBRACK, "Expected '['.")
            type_dims.append(self._parse_expression())
            self._consume(TokenType.COMMA, "Expected ','.")
            type_dims.append(self._parse_expression())
            self._consume(TokenType.RBRACK, "Expected ']'.")
        elif ttype in OPT_TWO_DIM_VAR_TYPES:
            self._consume(TokenType.LBRACK, "Expected '['.")
            type_dims.append(self._parse_expression())
            if self._match(TokenType.COMMA):
                type_dims.append(self._parse_expression())
            self._consume(TokenType.RBRACK, "Expected ']'.")

        return type_dims

    def _parse_array_dims(self) -> List[expr.Expr]:
        array_dims = []

        if self._match(TokenType.LBRACK):
            while True:
                array_dims.append(self._parse_expression())

                if not self._match(TokenType.COMMA):
                    break

            self._consume(TokenType.RBRACK,
                          "Expected ']' after array dimensions.")

        return array_dims

    def _parse_lower_upper_offset_multiplier(self,
                                             dtype: Token) -> VarConstraints:
        kwargs: Dict[str, Optional[expr.Expr]] = dict(lower=None,
                                                      upper=None,
                                                      offset=None,
                                                      multiplier=None)
        if self._match(TokenType.LABRACK):
            if (self._check_any(TokenType.OFFSET, TokenType.MULTIPLIER)
                    and dtype.ttype in OFFSET_MULTIPLIER_CONSTRAINT_VAR_TYPES):
                kwargs |= self._parse_var_constraints(TokenType.OFFSET,
                                                      TokenType.MULTIPLIER)
            elif (self._check_any(TokenType.LOWER, TokenType.UPPER)
                  and dtype.ttype in LOWER_UPPER_CONSTRAINT_VAR_TYPES):
                kwargs |= self._parse_var_constraints(TokenType.LOWER,
                                                      TokenType.UPPER)
            else:
                expected_keywords = ', '.join([
                    ttype.name.lower() for ttype in [
                        TokenType.MULTIPLIER, TokenType.OFFSET,
                        TokenType.LOWER, TokenType.UPPER
                    ]
                ])
                raise ParseError(self._get_current(),
                                 f"Expected {expected_keywords}.")

            self._consume(TokenType.RABRACK,
                          "Expect '>' after var constraints.")

        return VarConstraints(**kwargs)

    def _parse_var_constraints(
            self, ttype_0: TokenType,
            ttype_1: TokenType) -> Mapping[str, Optional[expr.Expr]]:
        constraints: Dict[str, Optional[expr.Expr]] = {
            ttype_0.name.lower(): None,
            ttype_1.name.lower(): None
        }

        while True:
            if not self._match_any(ttype_0, ttype_1):
                raise ParseError(
                    self._get_current(), f"Expected '{ttype_0.name.lower()}' "
                    f"or '{ttype_1.name.lower()}', but found "
                    f"'{self._get_current().lexeme}'.")
            modifier = self._previous()
            name = modifier.ttype.name.lower()

            self._consume(TokenType.ASSIGN, f"Expect '=' after {name}.")

            if constraints[name] is not None:
                raise ParseError(modifier, f"Multiple definition of {name}.")
            constraints[name] = self._parse_precedence_5()

            if not self._match(TokenType.COMMA):
                break

        return constraints
