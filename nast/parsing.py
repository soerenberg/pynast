"""Stan parser."""
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Tuple, Union

from nast import expr
from nast import stmt
from nast.tokens import Token, TokenType

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

BASIC_TYPES = [
    TokenType.INT,
    TokenType.REAL,
    TokenType.COMPLEX,
    TokenType.VECTOR,
    TokenType.ROWVECTOR,
    TokenType.MATRIX,
]

# Types that can have literal values in the code
LITERAL_TYPES = [
    TokenType.STRING, TokenType.INTNUMERAL, TokenType.REALNUMERAL,
    TokenType.IMAGNUMERAL
]

RETURN_TYPE_TTYPES = [TokenType.VOID, TokenType.ARRAY] + BASIC_TYPES

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

ASSIGNMENT_OPS = [
    TokenType.ASSIGN,
    TokenType.ARROWASSIGN,
    TokenType.PLUSASSIGN,
    TokenType.MINUSASSIGN,
    TokenType.TIMESASSIGN,
    TokenType.DIVIDEASSIGN,
    TokenType.ELTTIMESASSIGN,
    TokenType.ELTDIVIDEASSIGN,
]


class ParseError(Exception):
    """Parse exception."""

    def __init__(self, token: Token, message: str):
        super().__init__(f"In line {token.line}: {message}")


class VarConstraints(NamedTuple):
    """Constraints for variable declarations."""
    lower: Optional[expr.Expr] = None
    upper: Optional[expr.Expr] = None
    offset: Optional[expr.Expr] = None
    multiplier: Optional[expr.Expr] = None


class Parser:
    """Stan parser."""

    # pylint: disable=too-few-public-methods

    def __init__(self, token_list: List[Token]):
        self._token_list = list(token_list)
        self._current = 0

    def parse(self) -> List[Any]:
        """Run parser."""
        raise NotImplementedError

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

    def _consume_any(self,
                     ttypes: List[TokenType],
                     message: Optional[str] = None) -> Token:
        """Consume token of required type or raise error."""
        if self._check_any(*ttypes):
            return self._pop_token()

        raise ParseError(
            self._get_current(), message
            or f"Expected {','.join([str(x) for x in ttypes])}.")

    def _consume(self,
                 ttype: TokenType,
                 message: Optional[str] = None) -> Token:
        """Consume token of required type or raise error."""
        return self._consume_any([ttype], message=message)

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
        r"""Precedence level 3.

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
        self, callee: expr.Expr
    ) -> Union[expr.FunctionApplication, expr.FunctionConditionalApplication]:
        """Finish parsing FunctionApplication.

        At this point it is assumed that callee and opening parenthesis have
        been consumed.
        """
        arguments = []
        outcome = None  # for conditional calls, e.g. `normal_pdf(x |a,b);'
        if not self._check(TokenType.RPAREN):
            arguments.append(self._parse_expression())

            if self._match(TokenType.BAR):
                outcome = arguments[0]
                arguments = []

                if not self._check(TokenType.RPAREN):
                    arguments.append(self._parse_expression())

            while self._match(TokenType.COMMA):
                arguments.append(self._parse_expression())

        paren = self._consume(TokenType.RPAREN, "Expect ')' after arguments.")

        if outcome is not None:
            return expr.FunctionConditionalApplication(callee, outcome,
                                                       arguments)

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
        if self._check_any(*LITERAL_TYPES):
            return expr.Literal(self._pop_token())

        if self._match(TokenType.LPAREN):
            inner = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')'.")
            return expr.Parenthesis(inner)

        if self._match(TokenType.IDENTIFIER):
            return expr.Variable(self._previous())

        raise ParseError(self._get_current(), "")

    def _parse_declaration(self) -> stmt.Declaration:
        """Parse variable declaration.

        It is assumed that the type has already been consumed in the previous
        token.
        """
        dtype = self._previous()
        var_constraints = self._parse_lower_upper_offset_multiplier(dtype)
        type_dims = self._parse_type_dims(dtype.ttype)
        identifier = self._consume(TokenType.IDENTIFIER,
                                   "Expect identifier in declaration.")

        array_dims = self._parse_array_dims()

        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after declaration.")

        return stmt.Declaration(dtype=dtype,
                                identifier=identifier,
                                type_dims=type_dims,
                                array_dims=array_dims,
                                initializer=initializer,
                                **var_constraints._asdict())

    def _parse_declaration_no_assign(
            self, error_msg_if_init: str) -> stmt.Declaration:
        """Parse variable declaration, do not allow assignment.

        It is assumed that the type has already been consumed in the previous
        token.

        Args:
            error_msg_if_init: error message that will be raised as a
                ParseError if an initializer was given.

        Raises:
            ParseError: if initializer was given.
        """
        declaration = self._parse_declaration()
        if declaration.initializer is not None:
            raise ParseError(declaration.identifier, error_msg_if_init)
        return declaration

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

    def _parse_statement(self) -> stmt.Stmt:
        if self._match(TokenType.BREAK):
            keyword = self._previous()
            self._consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
            return stmt.Break(keyword)
        if self._match(TokenType.CONTINUE):
            keyword = self._previous()
            self._consume(TokenType.SEMICOLON, "Expect ';' after 'continue'.")
            return stmt.Continue(keyword)
        if self._match(TokenType.RETURN):
            keyword = self._previous()
            value = None
            if not self._match(TokenType.SEMICOLON):
                value = self._parse_expression()
                self._consume(TokenType.SEMICOLON,
                              "Expect ';' after return value.")
            return stmt.Return(keyword, value)
        if self._match(TokenType.IF):
            self._consume(TokenType.LPAREN, "Expect '(' after 'if'.")
            condition = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expect ')' after condition.")
            consequent = self._parse_statement()
            alternative = None
            if self._match(TokenType.ELSE):
                alternative = self._parse_statement()
            return stmt.IfElse(condition, consequent, alternative)
        if self._match(TokenType.WHILE):
            self._consume(TokenType.LPAREN, "Expect '(' after 'while'.")
            condition = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expect ')' after condition.")
            body = self._parse_statement()
            return stmt.While(condition, body)
        if self._match(TokenType.FOR):
            self._consume(TokenType.LPAREN, "Expect '(' after 'for'.")
            identifier = self._consume(TokenType.IDENTIFIER,
                                       "Expect identifier after '('.")
            self._consume(TokenType.IN, "Expect 'in' after identifier.")
            begin = self._parse_expression()
            self._consume(TokenType.COLON, "Expect ':' after expression.")
            end = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expect ')'.")
            body = self._parse_statement()
            return stmt.For(identifier, begin, end, body)
        if self._match(TokenType.PRINT):
            self._consume(TokenType.LPAREN, "Expect '(' after 'print'.")
            expressions = [self._parse_expression()]

            while self._match(TokenType.COMMA):
                expressions.append(self._parse_expression())

            self._consume(TokenType.RPAREN, "Expect ')' after expression.")
            self._consume(TokenType.SEMICOLON, "Expect ';' after statement.")
            return stmt.Print(expressions)
        if self._match(TokenType.REJECT):
            self._consume(TokenType.LPAREN, "Expect '(' after 'reject'.")
            expressions = [self._parse_expression()]

            while self._match(TokenType.COMMA):
                expressions.append(self._parse_expression())

            self._consume(TokenType.RPAREN, "Expect ')' after expression.")
            self._consume(TokenType.SEMICOLON, "Expect ';' after statement.")
            return stmt.Reject(expressions)
        if self._match(TokenType.TARGET):
            self._consume(TokenType.PLUSASSIGN)
            expression = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
            return stmt.TargetPlusAssign(expression)
        if self._match(TokenType.LBRACE):
            return self._parse_block()
        if self._match(TokenType.SEMICOLON):
            return stmt.Empty(self._previous())

        expression = self._parse_expression()

        if self._match_any(*ASSIGNMENT_OPS):
            assignment_op = self._previous()
            value = self._parse_expression()
            self._consume(TokenType.SEMICOLON, "Expect ';' after assignment.")

            return stmt.Assign(expression, assignment_op, value)

        self._consume(TokenType.TILDE, "Invalid statement.")
        identifier = self._consume(TokenType.IDENTIFIER,
                                   "Expect identifier after '~'.")
        self._consume(TokenType.LPAREN, "Expect '('.")
        args = []
        while True:
            args.append(self._parse_expression())
            if not self._match(TokenType.COMMA):
                break
        self._consume(TokenType.RPAREN, "Expect ')'.")

        # TODO parse truncation here
        self._consume(TokenType.SEMICOLON, "Expect ';'.")

        return stmt.Tilde(expression, identifier, args)

    def _parse_block(self) -> stmt.Block:
        """Parse block. It is assumed that opening brace has been consumed."""
        declarations: List[stmt.Declaration] = []
        while self._match_any(*VAR_TYPES):
            declarations.append(self._parse_declaration())

        statements = []
        while not self._match(TokenType.RBRACE):
            statements.append(self._parse_statement())

        return stmt.Block(declarations, statements)

    def _parse_function_declaration_or_definition(
            self) -> Union[stmt.FunctionDeclaration, stmt.FunctionDefinition]:
        """Parse custom function declaration or definition. """
        return_dtype = self._parse_return_type_declaration()

        identifier = self._consume(TokenType.IDENTIFIER,
                                   "Expect identifier for function name.")

        self._consume(TokenType.LPAREN, "Expect '(' after function name.")

        args = self._parse_function_declaration_arguments()

        self._consume(TokenType.RPAREN, "Expect ')'.")

        function_declaration = stmt.FunctionDeclaration(
            return_dtype, identifier, args)

        if self._match(TokenType.SEMICOLON):
            return function_declaration

        self._consume(TokenType.LBRACE, "Expect '{'.")
        body = self._parse_block()

        return stmt.FunctionDefinition(header=function_declaration, body=body)

    def _parse_function_declaration_arguments(
            self) -> List[stmt.ArgumentDeclaration]:
        args: List[stmt.ArgumentDeclaration] = []
        if not self._check(TokenType.RPAREN):
            args.append(self._parse_argument_declaration())
            while self._match(TokenType.COMMA):
                args.append(self._parse_argument_declaration())
        return args

    def _parse_return_type_declaration(self) -> stmt.ReturnTypeDeclaration:
        return stmt.ReturnTypeDeclaration(*self._parse_function_type())

    def _parse_function_type(self) -> Tuple[TokenType, int]:
        """Parse return or argument type for custom functions.

        Types occurring as return type or argument types are more restricted
        than types of, say, parameters.

        Returns:
            TokenType: Data type (e.g. TokenType.INT).
            int: number of (unsized) array dimensions, where `0` means scalar
                (non-array) values.
        """
        dtype = self._pop_token()
        if dtype.ttype not in RETURN_TYPE_TTYPES:
            raise ParseError(dtype, f"Invalid type {dtype}.")

        n_dims = 0

        if dtype.ttype == TokenType.ARRAY:
            self._consume(TokenType.LBRACK, "Expect '[' after 'array'.")
            n_dims = 1

            while self._match(TokenType.COMMA):
                n_dims += 1

            self._consume(TokenType.RBRACK, "Expect ']'.")

            dtype = self._consume_any(BASIC_TYPES, "Expect basic type.")
        elif self._match(TokenType.LBRACK):
            n_dims = 1

            while self._match(TokenType.COMMA):
                n_dims += 1

            self._consume(TokenType.RBRACK, "Expect ']'.")

        return dtype.ttype, n_dims

    def _parse_argument_declaration(self) -> stmt.ArgumentDeclaration:
        """Parse argument (type and identifier name) of custom functions.

        Types occurring as return type or argument types are more restricted
        than types of, say, parameters.

        Returns:
            TokenType: Data type (e.g. TokenType.INT).
            int: number of (unsized) array dimensions, where `0` means scalar
                (non-array) values.
            Token: identifier token for the argument name.
        """
        dtype, n_dims = self._parse_function_type()
        identifier = self._consume(TokenType.IDENTIFIER,
                                   "Expect argument name.")
        return stmt.ArgumentDeclaration(dtype, n_dims, identifier)

    def parse_program(self) -> stmt.Program:
        """Parse stan program."""
        functions = None
        data = None
        transformed_data = None
        parameters = None
        transformed_parameters = None
        model = None
        generated_quantities = None

        # TODO: distinguish between <top_vardecl_or_statement> and
        # <vardecl_or_statement> (see Stan BNF grammar).
        if self._match(TokenType.FUNCTIONBLOCK):
            functions = self._parse_function_block()
        if self._match(TokenType.DATABLOCK):
            data = self._parse_var_declaration_no_assign_block()
        if self._match(TokenType.TRANSFORMEDDATABLOCK):
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'transformed data'.")
            transformed_data = self._parse_block()
        if self._match(TokenType.PARAMETERSBLOCK):
            parameters = self._parse_var_declaration_no_assign_block()
        if self._match(TokenType.TRANSFORMEDPARAMETERSBLOCK):
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'transformed parameters'.")
            transformed_parameters = self._parse_block()
        if self._match(TokenType.MODELBLOCK):
            self._consume(TokenType.LBRACE, "Expect '{' after 'model'.")
            model = self._parse_block()
        if self._match(TokenType.GENERATEDQUANTITIESBLOCK):
            self._consume(TokenType.LBRACE,
                          "Expect '{' after 'generated quantities'.")
            generated_quantities = self._parse_block()

        return stmt.Program(
            functions=functions,
            data=data,
            transformed_data=transformed_data,
            parameters=parameters,
            transformed_parameters=transformed_parameters,
            model=model,
            generated_quantities=generated_quantities,
        )

    def _parse_function_block(self) -> stmt.Block:
        """Parse function block. It is assumed that 'function' is consumed."""
        self._consume(TokenType.LBRACE, "Expect '{' after 'functions'.")
        statements = []
        while not self._match(TokenType.RBRACE):
            statements.append(self._parse_function_declaration_or_definition())

        return stmt.Block([], statements)

    def _parse_var_declaration_no_assign_block(self):
        """Parse program block with variable declarations, no assigns only.

        This is the case for the 'data' and 'parameters' block in stan.
        It is assumed that 'data' or 'parameters' has already been consumed.
        """
        block_name = self._previous().ttype.name
        self._consume(TokenType.LBRACE, f"Expect '{{' after {block_name}.")
        declarations = []
        while not self._match(TokenType.RBRACE):
            self._consume_any(VAR_TYPES, "Expected type.")
            declarations.append(
                self._parse_declaration_no_assign(
                    f"Assigments not allowed in {block_name} block."))

        return stmt.Block(declarations, [])
