"""Scan stan code."""
from typing import Any, List

import error
from tokens import Token, TokenType

# Reserved keywords mapped to corresponding token type
STAN_KEYWORDS = {
    "functions": TokenType.FUNCTIONBLOCK,
    "data": TokenType.DATABLOCK,
    "transformed data": TokenType.TRANSFORMEDDATABLOCK,
    "parameters": TokenType.PARAMETERSBLOCK,
    "transformed parameters": TokenType.TRANSFORMEDPARAMETERSBLOCK,
    "model": TokenType.MODELBLOCK,
    "generated quantities": TokenType.GENERATEDQUANTITIESBLOCK,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "profile": TokenType.PROFILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "void": TokenType.VOID,
    "int": TokenType.INT,
    "real": TokenType.REAL,
    "complex": TokenType.COMPLEX,
    "vector": TokenType.VECTOR,
    "row_vector": TokenType.ROWVECTOR,
    "array": TokenType.ARRAY,
    "matrix": TokenType.MATRIX,
    "ordered": TokenType.ORDERED,
    "positive_ordered": TokenType.POSITIVEORDERED,
    "simplex": TokenType.SIMPLEX,
    "unit_vector": TokenType.UNITVECTOR,
    "cholesky_factor_corr": TokenType.CHOLESKYFACTORCORR,
    "cholesky_factor_cov": TokenType.CHOLESKYFACTORCOV,
    "corr_matrix": TokenType.CORRMATRIX,
    "cov_matrix": TokenType.COVMATRIX,
    "lower": TokenType.LOWER,
    "upper": TokenType.UPPER,
    "offset": TokenType.OFFSET,
    "multiplier": TokenType.MULTIPLIER,
    "increment_log_prob": TokenType.INCREMENTLOGPROB,
    "print": TokenType.PRINT,
    "reject": TokenType.REJECT,
}


class Scanner:
    """Scanner for Stan."""

    def __init__(self, source: str):
        self._source = source
        self._tokens: List[Token] = []

        self._start = 0
        self._current = 0
        self._line = 1
        self._column = 1

    def scan_tokens(self) -> List[Token]:
        # TODO list comprehension
        while not self._is_at_end():
            self._column += self._current - self._start
            self._start = self._current
            self._scan_single_token()

        self._column += self._current - self._start
        self._tokens.append(
            Token(ttype=TokenType.EOF, line=self._line, column=self._column))

        return self._tokens

    def _scan_single_token(self) -> None:
        char = self._pop_char()

        if char == "\n":
            self._increase_line()
            return
        elif char in [" ", "\t"]:
            return
        elif char == "\"":
            self._scan_string()
        elif char == "{":
            self._add_token(TokenType.LBRACE)
        elif char == "}":
            self._add_token(TokenType.RBRACE)
        elif char == "(":
            self._add_token(TokenType.LPAREN)
        elif char == ")":
            self._add_token(TokenType.RPAREN)
        elif char == "[":
            self._add_token(TokenType.LBRACK)
        elif char == "]":
            self._add_token(TokenType.RBRACK)
        elif char == "<":
            if self._match("="):
                self._add_token(TokenType.LEQ)
            elif self._match("-"):
                self._add_token(TokenType.ARROWASSIGN)
            else:
                self._add_token(TokenType.LABRACK)
        elif char == ">":
            if self._match("="):
                self._add_token(TokenType.GEQ)
            else:
                self._add_token(TokenType.RABRACK)
        elif char == ",":
            self._add_token(TokenType.COMMA)
        elif char == ";":
            self._add_token(TokenType.SEMICOLON)
        elif char == "|":
            if self._match("|"):
                self._add_token(TokenType.OR)
            else:
                self._add_token(TokenType.BAR)
        elif char == "?":
            self._add_token(TokenType.QMARK)
        elif char == ":":
            self._add_token(TokenType.COLON)
        elif char == "-":
            if self._match("="):
                self._add_token(TokenType.MINUSASSIGN)
            else:
                self._add_token(TokenType.MINUS)
        elif char == "+":
            if self._match("="):
                self._add_token(TokenType.PLUSASSIGN)
            else:
                self._add_token(TokenType.PLUS)
        elif char == "^":
            self._add_token(TokenType.HAT)
        elif char == "'":
            self._add_token(TokenType.TRANSPOSE)
        elif char == "*":
            if self._match("="):
                self._add_token(TokenType.TIMESASSIGN)
            else:
                self._add_token(TokenType.TIMES)
        elif char == "/":
            if self._match("/"):
                self._scan_one_line_comment()
            elif self._match("="):
                self._add_token(TokenType.DIVIDEASSIGN)
            else:
                self._add_token(TokenType.DIVIDE)
        elif char == "%":
            if self._match("/%"):
                self._add_token(TokenType.IDIVIDE)
            else:
                self._add_token(TokenType.MODULO)
        elif char == "\\":
            self._add_token(TokenType.LDIVIDE)
        elif char == ".":
            if self._match("*="):
                self._add_token(TokenType.ELTTIMESASSIGN)
            elif self._match("/="):
                self._add_token(TokenType.ELTDIVIDEASSIGN)
            elif self._match("*"):
                self._add_token(TokenType.ELTTIMES)
            elif self._match("^"):
                self._add_token(TokenType.ELTPOW)
            elif self._match("/"):
                self._add_token(TokenType.ELTDIVIDE)
            else:
                raise ValueError(f"Unknown character '{char}'.")
        elif char == "&":
            if self._match("&"):
                self._add_token(TokenType.AND)
            else:
                raise ValueError(f"Unknown character '{char}'.")
        elif char == "!":
            if self._match("="):
                self._add_token(TokenType.NEQUALS)
            else:
                self._add_token(TokenType.BANG)
        elif char == "~":
            self._add_token(TokenType.TILDE)
        elif char == "=":
            if self._match("="):
                self._add_token(TokenType.EQUALS)
            else:
                self._add_token(TokenType.ASSIGN)
        else:
            if char.isdigit():
                self._scan_number()
            elif is_identifier_char(char, is_first_char=True):
                self._scan_identifier()
            else:
                raise ValueError(f"Unknown character '{char}'.")

    def _scan_identifier(self) -> None:
        self._scan_while_char()

        text = self._get_start_to_current()

        # Special case: reserved keywords containing white spaces
        if text in {kw.split(" ")[0] for kw in STAN_KEYWORDS if " " in kw}:
            self._pop_char()  # advance single whitespace
            self._scan_while_char()
            text = self._get_start_to_current()

        token_type = TokenType.IDENTIFIER
        if text in STAN_KEYWORDS:
            token_type = STAN_KEYWORDS[text]

        self._add_token(token_type)

    def _scan_while_char(self):
        while is_identifier_char(self._peek(), is_first_char=False):
            self._pop_char()

    def _scan_one_line_comment(self) -> None:
        """ Scan until EOF or newline is encountered."""
        while not self._is_at_end() and self._peek() != "\n":
            self._pop_char()

    def _get_start_to_current(self):
        return self._get_to_current(self._start)

    def _get_to_current(self, position: int) -> str:
        return self._source[position:self._current]

    def _scan_string(self) -> None:
        while (is_valid_string_literal_char(self._peek())
               and not self._is_at_end()):
            self._pop_char()

        if self._is_at_end():
            error.throw_at(self._line, self._column,
                           "Unterminated string in file.")

        closing = self._pop_char()

        if closing != "\"":
            error.throw_at(self._line, self._column,
                           "Unterminated string in line.")

        literal = self._source[self._start + 1:self._current - 1]
        self._add_token(TokenType.STRING, literal)

    def _scan_number(self) -> None:
        while self._peek().isdigit():
            self._pop_char()

        literal = self._get_start_to_current()
        self._add_token(TokenType.INTNUMERAL, int(literal))

    def _add_token(self, ttype: TokenType, literal: Any = None) -> None:
        lexeme = self._source[self._start:self._current]

        self._tokens.append(
            Token(ttype=ttype,
                  lexeme=lexeme,
                  literal=literal,
                  line=self._line,
                  column=self._column))

    def _is_at_end(self, offset: int = 0) -> bool:
        return self._current + offset >= len(self._source)

    def _pop_char(self) -> str:
        """Advance by a single character."""
        char = self._source[self._current]
        self._current += 1
        return char

    def _peek(self, offset=0) -> str:
        """Peek at `offset` characters ahead (n=0 means current token)."""
        if self._current + offset >= len(self._source):
            return "\0"

        return self._source[self._current + offset]

    def _match(self, expected: str) -> bool:
        for i, char in enumerate(expected):
            if self._is_at_end(offset=i):
                return False

            if self._source[self._current + i] != char:
                return False
        self._current += len(expected)
        return True

    def _increase_line(self):
        self._line += 1
        self._column = 0


def is_valid_string_literal_char(char: str) -> bool:
    """Return if a char is valid to be used in a string literal."""
    return char not in ["\"", "\n", "\r"]


def is_identifier_char(char: str, is_first_char: bool) -> bool:
    """Returns if character is a valid char for an identifier.

    Args:
        char: character (string of length 1)
        is_first_char: whether `char` is supposed to be the first character of
            the identifier.

    Returns:
        bool: True if `char` is valid, False otherwise.
    """
    if is_first_char and (char.isdigit() or char == "_"):
        return False
    return char.isalpha() or char.isdigit() or char == "_"
